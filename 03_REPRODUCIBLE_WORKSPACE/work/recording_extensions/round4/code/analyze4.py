"""Network-paired summaries, retaining every planned network and condition."""
from common4 import *
import argparse

def read_stage(stage,nids,template='{nid}.json'):
    ds=[]
    for nid in nids:
        p=HERE/'runs'/stage/template.format(nid=nid)
        if not p.exists():raise RuntimeError(f'Incomplete planned cohort: {p.name}')
        d=json.loads(p.read_text());assert d['complete'];ds.append(d)
    return ds

def contrast(a,b):
    d=bootstrap_change(a,b);n=len(a);rng=np.random.default_rng(20261020);ids=rng.integers(0,n,(30000,n))
    vals=100*(np.asarray(a)[ids].mean(1)/np.asarray(b)[ids].mean(1)-1)
    d['ci_bonferroni_six']=np.percentile(vals,[100*.05/12,100*(1-.05/12)]).tolist()
    return d

def mechanism(stage,nids):
    data=read_stage(stage,nids);metrics={};gradient={};parts={}
    for policy in ['neither','both']:
        rows=[next(r for r in d['records'] if r['policy']==policy) for d in data]
        metrics[policy]={};gradient[policy]={};parts[policy]={}
        for name in ['endpoint','endpoint_recurrence','random8']:
            gradient[policy][name]=[r['combinations'][name]['gradient_fraction'] for r in rows]
            for rms in ['0.1','0.3']:
                metrics[policy][name+'_'+rms]=[r['combinations'][name]['perturbations'][rms]['mean_squared_change'] for r in rows]
        for k,label in enumerate(['input','recurrence','readout']):
            vals=[]
            for r in rows:
                if 'decomposition' in r:
                    vals.append(float(np.mean([np.asarray(x['component_changes'])[k,x['target']]**2 for x in r['decomposition']])))
                else:vals.append(float(np.mean(np.asarray(r['component_changes'])[k]**2)))
            parts[policy][label]=vals
    tests={}
    for policy in ['neither','both']:
        for rms in ['0.1','0.3']:
            for a,b in [('endpoint_recurrence','random8'),('endpoint_recurrence','endpoint')]:
                tests[f'{policy}/{rms}/{a}_vs_{b}']=contrast(metrics[policy][a+'_'+rms],metrics[policy][b+'_'+rms])
    part_comparisons={k:contrast(parts['both'][k],parts['neither'][k]) for k in parts['both']}
    out=dict(n=len(data),gradient_fractions=gradient,perturbation_metrics=metrics,perturbation_comparisons=tests,
             component_squares=parts,component_comparisons=part_comparisons,max_identity_error=max(d['max_identity_error'] for d in data))
    dump(HERE/'analysis'/f'{stage}_summary.json',out)
    print(stage,json.dumps(dict(gradient_medians={p:{k:float(np.median(v)) for k,v in d.items()} for p,d in gradient.items()},
        perturbation_effects={k:v['change_pct'] for k,v in tests.items()},component_changes={k:v['change_pct'] for k,v in part_comparisons.items()}),indent=2))

def robustness():
    out={}
    for condition in CONDITIONS:
        data=read_stage('robustness',range(50000,50040),'{nid}_'+condition+'.json')
        metrics={p:[next(r for r in d['records'] if r['policy']==p)['mse'] for d in data] for p in ['neither','both']}
        selected=[r for d in data for r in d['records']]
        out[condition]=dict(metrics=metrics,comparison=contrast(metrics['both'],metrics['neither']),
            fit_flags=dict(failed_selected=sum(not r['best']['success'] for r in selected),
                           above_generating=sum(r['best']['objective']>r['generating_latent_objective']+1e-6 for r in selected)))
    dump(HERE/'analysis/robustness_summary.json',out);print(json.dumps({k:v['comparison'] for k,v in out.items()},indent=2))

