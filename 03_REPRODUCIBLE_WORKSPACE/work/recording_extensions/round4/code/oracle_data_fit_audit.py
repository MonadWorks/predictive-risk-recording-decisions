"""Common starts fitted to calibration data without oracle knowledge."""
from oracle_combinations import constrained_fit
from common4 import *
from analyze4 import read_stage,contrast
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse

def originals(nid):
    a=json.loads((HERE/'runs/oracle_combinations'/f'{nid}.json').read_text())
    b=json.loads((HERE/'runs/oracle_matched_control'/f'{nid}.json').read_text())
    return a['records']+b['records'],a['generating_objective']

def flagged(nid):
    rs,feasible=originals(nid)
    return any(not r['best']['success'] or r['best']['objective']>feasible+1e-6 for r in rs)

def worker(nid):
    path=HERE/'runs/oracle_data_fit_audit'/f'{nid}.json'
    if path.exists():return dict(network_id=nid,cached=True)
    old,feasible=originals(nid);tick=time.perf_counter();cfg,c,t,theta,y,eps,q=make_case(nid,'matched_rank2');m=c['model']
    nodes=paired_allocations(c)['neither'];ends=[c['stim'],*c['readouts']];eye=np.eye(m.P);E=eye[ends]
    A=np.einsum('ai,ib->abi',m.right,m.left).reshape(-1,m.P)*c['sd'][None,:]
    perm=seeded(95231,nid).permutation([i for i in range(m.N) if i not in ends and i not in nodes]).tolist()
    bases={'endpoints4':E,'recurrence4':A,'endpoints_recurrence8':np.row_stack([E,A]),'ordinary4':eye[perm[:4]],'ordinary8':eye[perm[:8]],'endpoint_ordinary8':eye[ends+perm[:4]]}
    base=json.loads((HERE/'runs/robustness'/f'{nid}_matched_rank2.json').read_text())
    ordinary=next(r for r in base['records'] if r['policy']=='neither')
    assert ordinary['nodes']==nodes
    common=[np.asarray(f['z']) for f in ordinary['fits']]+list(seeded(95413,nid).normal(size=(8,m.P)))
    p=Problem(c,cfg,nodes,y[:,:,nodes]+.05*eps[:,:,nodes],.05);truthz=(theta-c['mu'])/c['sd'];records=[]
    for r in old:
        extra=[constrained_fit(p,bases[r['policy']],truthz,z) for z in common]
        fits=r['fits']+extra;best=min(fits,key=lambda f:f['objective'])
        records.append(dict(policy=r['policy'],best=best,fits=fits,q_true=q.tolist(),mse=float(np.mean((np.asarray(best['q_hat'])-q)**2))))
    dump(path,dict(network_id=nid,complete=True,seconds=time.perf_counter()-tick,records=records,generating_objective=feasible,additional_common_starts=len(common)))
    return dict(network_id=nid,seconds=time.perf_counter()-tick)

def summary():
    selected=[];flags=[]
    for nid in range(50000,50040):
        old,feasible=originals(nid)
        if flagged(nid):
            flags.append(nid);d=json.loads((HERE/'runs/oracle_data_fit_audit'/f'{nid}.json').read_text());assert d['complete'];old=d['records']
        selected.append(dict(network_id=nid,records=old,feasible=feasible))
    policies=[r['policy'] for r in selected[0]['records']]
    metrics={p:[next(r['mse'] for r in d['records'] if r['policy']==p) for d in selected] for p in policies}
    pairs=[('endpoints_recurrence8','ordinary8'),('endpoints_recurrence8','endpoints4'),('endpoints_recurrence8','endpoint_ordinary8'),('recurrence4','ordinary4'),('endpoints4','ordinary4')]
    out=dict(n=40,scope='Retrospective common-data-start fitting audit; no cross-policy oracle estimates used',audited_networks=flags,metrics=metrics,
        comparisons={a+'_vs_'+b:contrast(metrics[a],metrics[b]) for a,b in pairs},
        failed_selected=sum(not r['best']['success'] for d in selected for r in d['records']),
        above_generating=sum(r['best']['objective']>d['feasible']+1e-6 for d in selected for r in d['records']))
    dump(HERE/'analysis/oracle_data_fit_audit_summary.json',out);print(json.dumps({k:v for k,v in out.items() if k!='metrics'},indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=2);ap.add_argument('--summary',action='store_true');a=ap.parse_args()
    if a.summary:summary()
    else:
        ids=[n for n in range(50000,50040) if flagged(n)]
        with ProcessPoolExecutor(a.workers) as ex:
            for f in as_completed([ex.submit(worker,n) for n in ids]):print(json.dumps(f.result()),flush=True)
        summary()
