"""Mechanism-only information intervention: reveal gains, then refit nuisance gains.

True gains are used exclusively in these explicitly labelled oracle diagnostics.
They never enter any deployable design or the method-validation cohort.
"""
from common import *
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse

def fixed_fit(p,start,known,truthz):
    free=np.array([i for i in range(p.m.P) if i not in known]);base=start.copy();base[known]=truthz[known]
    def full(x):
        z=base.copy();z[free]=x;return z
    tick=time.perf_counter()
    f=least_squares(lambda x:p.evaluate(full(x))['res'],base[free],
        jac=lambda x:p.evaluate(full(x))['jac'][:,free],max_nfev=300,xtol=1e-8,ftol=1e-8,gtol=1e-8)
    z=full(f.x);e=p.evaluate(z);q=p.response(z)['q']
    assert np.array_equal(z[known],truthz[known])
    return dict(z=z.tolist(),q_hat=q.tolist(),objective=float(f.cost),success=bool(f.success),
                nfev=int(f.nfev),seconds=time.perf_counter()-tick)

def worker(nid):
    dest=HERE/'runs/oracle_refit'/f'{nid}.json'
    if dest.exists():return dict(network_id=nid,cached=True)
    tick=time.perf_counter();cfg,case=case_for(nid);theta,y,eps,trueq=data_for(case,cfg)
    nodes,ends=allocated_nodes(case,'neither');obs=y[:,:,nodes]+.05*eps[:,:,nodes]
    p=Problem(case,cfg,nodes,obs,.05);truthz=(theta-case['mu'])/case['sd'];starts=starts_for(case)
    control_pool=[i for i in range(p.m.P) if i not in ends and i not in nodes]
    random_known=seeded(93931,nid).choice(control_pool,4,replace=False).tolist()
    records=[]
    for policy,known in [('known_stim',[case['stim']]),('known_readouts',case['readouts'].tolist()),('known_both',ends),('known_random4',random_known)]:
        known=list(map(int,known));fits=[fixed_fit(p,s,known,truthz) for s in starts]
        best=min(fits,key=lambda f:f['objective'])
        records.append(dict(policy=policy,known=known,best=best,fits=fits,q_true=trueq.tolist(),
                            mse=float(np.mean((np.array(best['q_hat'])-trueq)**2))))
    out=dict(network_id=nid,complete=True,scope='oracle mechanism diagnostic only',nodes=nodes,records=records,seconds=time.perf_counter()-tick)
    dump(dest,out);return dict(network_id=nid,seconds=out['seconds'])

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=2);a=ap.parse_args()
    with ProcessPoolExecutor(a.workers) as ex:
        jobs=[ex.submit(worker,n) for n in range(40000,40040)]
        for f in as_completed(jobs):print(json.dumps(f.result()),flush=True)
