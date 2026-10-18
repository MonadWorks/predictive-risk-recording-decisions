"""Post-experiment case diagnosis: alternative starts for the SAME MAP objective.

Cases are selected by influence in the completed mechanism experiment. These
case studies neither replace the frozen outcomes nor estimate a new policy's
population performance. Teacher starts are explicitly oracle diagnostics.
"""
import csv,json,os,time
from pathlib import Path
from datetime import datetime,timezone
from collections import defaultdict
import numpy as np
from scipy.optimize import least_squares
from threadpoolctl import threadpool_limits
from models import seeded,generate_truth
from rank2_refined import refined_case

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'analysis/fit_diagnosis'


def fit_from(case,cfg,nodes,observed,start,true_q):
    m=case['model'];mu=case['mu'];sd=case['sd'];cache={}
    nodes=np.asarray(sorted(nodes),dtype=np.int64)
    def evaluate(theta):
        key=theta.tobytes()
        if cache.get('key')!=key:
            r,d=m.simulate(theta,case['train'],True,nodes)
            pred=r[:,::cfg['sample_stride']];jac=d[:,::cfg['sample_stride']]
            data=((pred-observed)/cfg['noise_sd']).ravel()
            prior=(theta-mu)/sd
            cache.update(key=key,residual=np.r_[data,prior],
                jac=np.vstack([jac.reshape(-1,m.P)/cfg['noise_sd'],np.diag(1/sd)]),
                data_cost=float(.5*np.dot(data,data)),prior_cost=float(.5*np.dot(prior,prior)))
        return cache
    tick=time.perf_counter()
    fit=least_squares(lambda x:evaluate(x)['residual'],start,
                      jac=lambda x:evaluate(x)['jac'],max_nfev=cfg['max_nfev'],
                      xtol=1e-7,ftol=1e-7,gtol=1e-7)
    info=evaluate(fit.x);q,_=m.responses(fit.x,case['intervention'])
    target=q[case['readouts']]
    return dict(success=bool(fit.success),nfev=int(fit.nfev),objective=float(fit.cost),
        data_cost=info['data_cost'],prior_cost=info['prior_cost'],optimality=float(fit.optimality),
        response_mse=float(np.mean((target-true_q)**2)),q_hat=target.tolist(),theta=fit.x.tolist(),
        seconds=time.perf_counter()-tick)


def main():
    OUT.mkdir(exist_ok=True)
    cfg=json.loads((ROOT/'protocols/mechanism.json').read_text())
    allrows=[]
    for path in (ROOT/'runs').glob('mechanism_shard_*/results.csv'):
        with path.open() as f:allrows.extend(csv.DictReader(f))
    cases=[(20009,.9),(20014,.6),(20020,.6)]
    methods=['local_vector','ensemble_vector','ensemble_fixed_goal','ensemble_fixed_info']
    plan=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
              scope='post-experiment diagnosis of three influential network/uncertainty cases',
              cases=cases,budget=10,
              case_selection='largest absolute network effect at SD .9 M10, and two largest at SD .6 M10',
              trial_selection='truth/noise pair with largest absolute ensemble-minus-nominal response MSE',
              starts=['nominal','near_1','near_2','prior_1','prior_2','teacher_oracle'],
              estimation='same MAP objective and tolerances; prior center always zero, start changes only',
              seed=91021,max_nfev=cfg['max_nfev'],frozen_experiment_replaced=False)
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    records=[]
    for nid,sd in cases:
        condition=dict(name=f'gain_sd_{sd:.1f}',mode='gain',prior_sd=sd)
        subset=[r for r in allrows if int(r['network_id'])==nid and r['condition']==condition['name'] and int(r['budget'])==10]
        bytrial=defaultdict(list)
        for r in subset:bytrial[int(r['truth_id']),int(r['noise_id']),r['method']].append(r)
        trial=max([(t,n) for t in range(2) for n in range(2)],key=lambda x:abs(np.mean([float(r['squared_error']) for r in bytrial[*x,'ensemble_vector']])-np.mean([float(r['squared_error']) for r in bytrial[*x,'local_vector']])))
        truth_id,noise_id=trial
        case=refined_case(nid,cfg,condition,2);m=case['model']
        theta=generate_truth(case,cfg,condition,truth_id)
        train,_=m.simulate(theta,case['train']);q,_=m.responses(theta,case['intervention']);true_q=q[case['readouts']]
        noise=seeded(cfg['noise_seed']+noise_id,nid,truth_id).normal(size=train[:,::cfg['sample_stride']].shape)
        observed=train[:,::cfg['sample_stride']]+cfg['noise_sd']*noise
        rng=seeded(91021,nid,int(round(sd*10)))
        starts=[('nominal',case['mu'].copy())]
        starts += [(f'near_{i+1}',case['mu']+.25*case['sd']*rng.normal(size=m.P)) for i in range(2)]
        starts += [(f'prior_{i+1}',case['mu']+case['sd']*rng.normal(size=m.P)) for i in range(2)]
        starts += [('teacher_oracle',theta)]
        for method in methods:
            archived=sorted(bytrial[truth_id,noise_id,method],key=lambda r:int(r['target_id']))
            nodes=sorted(map(int,archived[0]['nodes'].split(';')))
            for name,start in starts:
                fit=fit_from(case,cfg,nodes,observed[:,:,nodes],start,true_q)
                if name=='nominal':
                    assert np.allclose(fit['q_hat'],[float(r['q_hat']) for r in archived],rtol=1e-7,atol=1e-9)
                    # Refine integration at the same fitted parameters; no refit.
                    fine=refined_case(nid,cfg,condition,8)
                    fine_q,_=fine['model'].responses(np.asarray(fit['theta']),case['intervention'])
                    fit['rk4_substeps8_max_target_difference']=float(np.max(np.abs(fine_q[case['readouts']]-fit['q_hat'])))
                row=dict(network_id=nid,prior_sd=sd,truth_id=truth_id,noise_id=noise_id,method=method,
                         start=name,nodes=nodes,q_true=true_q.tolist(),**fit)
                records.append(row)
                print(json.dumps({k:row[k] for k in ['network_id','prior_sd','method','start','objective','response_mse','success']}),flush=True)
                (OUT/'results.json').write_text(json.dumps(records,indent=2)+'\n')
    compact=[{k:v for k,v in r.items() if not isinstance(v,list)} for r in records]
    keys=list(dict.fromkeys(k for r in compact for k in r))
    with (OUT/'results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(compact)
    (OUT/'complete.json').write_text(json.dumps(dict(complete=True,fit_count=len(records)),indent=2)+'\n')


if __name__=='__main__':
    with threadpool_limits(limits=1):main()
