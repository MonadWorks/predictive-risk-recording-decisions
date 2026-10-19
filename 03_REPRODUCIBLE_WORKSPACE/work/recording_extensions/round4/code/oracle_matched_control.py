"""Dimension-matched extra-information control after the planned oracle study."""
from oracle_combinations import constrained_fit
from common4 import *
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse

def worker(nid):
    path=HERE/'runs/oracle_matched_control'/f'{nid}.json'
    if path.exists():return dict(network_id=nid,cached=True)
    cfg,c,t,theta,y,eps,q=make_case(nid,'matched_rank2');m=c['model'];tick=time.perf_counter()
    nodes=paired_allocations(c)['neither'];ends=[c['stim'],*c['readouts']];eye=np.eye(m.P)
    perm=seeded(95231,nid).permutation([i for i in range(m.N) if i not in ends and i not in nodes]).tolist()
    rows=eye[ends+perm[:4]];truthz=(theta-c['mu'])/c['sd']
    p=Problem(c,cfg,nodes,y[:,:,nodes]+.05*eps[:,:,nodes],.05)
    fits=[constrained_fit(p,rows,truthz,s) for s in starts(nid)];best=min(fits,key=lambda f:f['objective'])
    r=dict(policy='endpoint_ordinary8',best=best,fits=fits,q_true=q.tolist(),mse=float(np.mean((np.asarray(best['q_hat'])-q)**2)))
    dump(path,dict(network_id=nid,complete=True,seconds=time.perf_counter()-tick,nodes=nodes,records=[r],generating_objective=float(p.evaluate(truthz)['cost'])))
    return dict(network_id=nid,seconds=time.perf_counter()-tick)

def summary():
    from analyze4 import read_stage,contrast
    controls=read_stage('oracle_matched_control',range(50000,50040));base=read_stage('oracle_combinations',range(50000,50040))
    a=[next(r['mse'] for r in d['records'] if r['policy']=='endpoints_recurrence8') for d in base]
    b=[d['records'][0]['mse'] for d in controls]
    out=dict(n=40,scope='Retrospective, dimension-matched follow-up; same network cohort',metrics=dict(endpoints_recurrence8=a,endpoint_ordinary8=b),comparison=contrast(a,b),
        failed_selected=sum(not d['records'][0]['best']['success'] for d in controls),above_generating=sum(d['records'][0]['best']['objective']>d['generating_objective']+1e-6 for d in controls))
    dump(HERE/'analysis/oracle_matched_control_summary.json',out);print(json.dumps(out['comparison'],indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=2);ap.add_argument('--summary',action='store_true');a=ap.parse_args()
    if a.summary:summary()
    else:
        with ProcessPoolExecutor(a.workers) as ex:
            for f in as_completed([ex.submit(worker,n) for n in range(50000,50040)]):print(json.dumps(f.result()),flush=True)
        summary()
