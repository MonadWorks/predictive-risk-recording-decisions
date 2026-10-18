"""Execute frozen protocols; no analysis or adaptive sample-size selection."""
import argparse,csv,hashlib,json,os,platform,time,shutil
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import scipy
from threadpoolctl import threadpool_limits,threadpool_info
from models import public_case,generate_truth,seeded,source_receipt
from design import build_bank,recording_designs
from inference import fit_selected


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(cfg_path,out):
    cfg=json.loads(cfg_path.read_text());out.mkdir(parents=True,exist_ok=True)
    if (out/'status.json').exists():raise RuntimeError('use a fresh output directory; frozen results are not overwritten')
    frozen=cfg_path.read_bytes();(out/'protocol.json').write_bytes(frozen)
    (out/'protocol.sha256').write_text(hashlib.sha256(frozen).hexdigest()+'\n')
    computational_files=['models.py','design.py','inference.py','run.py']
    sources={name:digest(Path(__file__).parent/name) for name in computational_files}
    (out/'source_hashes.json').write_text(json.dumps(sources,indent=2))
    (out/'source_snapshot').mkdir(exist_ok=True)
    for name in computational_files:shutil.copy2(Path(__file__).parent/name,out/'source_snapshot'/name)
    (out/'execution_freeze.json').write_text(json.dumps(dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
        protocol_sha256=hashlib.sha256(frozen).hexdigest(),source_hashes=sources,
        registration='local execution-time freeze, not public preregistration'),indent=2))
    env=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
             platform=platform.platform(),threadpool_info=threadpool_info(),threads_limit=cfg['threads'])
    try:
        import numba
        env['numba']=numba.__version__
    except ImportError:env['numba']=None
    (out/'environment.json').write_text(json.dumps(env,indent=2))
    rows=[];design_rows=[];receipts=[];fit_count=0;reuse_count=0;start=time.perf_counter()
    # Compile kernel before experiment timing; record warm-up separately.
    first=public_case(cfg['network_ids'][0],cfg,cfg['conditions'][0])
    first['model'].simulate(first['mu'],first['train'],True)
    warmup=time.perf_counter()-start;start=time.perf_counter()
    finished=[]
    with threadpool_limits(limits=cfg['threads']):
      for network_id in cfg['network_ids']:
        for condition in cfg['conditions']:
            tick=time.perf_counter();case=public_case(network_id,cfg,condition);m=case['model']
            bank=build_bank(case,cfg)
            receipt=source_receipt(case);receipt.update(network_id=network_id,condition=condition['name'],
                 prior_q_variance=bank['prior_q_variance'].tolist(),bank_seconds=bank['seconds'])
            receipts.append(receipt)
            all_designs=[]
            for pool in cfg['pools']:
              for budget in cfg['budgets']:
                designs=recording_designs(case,cfg,bank,pool,budget)
                for d in designs:
                    d.update(pool=pool,budget=budget)
                    saved={k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in d.items()}
                    saved.update(network_id=network_id,condition=condition['name'])
                    design_rows.append(saved)
                all_designs.extend(designs)
            for truth_id in range(cfg['truth_repeats']):
                theta=generate_truth(case,cfg,condition,truth_id)
                train,_=m.simulate(theta,case['train']);truth_test,_=m.simulate(theta,case['test'])
                trueQ,_=m.responses(theta,case['intervention'])
                if not np.isfinite(trueQ).all() or not np.isfinite(train).all():raise FloatingPointError('nonfinite teacher; retain protocol and investigate, no filtering')
                if m.kind==0:
                    gain=np.ones(m.N)
                    for p,ix in enumerate(m.active):
                        if ix<m.N:gain[ix]=np.exp(theta[p])
                    feedback=float(np.linalg.norm(m.J*gain[None,:],2))
                else:feedback=float('nan')
                for noise_id in range(cfg['noise_repeats']):
                    noise=seeded(cfg['noise_seed']+noise_id,network_id,truth_id).normal(size=train[:,::cfg['sample_stride']].shape)
                    observed=train[:,::cfg['sample_stride']]+cfg['noise_sd']*noise
                    cache={}
                    for d in all_designs:
                        key=tuple(sorted(d['nodes']))
                        if key not in cache:
                            cache[key]=fit_selected(case,cfg,key,observed[:,:,key]);fit_count+=1
                        else:reuse_count+=1
                        fit=cache[key]
                        activity_mse=float(np.mean((fit['test_activity']-truth_test)**2))
                        target_ids=range(len(case['readouts'])) if d['target']<0 else [d['target']]
                        for qid in target_ids:
                            qtrue=float(trueQ[case['readouts'][qid]]);qhat=float(fit['Q'][qid]);error=qhat-qtrue
                            variance=float(bank['prior_q_variance'][qid]);valid=variance>cfg['scale_floor']
                            rows.append(dict(network_id=network_id,condition=condition['name'],truth_id=truth_id,
                              noise_id=noise_id,target_id=qid,readout=int(case['readouts'][qid]),stim=case['stim'],
                              pool=d['pool'],budget=d['budget'],method=d['method'],design_repeat=d['replicate'],
                              nodes=';'.join(map(str,key)),q_true=qtrue,q_hat=qhat,error=error,squared_error=error**2,
                              abs_error=abs(error),prior_mc_variance=variance,scale_valid=valid,
                              normalized_squared_error=error**2/variance if valid else float('nan'),
                              risk_nominal=float(d['risk_nominal'][qid]),risk_ensemble=float(d['risk_ensemble'][qid]),
                              map_q_variance=float(fit['variance'][qid]),
                              covered_95=bool(abs(error)<=1.96*np.sqrt(fit['variance'][qid])),
                              passive_mse=activity_mse,optimizer_success=fit['success'],fallback=fit['fallback'],
                              nfev=fit['nfev'],fit_objective=fit['cost'],fit_seconds=fit['seconds'],
                              teacher_feedback_bound=feedback,fit_error=fit['error']))
            print(json.dumps(dict(network_id=network_id,condition=condition['name'],rows=len(rows),
                  actual_fits=fit_count,condition_seconds=round(time.perf_counter()-tick,2),
                  elapsed_seconds=round(time.perf_counter()-start,2))),flush=True)
        finished.append(network_id)
        # Whole-network checkpoints preserve the independent sampling unit.
        with (out/'results.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        (out/'designs.json').write_text(json.dumps(design_rows,indent=1))
        (out/'models.json').write_text(json.dumps(receipts,indent=1))
        status=dict(complete=len(finished)==len(cfg['network_ids']),networks_completed=finished,
             networks_planned=cfg['network_ids'],evaluated_rows=len(rows),actual_optimizer_calls=fit_count,
             cached_dataset_reuses=reuse_count,elapsed_seconds=time.perf_counter()-start,warmup_seconds=warmup,
             status='complete' if len(finished)==len(cfg['network_ids']) else 'running')
        (out/'status.json').write_text(json.dumps(status,indent=2))
        if time.perf_counter()-start>cfg['wall_limit_seconds']:
            if not status['complete']:
                status['status']='partial_time_limit';(out/'status.json').write_text(json.dumps(status,indent=2))
            break
    print(json.dumps(status,indent=2),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--protocol',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();execute(a.protocol,a.out)
