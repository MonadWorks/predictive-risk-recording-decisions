"""Independent information interventions for endpoint and recurrent combinations."""
from common4 import *
from scipy.optimize import least_squares
from concurrent.futures import ProcessPoolExecutor,as_completed
from mechanism4 import coefficients,hybrids,combination_controls
import argparse

def constrained_fit(p,rows,truthz,start):
    _,s,v=np.linalg.svd(rows,full_matrices=True);rank=int(np.sum(s>s[0]*1e-10))
    known=v[:rank];free=v[rank:];fixed=np.einsum('pi,p->i',known,np.einsum('pi,i->p',known,truthz))
    def full(x):return fixed+np.einsum('pi,p->i',free,x)
    def jac(x):return np.einsum('ki,pi->kp',p.evaluate(full(x))['jac'],free)
    tick=time.perf_counter();f=least_squares(lambda x:p.evaluate(full(x))['res'],np.einsum('pi,i->p',free,start),
        jac=jac,max_nfev=400,xtol=1e-8,ftol=1e-8,gtol=1e-8)
    z=full(f.x);e=p.evaluate(z);q=p.response(z)['q']
    err=float(np.max(abs(np.einsum('pi,i->p',known,z-truthz))));assert err<1e-10
    return dict(z=z.tolist(),q_hat=q.tolist(),objective=float(f.cost),success=bool(f.success),
                nfev=int(f.nfev),optimality=float(f.optimality),constraint_rank=rank,constraint_error=err,seconds=time.perf_counter()-tick)

def worker(nid):
    path=HERE/'runs/oracle_combinations'/f'{nid}.json'
    if path.exists():return dict(network_id=nid,cached=True)
    cfg,c,t,theta,y,eps,q=make_case(nid,'matched_rank2');m=c['model'];tick=time.perf_counter()
    nodes=paired_allocations(c)['neither'];ends=[c['stim'],*c['readouts']];eye=np.eye(m.P)
    E=eye[ends];A=np.einsum('ai,ib->abi',m.right,m.left).reshape(-1,m.P)*c['sd'][None,:]
    perm=seeded(95231,nid).permutation([i for i in range(m.N) if i not in ends and i not in nodes]).tolist()
    bases={'endpoints4':E,'recurrence4':A,'endpoints_recurrence8':np.row_stack([E,A]),'ordinary4':eye[perm[:4]],'ordinary8':eye[perm[:8]]}
    truthz=(theta-c['mu'])/c['sd'];p=Problem(c,cfg,nodes,y[:,:,nodes]+.05*eps[:,:,nodes],.05);records=[]
    for label,rows in bases.items():
        fits=[constrained_fit(p,rows,truthz,s) for s in starts(nid)]
        best=min(fits,key=lambda f:f['objective'])
        records.append(dict(policy=label,best=best,fits=fits,q_true=q.tolist(),mse=float(np.mean((np.asarray(best['q_hat'])-q)**2))))
    out=dict(network_id=nid,complete=True,seconds=time.perf_counter()-tick,nodes=nodes,records=records,
             generating_objective=float(p.evaluate(truthz)['cost']))
    dump(path,out);return dict(network_id=nid,seconds=out['seconds'])

def validation(nid):
    path=HERE/'runs/mechanism_validation'/f'{nid}.json'
    if path.exists():return dict(network_id=nid,cached=True)
    rawpath=HERE/'runs/robustness'/f'{nid}_matched_rank2.json'
    raw=json.loads(rawpath.read_text());cfg,c,t,th,y,eps,q=make_case(nid,'matched_rank2');truth=coefficients(c,(th-c['mu'])/c['sd'])
    records=[];err=0.
    for r in raw['records']:
        z=np.asarray(r['best']['z']);ref=coefficients(c,z);qs,phi=hybrids(c,ref,truth)
        err=max(err,float(np.max(abs(qs[0]-r['best']['q_hat']))),float(np.max(abs(qs[-1]-q))))
        records.append(dict(policy=r['policy'],hybrid_q=qs.tolist(),component_changes=phi.tolist(),
                            combinations=combination_controls(c,z,nid)))
    assert err<1e-9
    dump(path,dict(network_id=nid,complete=True,max_identity_error=err,records=records))
    return dict(network_id=nid,identity_error=err)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=50000);ap.add_argument('--count',type=int,default=40)
    ap.add_argument('--workers',type=int,default=2);ap.add_argument('--validate',action='store_true');a=ap.parse_args()
    func=validation if a.validate else worker
    with ProcessPoolExecutor(a.workers) as ex:
        for f in as_completed([ex.submit(func,n) for n in range(a.start,a.start+a.count)]):print(json.dumps(f.result()),flush=True)
