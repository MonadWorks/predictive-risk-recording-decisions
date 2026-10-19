"""Fixed-budget allocation under structure and model perturbations."""
from common4 import *
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse

def worker(nid,condition,stage):
    path=HERE/'runs'/stage/f'{nid}_{condition}.json'
    if path.exists():return dict(network_id=nid,condition=condition,cached=True)
    tick=time.perf_counter();cfg,c,t,theta,y,eps,q=make_case(nid,condition)
    records=[];start_list=starts(nid,c['model'].P)
    for policy,nodes in paired_allocations(c).items():
        p,r=fit_record(c,cfg,nodes,y,eps,np.full(c['model'].N,.05),q,start_list)
        r['policy']=policy;r['generating_latent_objective']=float(p.evaluate((theta-c['mu'])/c['sd'])['cost'])
        records.append(r)
    out=dict(network_id=nid,condition=condition,complete=True,seconds=time.perf_counter()-tick,
             readouts=c['readouts'].tolist(),stim=int(c['stim']),model=model_receipt(c,t),records=records)
    dump(path,out)
    return {k:out[k] for k in ['network_id','condition','seconds']}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,required=True);ap.add_argument('--count',type=int,required=True)
    ap.add_argument('--workers',type=int,default=4);ap.add_argument('--stage',required=True);a=ap.parse_args()
    with ProcessPoolExecutor(a.workers) as ex:
        jobs=[ex.submit(worker,n,c,a.stage) for n in range(a.start,a.start+a.count) for c in CONDITIONS]
        for f in as_completed(jobs):print(json.dumps(f.result()),flush=True)
