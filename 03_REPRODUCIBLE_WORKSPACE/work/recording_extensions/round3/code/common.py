"""Round-three research, preserving all prior source and outcomes."""
import os,sys,json,time,hashlib
from pathlib import Path
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[key]='1'
HERE=Path(__file__).resolve().parent.parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'code'))
import numpy as np
from scipy.optimize import least_squares, minimize
from models import seeded,generate_truth
from rank2_refined import refined_case

def case_for(nid):
    cfg=json.loads((ROOT/'protocols/confirmation.json').read_text())
    cfg['max_nfev']=300
    case=refined_case(nid,cfg,cfg['conditions'][0],2)
    return cfg,case

def data_for(case,cfg,tid=0,noiseid=0):
    theta=generate_truth(case,cfg,cfg['conditions'][0],tid)
    r,_=case['model'].simulate(theta,case['train'])
    clean=r[:,::cfg['sample_stride']]
    eps=seeded(cfg['noise_seed']+noiseid,case['network_id'],tid).normal(size=clean.shape)
    q,_=case['model'].responses(theta,case['intervention'])
    return theta,clean,eps,q[case['readouts']]

def starts_for(case):
    rng=seeded(93631,case['network_id']);p=case['model'].P
    return [np.zeros(p),*.25*rng.normal(size=(2,p)),*rng.normal(size=(2,p))]

class Problem:
    """Whitened MAP parameters; no truth used in estimation or profiles."""
    def __init__(self,case,cfg,nodes,observed,sigma):
        self.case=case;self.cfg=cfg;self.m=case['model'];self.nodes=np.asarray(nodes,dtype=int)
        self.y=observed;self.sigma=np.broadcast_to(np.asarray(sigma),observed.shape)
        self.cache={};self.qcache={}
    def evaluate(self,z):
        key=z.tobytes()
        if self.cache.get('key')!=key:
            theta=self.case['mu']+self.case['sd']*z
            r,d=self.m.simulate(theta,self.case['train'],True,self.nodes)
            r=r[:,::self.cfg['sample_stride']];d=d[:,::self.cfg['sample_stride']]
            e=((r-self.y)/self.sigma).ravel()
            j=(d*self.case['sd'][None,None,None,:]/self.sigma[:,:,:,None]).reshape(-1,self.m.P)
            res=np.r_[e,z];jac=np.vstack([j,np.eye(self.m.P)])
            self.cache=dict(key=key,res=res,jac=jac,cost=.5*float(np.dot(res,res)),grad=np.einsum('ki,k->i',jac,res),
                            data_cost=.5*float(np.dot(e,e)),prior_cost=.5*float(np.dot(z,z)))
        return self.cache
    def response(self,z):
        key=z.tobytes()
        if self.qcache.get('key')!=key:
            theta=self.case['mu']+self.case['sd']*z
            q,g=self.m.responses(theta,self.case['intervention'],True)
            ids=self.case['readouts']
            self.qcache=dict(key=key,q=q[ids],g=g[ids]*self.case['sd'][None,:])
        return self.qcache
    def fit(self,start,max_nfev=None):
        tick=time.perf_counter()
        f=least_squares(lambda z:self.evaluate(z)['res'],start,jac=lambda z:self.evaluate(z)['jac'],
                        max_nfev=max_nfev or self.cfg['max_nfev'],xtol=1e-8,ftol=1e-8,gtol=1e-8)
        e=self.evaluate(f.x);q=self.response(f.x)['q']
        return dict(z=f.x.tolist(),q_hat=q.tolist(),objective=float(f.cost),data_cost=e['data_cost'],
                    prior_cost=e['prior_cost'],success=bool(f.success),nfev=int(f.nfev),
                    optimality=float(f.optimality),seconds=time.perf_counter()-tick)
    def multistart(self,starts):
        fits=[self.fit(s) for s in starts]
        return min(fits,key=lambda x:x['objective']),fits

def allocated_nodes(case,policy):
    ends=[int(case['stim']),*map(int,case['readouts'])]
    pool=[i for i in range(case['model'].N) if i not in ends]
    perm=seeded(1601,case['network_id']).permutation(pool).tolist()
    nodes=sorted(perm[:5] if policy=='neither' else [*ends,perm[0]])
    return nodes,ends

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')

def bootstrap_change(a,b,reps=10000):
    a=np.asarray(a);b=np.asarray(b);rng=np.random.default_rng(20261019)
    ids=rng.integers(0,len(a),(reps,len(a)))
    change=100*(a.mean()/b.mean()-1)
    vals=100*(a[ids].mean(1)/b[ids].mean(1)-1)
    loo=[100*(np.delete(a,i).mean()/np.delete(b,i).mean()-1) for i in range(len(a))]
    return dict(change_pct=float(change),ci95=np.percentile(vals,[2.5,97.5]).tolist(),
                wins=int(np.sum(a<b)),n=len(a),mean_a=float(a.mean()),mean_b=float(b.mean()),
                loo_pct=[min(loo),max(loo)])
