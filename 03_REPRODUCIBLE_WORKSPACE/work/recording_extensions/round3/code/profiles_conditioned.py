"""Same constrained problem in invertible local Gauss-Newton coordinates.

The quadratic prior makes the original coordinate box redundant. Removing
that box under this invertible transformation does not change feasible sets.
"""
from common import *
import profiles_fast as base
from scipy.linalg import solve_triangular
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse

def extremes(p,best,delta=2.,maxiter=160):
    z=np.asarray(best['z']);cost=best['objective'];e=p.evaluate(z)
    H=np.einsum('ki,kj->ij',e['jac'],e['jac'])
    B=solve_triangular(np.linalg.cholesky(H).T,np.eye(len(z)),lower=False)
    q=p.response(z)['q'].copy();G=p.response(z)['g'].copy();GB=np.einsum('ki,ij->kj',G,B)
    def full(v):return z+np.einsum('ij,j->i',B,v)
    allout=[]
    for k in range(3):
        variance=max(float(np.dot(GB[k],GB[k])),1e-16);scale=np.sqrt(variance)
        d=GB[k]*np.sqrt(2*delta/variance)
        for sign in [-1,1]:
            candidates=[dict(z=z.tolist(),q=float(q[k]),cost=cost,success=True,source='map')];attempts=[]
            for sid,x0 in enumerate([np.zeros(len(z)),.6*sign*d]):
                f=minimize(lambda v:-sign*p.q_value(full(v))[k]/scale,x0,
                    jac=lambda v:-sign*np.einsum('i,ij->j',p.response(full(v))['g'][k],B)/scale,
                    method='SLSQP',constraints=[dict(type='ineq',
                        fun=lambda v:(cost+delta-p.cost_value(full(v)))/delta,
                        jac=lambda v:-np.einsum('i,ij->j',p.evaluate(full(v))['grad'],B)/delta)],
                    options=dict(maxiter=maxiter,ftol=1e-8))
                actual=p.evaluate(full(f.x))['cost'];val=float(p.response(full(f.x))['q'][k]);feasible=actual<=cost+delta+1e-5
                rec=dict(z=full(f.x).tolist(),q=val,cost=float(actual),success=bool(f.success),
                         feasible=bool(feasible),nit=int(f.nit),message=str(f.message),start=sid,source='slsqp')
                attempts.append(rec)
                if feasible and np.isfinite(val):candidates.append(rec)
            chosen=max(candidates,key=lambda c:sign*c['q'])
            allout.append(dict(target=k,sign=sign,chosen=chosen,attempts=attempts))
    lo=np.array([r['chosen']['q'] for r in allout if r['sign']==-1]);hi=np.array([r['chosen']['q'] for r in allout if r['sign']==1])
    return dict(delta=delta,lower=lo.tolist(),upper=hi.tolist(),width=(hi-lo).tolist(),
                local_width=(2*np.sqrt(2*delta*np.sum(GB*GB,axis=1))).tolist(),searches=allout,
                coordinates='invertible local Gauss-Newton preconditioning')

def worker(nid,stage,policies):
    base.extremes=extremes
    return base.worker(nid,stage,policies)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True);ap.add_argument('--start',type=int,required=True)
    ap.add_argument('--count',type=int,required=True);ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--policies',default='neither,both,both_noise4,both_noise16');a=ap.parse_args()
    with ProcessPoolExecutor(a.workers) as ex:
        jobs=[ex.submit(worker,n,a.stage,a.policies.split(',')) for n in range(a.start,a.start+a.count)]
        for f in as_completed(jobs):print(json.dumps(f.result()),flush=True)
