"""Bounded development-only numerical/ensemble diagnostics, not outcome tuning."""
import copy,json,time
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits
from models import public_case,generate_truth,seeded
from design import build_bank,recording_designs
from inference import fit_selected

ROOT=Path(__file__).parent
CORE=['local_scalar','ensemble_scalar','local_vector','ensemble_vector']

def relative(a,b):
    return float(np.linalg.norm(a-b)/max(np.linalg.norm(b),1e-15))

def at_resolution(base,condition,network_id,factor):
    cfg=dict(base,dt=base['dt']/factor,steps=base['steps']*factor,
             sample_stride=base['sample_stride']*factor)
    return cfg,public_case(network_id,cfg,condition)

def bank_prefix(bank,L):
    sliced=dict(bank)
    for k in ['info','goal','vector','gradients','particles']:
        sliced[k]=bank[k][:L+1]
    return sliced

def select_one_goal(case,cfg,bank,budget):
    """Fixed first goal plus common three-readout vector; all candidates retained."""
    cfg=dict(cfg,methods=CORE)
    designs=recording_designs(case,cfg,bank,'exclude_endpoints',budget)
    return [d for d in designs if d['target'] in [-1,0]]

def main():
    start=time.perf_counter()
    report=dict(scope='development numerical diagnostics only; no holdout read or outcome-based L selection',
       network_ids=[1880,1881],resolutions=[.05,.025,.0125],wall_budget_seconds=120,
       common_observation_times='0,.2,...,5.8',physical_duration=6.,
       integration='left-Riemann integral on [0,6), same analytic inputs and x0',
       ensemble_sizes=[8,16,32],numerical=[],ensemble=[],map_comparison=[])
    soft=json.loads((ROOT/'development.json').read_text())
    rank=json.loads((ROOT/'rank2_n100.json').read_text())
    cases=[]
    for network_id in [1880,1881]:
        for name in ['matched','broad']:
            cond=next(c for c in soft['conditions'] if c['name']==name)
            cases.append((soft,cond,network_id))
        cases.append((rank,rank['conditions'][0],network_id))
    with threadpool_limits(limits=2):
      for base,condition,network_id in cases:
        outputs=[]
        for factor in [1,2,4]:
            cfg,case=at_resolution(base,condition,network_id,factor)
            theta=generate_truth(case,cfg,condition,0)
            r,d=case['model'].simulate(theta,case['train'],True)
            q,g=case['model'].responses(theta,case['intervention'],True)
            outputs.append(dict(q=q,g=g,r=r[:,::cfg['sample_stride']],d=d[:,::cfg['sample_stride']]))
        ref=outputs[-1]
        entry=dict(family=base['family'],condition=condition['name'],network_id=network_id,
          q_reference=ref['q'].tolist(),reference_q_norm=float(np.linalg.norm(ref['q'])),
          reference_sensitivity_norm=float(np.linalg.norm(ref['g'])),comparisons=[])
        for factor,o in zip([1,2,4],outputs):
            entry['comparisons'].append(dict(dt=.05/factor,q_relative_error=relative(o['q'],ref['q']),
              q_max_abs_error=float(np.max(np.abs(o['q']-ref['q']))),
              sensitivity_relative_error=relative(o['g'],ref['g']),
              calibration_rate_relative_error=relative(o['r'],ref['r']),
              calibration_sensitivity_relative_error=relative(o['d'],ref['d'])))
        report['numerical'].append(entry)
        print('numerical',base['family'],condition['name'],network_id,round(time.perf_counter()-start,2),flush=True)
      # Fixed two diagnostic cases. Fine measurement and truth are identical for every method/resolution.
      for base,condition,budget in [(soft,next(c for c in soft['conditions'] if c['name']=='broad'),3),
                                    (rank,rank['conditions'][0],5)]:
        if time.perf_counter()-start>110:
            report['partial_reason']='predeclared runtime guard before next whole family diagnostic';break
        cfg,case=at_resolution(base,condition,1880,1)
        diagcfg=dict(cfg,ensemble_size=32,scale_samples=16,methods=CORE,max_nfev=40)
        bank=build_bank(case,diagcfg)
        designs={}
        for L in [8,16,32]:
            designs[L]=select_one_goal(case,diagcfg,bank_prefix(bank,L),budget)
        for method in CORE:
            dd={L:next(d for d in designs[L] if d['method']==method) for L in [8,16,32]}
            entry=dict(family=base['family'],network_id=1880,condition=condition['name'],method=method,
                       budget=budget,selected={str(L):dd[L]['nodes'] for L in dd},comparisons=[])
            for a,b in [(8,16),(16,32),(8,32)]:
                sa,sb=set(dd[a]['nodes']),set(dd[b]['nodes'])
                entry['comparisons'].append(dict(L_a=a,L_b=b,jaccard=len(sa&sb)/len(sa|sb)))
            # Risk of each selected set evaluated on the common, fixed 32-particle bank.
            from design import risks_for_set
            entry['common_L32_risks']={str(L):dict(zip(['nominal_by_target','ensemble_by_target'],
                  [a.tolist() for a in risks_for_set(bank,dd[L]['nodes'])])) for L in dd}
            report['ensemble'].append(entry)
        finecfg,fine=at_resolution(base,condition,1880,4)
        theta=generate_truth(fine,finecfg,condition,0)
        rr,_=fine['model'].simulate(theta,fine['train'])
        observed=rr[:,::finecfg['sample_stride']]
        observed=observed+cfg['noise_sd']*seeded(991,1880,0).normal(size=observed.shape)
        truthq,_=fine['model'].responses(theta,fine['intervention'])
        for d in designs[16]:
            for factor in [1,4]:
                cc,ca=at_resolution(base,condition,1880,factor)
                cc=dict(cc,max_nfev=40)
                nodes=tuple(sorted(d['nodes']))
                fit=fit_selected(ca,cc,nodes,observed[:,:,nodes])
                error=fit['Q']-truthq[case['readouts']]
                report['map_comparison'].append(dict(family=base['family'],network_id=1880,
                    method=d['method'],target=d['target'],dt=cc['dt'],nodes=list(nodes),
                    q_error_by_target=error.tolist(),mean_squared_q_error=float(np.mean(error**2)),
                    optimizer_success=fit['success'],nfev=fit['nfev'],fallback=fit['fallback'],
                    note='fit and response rollout at stated dt; same finest-grid calibration observations',
                    max_nfev=40))
            print('map',base['family'],d['method'],round(time.perf_counter()-start,2),flush=True)
        (ROOT/'diagnostics_results.json').write_text(json.dumps(report,indent=2)+'\n')
    report['elapsed_seconds']=time.perf_counter()-start
    report['complete']=len(report['numerical'])==6 and len(report['ensemble'])==8 and len(report['map_comparison'])==16
    report['interpretation']='numerical convergence and finite-prior-set sensitivity checks; not ranking validation or biological evidence'
    (ROOT/'diagnostics_results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(complete=report['complete'],elapsed_seconds=report['elapsed_seconds'])),flush=True)

if __name__=='__main__':main()