def allocation():
    data=read_stage('allocation',range(55000,55040));policies=[r['policy'] for r in data[0]['records'][:6]]
    metrics={p:[float(np.mean([r['mse'] for r in d['records'] if r['policy']==p])) for d in data] for p in policies}
    tests={f'endpoint_pair_vs_{p}':contrast(metrics['endpoint_pair'],metrics[p]) for p in policies if p!='endpoint_pair'}
    tests.update({f'endpoint_joint_vs_{p}':contrast(metrics['endpoint_joint'],metrics[p]) for p in ['ensemble_greedy','nominal_greedy','stimulus_first']})
    strata={}
    for budget in [2,3]:
        for precision in ['uniform','stimulus_noisy','readouts_noisy']:
            mm={p:[next(r['mse'] for r in d['records'] if r['policy']==p and r['budget']==budget and r['precision']==precision) for d in data] for p in policies}
            strata[f'{budget}_{precision}']=dict(metrics=mm,comparisons={f'endpoint_pair_vs_{p}':contrast(mm['endpoint_pair'],mm[p]) for p in policies if p!='endpoint_pair'})
    flags=[]
    for d in data:
        for r in d['records']:
            if not r['best']['success'] or r['best']['objective']>r['generating_latent_objective']+1e-6:
                flags.append(dict(network_id=d['network_id'],policy=r['policy'],budget=r['budget'],precision=r['precision']))
    agreement={p:sum(tuple(a['nodes'])==tuple(next(b['nodes'] for b in d['designs'] if b['policy']==p and b['budget']==a['budget'] and b['precision']==a['precision']))
                     for d in data for a in d['designs'] if a['policy']=='endpoint_pair') for p in policies if p!='endpoint_pair'}
    selection_diagnostics={}
    for key in strata:
        budget,precision=key.split('_',1);budget=int(budget);entries=[]
        for d in data:
            designs={r['policy']:r for r in d['designs'] if r['budget']==budget and r['precision']==precision}
            ends={d['stim'],*d['readouts']}
            entries.append(dict(network_id=d['network_id'],criterion_ratio=designs['endpoint_pair']['ensemble_risk']/designs['ensemble_greedy']['ensemble_risk'],
                pair_equals_greedy=designs['endpoint_pair']['nodes']==designs['ensemble_greedy']['nodes'],
                pair_equals_endpoint_joint=designs['endpoint_pair']['nodes']==designs['endpoint_joint']['nodes'],
                endpoint_counts={p:len(set(r['nodes'])&ends) for p,r in designs.items()}))
        selection_diagnostics[key]=entries
    out=dict(n=len(data),metrics=metrics,comparisons=tests,strata=strata,flagged_fits=flags,agreement_out_of_240=agreement,
             descriptive_selection_diagnostics=selection_diagnostics,
             mean_selection_seconds={p:float(np.mean([r['selection_seconds'] for d in data for r in d['designs'] if r['policy']==p])) for p in policies},
             mean_shared_bank_seconds=float(np.mean([d['bank_seconds'] for d in data])))
    dump(HERE/'analysis/allocation_summary.json',out);print(json.dumps(tests,indent=2))

def oracle():
    data=read_stage('oracle_combinations',range(50000,50040));policies=[r['policy'] for r in data[0]['records']]
    metrics={p:[next(r['mse'] for r in d['records'] if r['policy']==p) for d in data] for p in policies}
    comparisons={f'{a}_vs_{b}':contrast(metrics[a],metrics[b]) for a,b in [('endpoints_recurrence8','ordinary8'),('endpoints_recurrence8','endpoints4'),('recurrence4','ordinary4'),('endpoints4','ordinary4')]}
    out=dict(n=len(data),metrics=metrics,comparisons=comparisons,failed_selected=sum(not r['best']['success'] for d in data for r in d['records']),
        above_generating=sum(r['best']['objective']>d['generating_objective']+1e-6 for d in data for r in d['records']))
    dump(HERE/'analysis/oracle_combinations_summary.json',out);print(json.dumps(comparisons,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['mechanism','mechanism_validation','robustness','allocation','oracle']);a=ap.parse_args()
    if a.phase=='mechanism':mechanism('mechanism',range(40000,40040))
    elif a.phase=='mechanism_validation':mechanism('mechanism_validation',range(50000,50040))
    else:globals()[a.phase]()
