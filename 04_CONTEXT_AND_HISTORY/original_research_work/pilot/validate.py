"""Post-pilot numerical audit, not a new confirmatory experiment."""
from pathlib import Path
import csv, hashlib, itertools, json, time
import numpy as np
from threadpoolctl import threadpool_limits
import pilot as p

root=Path(__file__).parent
out=root/'main_v1'
cfg=json.loads((out/'protocol.json').read_text())
rows=list(csv.DictReader((out/'results.csv').open()))
start=time.perf_counter()
report={'status':'post-pilot numerical diagnostics; no tuned outcomes'}
assert hashlib.sha256((root/'pilot.py').read_bytes()).hexdigest()==(out/'source.sha256').read_text().strip()
assert len(rows)==336
assert all(np.isfinite(float(r[k])) for r in rows for k in ['q_true','q_hat','q_error','q_variance','passive_mse'])
report['rows_finite']=True
report['exact_zero_targets']=sum(float(r['q_true'])==0 for r in rows[::28])
report['prior_q_variance_below_floor_rows']=sum(float(r['prior_q_variance'])<1e-12 for r in rows)
half=[]; cross=[]; exact=[]
with threadpool_limits(limits=2):
 for seed in range(cfg['seed_start'],cfg['seed_start']+cfg['teachers']):
    c=p.make_case(seed,cfg)
    fine=dict(cfg,dt=cfg['dt']/2,steps=cfg['steps']*2,sample_stride=cfg['sample_stride']*2)
    cf=p.make_case(seed,fine)
    q1,_=p.response(c['truth'],c['J'],c['intervention'],c['readout'],cfg['dt'])
    q2,_=p.response(cf['truth'],cf['J'],cf['intervention'],cf['readout'],fine['dt'])
    half.append({'seed':seed,'q_dt':q1,'q_half_dt':q2,'absolute_change':abs(q1-q2),'relative_change':abs(q1-q2)/max(abs(q2),1e-12)})
 for pool in cfg['pools']:
  for budget in cfg['budgets']:
   for method in cfg['methods']:
    rr=[r for r in rows if r['pool']==pool and int(r['budget'])==budget and r['method']==method]
    cross.append({'pool':pool,'budget':budget,'method':method,
       'target_q_rmse':float(np.sqrt(np.mean([float(r['q_error'])**2 for r in rr]))),
       'alternate_task_rmse':float(np.sqrt(np.mean([float(r['other_q_error'])**2 for r in rr])))})
 # Exhaustive n=6,k=2 design check: numerical algorithm audit, not main results.
 small=dict(cfg,neurons=6,budgets=[2])
 for small_seed in range(21,26):
    c=p.make_case(small_seed,small);P=len(c['theta0'])
    _,D=p.simulate(c['theta0'],c['J'],c['train'],small['dt'],True)
    D=D[:,::small['sample_stride']]
    info=[np.einsum('ki,kj->ij',D[:,:,i].reshape(-1,P),D[:,:,i].reshape(-1,P))/small['noise_sd']**2 for i in range(6)]
    H0=np.diag(1/c['sd']**2)
    _,g=p.response(c['theta0'],c['J'],c['intervention'],c['readout'],small['dt'],True)
    subsets=list(itertools.combinations(range(6),2))
    risks=[float(g@np.linalg.solve(H0+info[a]+info[b],g)) for a,b in subsets]
    designs,_=p.prospective_design(c,small,2,list(range(6)))
    chosen=tuple(sorted(designs['goal']['nodes']))
    exact.append({'seed':small_seed,'neurons':6,'budget':2,'subsets':len(subsets),
      'target_gradient_norm':float(np.linalg.norm(g)),
      'exact_best_subset':subsets[int(np.argmin(risks))], 'greedy_subset':chosen,
      'greedy_risk':risks[subsets.index(chosen)],'exact_best_risk':min(risks)})
 report['enumeration']=exact
report['time_step_audit']=half
report['cross_task_errors']=cross
report['elapsed_seconds']=time.perf_counter()-start
(out/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'checks':{k:v for k,v in report.items() if k not in ['cross_task_errors','time_step_audit']},
 'dt_relative_max':max(r['relative_change'] for r in half)},indent=2))
