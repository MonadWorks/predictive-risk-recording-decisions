from common import *
from scipy.stats import spearmanr
import argparse

def load(stage,start,count):
    paths=[HERE/'runs'/stage/f'{n}.json' for n in range(start,start+count)]
    missing=[str(p) for p in paths if not p.exists()]
    if missing:raise RuntimeError(f'{stage}: {len(missing)} planned networks remain')
    return [json.loads(p.read_text()) for p in paths]

def profiles():
    raw=load('profile_audited',40000,40);policies=['neither','both','both_noise4','both_noise16']
    by={p:[next(r for r in x['records'] if r['policy']==p) for x in raw] for p in policies}
    metrics={p:dict(mse=[r['mse'] for r in by[p]],
        width2=[float(np.mean(np.square(r['profile']['width']))) for r in by[p]],
        local_width2=[float(np.mean(np.square(r['profile']['local_width']))) for r in by[p]]) for p in policies}
    comp={}
    for a,b in [('both','neither'),('both_noise4','both'),('both_noise16','both'),('both_noise16','neither')]:
        comp[a+'_vs_'+b]={k:bootstrap_change(metrics[a][k],metrics[b][k]) for k in ['mse','width2']}
    audit={}
    for p,rr in by.items():
        attempts=[a for r in rr for s in r['profile']['searches'] for a in s['attempts']]
        chosen=[s['chosen'] for r in rr for s in r['profile']['searches']]
        audit[p]=dict(attempts=len(attempts),success=sum(a['success'] for a in attempts),
            feasible=sum(a['feasible'] for a in attempts),chosen_success=sum(a['success'] for a in chosen),
            chosen_map=sum(a['source']=='map' for a in chosen),
            max_constraint_excess=max(a['cost']-r['best']['objective']-2 for r in rr for s in r['profile']['searches'] for a in [s['chosen']]),
            selected_fit_success=sum(r['best']['success'] for r in rr),
            certified_suboptimal_fits=sum(r['best']['objective']>r['teacher_objective']+.001 for r in rr),
            true_response_in_range=float(np.mean([(np.asarray(r['q_true'])>=r['profile']['lower'])&(np.asarray(r['q_true'])<=r['profile']['upper']) for r in rr])),
            range_vs_local_width2=bootstrap_change(metrics[p]['width2'],metrics[p]['local_width2']))
    rho=spearmanr(np.log(np.array(metrics['both']['width2'])/metrics['neither']['width2']),
                  np.log(np.array(metrics['both']['mse'])/metrics['neither']['mse']))
    out=dict(networks=40,policies=policies,metrics=metrics,comparisons=comp,audit=audit,
             exploratory_log_change_spearman=dict(rho=float(rho.statistic),pvalue=float(rho.pvalue)),
             noise_width_monotone_networks=int(np.sum((np.array(metrics['both_noise4']['width2'])>=metrics['both']['width2'])&(np.array(metrics['both_noise16']['width2'])>=metrics['both_noise4']['width2']))),
             seconds=sum(x['seconds'] for x in raw))
    dump(HERE/'analysis/profile_summary.json',out);print(json.dumps(comp,indent=2))
    return out

def methods():
    raw=load('method_validation',45000,40);policies=['local','ensemble','prior_cov','prior_cv','random']
    metrics={p:[float(np.mean([r['mse'] for r in x['records'] if r['policy']==p])) for x in raw] for p in policies}
    comparisons={a+'_vs_'+b:bootstrap_change(metrics[a],metrics[b]) for a,b in [('prior_cv','local'),('prior_cov','local'),('ensemble','local'),('prior_cv','ensemble'),('prior_cv','prior_cov'),('prior_cv','random'),('prior_cov','ensemble'),('prior_cov','random'),('ensemble','random')]}
    audit={}
    for p in policies:
        rr=[r for x in raw for r in x['records'] if r['policy']==p]
        ds=[d for x in raw for d in x['designs'] if d['policy']==p]
        audit[p]=dict(fits=len(rr),chosen_fit_success=sum(r['best']['success'] for r in rr),
            certified_suboptimal=sum(r['best']['objective']>r['teacher_objective']+.001 for r in rr),
            all_starts_failed=sum(not any(f['success'] for f in r['fits']) for r in rr),
            median_selection_seconds=float(np.median([d['selection_seconds'] for d in ds])),
            median_shared_bank_seconds=float(np.median([d['shared_bank_seconds'] for d in ds])))
    out=dict(networks=40,metrics=metrics,comparisons=comparisons,audit=audit,seconds=sum(x['seconds'] for x in raw))
    dump(HERE/'analysis/method_summary.json',out);print(json.dumps(comparisons,indent=2));return out

def oracle():
    raw=load('oracle_refit',40000,40);base=load('profile_audited',40000,40)
    ps=['known_stim','known_readouts','known_both','known_random4']
    metrics={p:[next(r['mse'] for r in x['records'] if r['policy']==p) for x in raw] for p in ps}
    for p in ['neither','both']:
        metrics[p]=[next(r['mse'] for r in x['records'] if r['policy']==p) for x in base]
    comparisons={a+'_vs_'+b:bootstrap_change(metrics[a],metrics[b]) for a,b in [
        ('known_stim','neither'),('known_readouts','neither'),('known_both','neither'),
        ('known_random4','neither'),('known_both','known_random4'),('known_both','known_stim'),
        ('known_both','known_readouts'),('known_both','both')]}
    audit={p:dict(selected_fit_success=sum(next(r['best']['success'] for r in x['records'] if r['policy']==p) for x in raw)) for p in ps}
    out=dict(networks=40,metrics=metrics,comparisons=comparisons,audit=audit,scope='Oracle mechanism diagnostic only; hidden gains are revealed and all other gains refitted')
    dump(HERE/'analysis/oracle_summary.json',out);print(json.dumps(comparisons,indent=2));return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['profiles','methods','oracle']);a=ap.parse_args()
    {'profiles':profiles,'methods':methods,'oracle':oracle}[a.phase]()
