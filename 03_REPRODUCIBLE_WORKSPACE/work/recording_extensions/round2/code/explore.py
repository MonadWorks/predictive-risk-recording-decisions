"""Focused retrospective extension: endpoint allocation and shared MAP fitting.

Frozen round-one outcomes are never edited. All fitting starts and endpoint
policies use public information; truth is used only for evaluation/diagnosis.
"""
import argparse, csv, hashlib, json, os, sys, time
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ProcessPoolExecutor, as_completed

for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[key]='1'
HERE=Path(__file__).resolve().parent.parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'code'))
import numpy as np
from threadpoolctl import threadpool_limits
from models import seeded, generate_truth
from rank2_refined import refined_case
from diagnose_influential_fits import fit_from

def load_archive():
    rows=[]
    for p in sorted((ROOT/'runs').glob('confirmation_shard_*/results.csv')):
        with p.open() as f: rows.extend(csv.DictReader(f))
    return rows

def worker(nid,phase):
    cfg=json.loads((ROOT/'protocols/confirmation.json').read_text())
    cfg['max_nfev']=200
    cond=cfg['conditions'][0]
    case=refined_case(nid,cfg,cond,2);m=case['model']
    endpoints={case['stim'],*map(int,case['readouts'])}
    nonends=[i for i in range(m.N) if i not in endpoints]
    out=HERE/'runs'/phase/f'{nid}.jsonl'
    done=out.with_suffix('.done.json')
    if done.exists():return json.loads(done.read_text())
    if out.exists():raise RuntimeError(f'Partial output exists: {out}')
    designs=[]
    archived={}
    if phase=='endpoint':
        for rep in range(3):
            perm=seeded(1601+rep,nid).permutation(nonends).tolist()
            for label,fixed in [('neither',[]),('stim_only',[case['stim']]),('readouts_only',list(case['readouts'])),('both',[case['stim'],*case['readouts']])]:
                nodes=sorted(map(int,[*fixed,*perm[:5-len(fixed)]]))
                assert len(set(nodes))==5
                designs.append(dict(policy=label,replicate=rep,nodes=nodes,pool='controlled_allocation'))
        starts=[('nominal',case['mu'])]
    elif phase=='fit_primary':
        rows=[r for r in load_archive() if int(r['network_id'])==nid and r['pool']=='exclude_endpoints' and int(r['budget'])==5 and r['method'] in ['local_vector','ensemble_vector']]
        for method in ['local_vector','ensemble_vector']:
            rr=[r for r in rows if r['method']==method]
            nodes=sorted(map(int,rr[0]['nodes'].split(';')))
            designs.append(dict(policy=method,replicate=0,nodes=nodes,pool='exclude_endpoints'))
        for r in rows:
            archived[int(r['truth_id']),int(r['noise_id']),r['method'],int(r['target_id'])]=r
        rng=seeded(91631,nid)
        starts=[('nominal',case['mu'])]
        starts += [(f'near_{i+1}',case['mu']+.25*case['sd']*rng.normal(size=m.P)) for i in range(2)]
        starts += [(f'prior_{i+1}',case['mu']+case['sd']*rng.normal(size=m.P)) for i in range(2)]
    else:raise ValueError(phase)
    tick=time.perf_counter();count=0;reuses=0
    with threadpool_limits(limits=1),out.open('w') as stream:
        for tid in range(2):
            theta=generate_truth(case,cfg,cond,tid)
            train,_=m.simulate(theta,case['train']);q,_=m.responses(theta,case['intervention'])
            true_q=q[case['readouts']]
            for noiseid in range(2):
                noise=seeded(cfg['noise_seed']+noiseid,nid,tid).normal(size=train[:,::cfg['sample_stride']].shape)
                observed=train[:,::cfg['sample_stride']]+cfg['noise_sd']*noise
                cache={}
                for d in designs:
                    nodes=d['nodes']
                    teacher_cost=.5*float(np.sum(noise[:,:,nodes]**2)+np.sum(((theta-case['mu'])/case['sd'])**2))
                    for name,start in starts:
                        key=(tuple(nodes),name)
                        if key not in cache:
                            cache[key]=fit_from(case,cfg,nodes,observed[:,:,nodes],start,true_q);count+=1
                        else:reuses+=1
                        fit=cache[key]
                        assert np.isfinite(fit['objective']) and np.isfinite(fit['q_hat']).all()
                        if phase=='fit_primary' and name=='nominal':
                            old=[float(archived[tid,noiseid,d['policy'],k]['q_hat']) for k in range(3)]
                            assert np.allclose(old,fit['q_hat'],rtol=1e-7,atol=1e-9)
                        rec=dict(network_id=nid,truth_id=tid,noise_id=noiseid,budget=5,
                                 stim=case['stim'],readouts=case['readouts'].tolist(),
                                 q_true=true_q.tolist(),teacher_objective=teacher_cost,
                                 start=name,**d,**fit)
                        stream.write(json.dumps(rec)+'\n');stream.flush()
    report=dict(network_id=nid,phase=phase,complete=True,actual_fits=count,cached=reuses,seconds=time.perf_counter()-tick)
    done.write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['endpoint','fit_primary'],required=True)
    ap.add_argument('--workers',type=int,default=4);args=ap.parse_args()
    dest=HERE/'runs'/args.phase;dest.mkdir(parents=True,exist_ok=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        tasks=[pool.submit(worker,nid,args.phase) for nid in range(20000,20040)]
        for f in as_completed(tasks): print(json.dumps(f.result()),flush=True)

if __name__=='__main__':main()
