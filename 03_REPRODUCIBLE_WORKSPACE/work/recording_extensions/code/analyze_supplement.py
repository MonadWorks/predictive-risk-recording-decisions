"""Network-level paired analysis of the prespecified supplement."""
import argparse
from collections import defaultdict
import csv
import json
import os
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT/'analysis'
os.environ.setdefault('MPLCONFIGDIR', str(ROOT/'scratch/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def write_csv(path, rows):
    if not rows:
        return
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def load_runs(group):
    dirs = sorted((ROOT/'runs').glob(group+'_shard_*'))
    if len(dirs) != 4:
        raise RuntimeError(f'{group}: expected four shards')
    rows, designs, ranking, statuses = [], [], [], []
    for run in dirs:
        status = json.loads((run/'status.json').read_text())
        if not status['complete']:
            raise RuntimeError(f'{run} is incomplete')
        statuses.append(status)
        with (run/'results.csv').open() as f:
            rows.extend(csv.DictReader(f))
        designs.extend(json.loads((run/'designs.json').read_text()))
        if (run/'ranking_diagnostics.jsonl').exists():
            ranking.extend(json.loads(line) for line in (run/'ranking_diagnostics.jsonl').read_text().splitlines())
    planned = json.loads((ROOT/'protocols'/(group+'.json')).read_text())['network_ids']
    completed = [nid for s in statuses for nid in s['networks_completed']]
    assert sorted(completed) == sorted(planned) and len(set(completed)) == len(planned)
    return rows, designs, ranking, statuses


def network_means(rows):
    groups = defaultdict(list)
    for row in rows:
        key = (int(row['network_id']), row['condition'], row['pool'], int(row['budget']), row['method'])
        groups[key].append(row)
    result = []
    for key, values in sorted(groups.items()):
        mse = np.array([float(v['squared_error']) for v in values])
        normalized = np.array([float(v['normalized_squared_error']) for v in values])
        result.append(dict(zip(['network_id','condition','pool','budget','method'], key),
                           mse=float(mse.mean()), normalized_mse=float(normalized.mean()),
                           rows=len(values), failures=sum(v['optimizer_success'] != 'True' for v in values)))
    return result


def paired(a, b, seed=20261018):
    """a is reference; b is comparator. Relative effect is ratio of mean MSEs."""
    a, b = np.asarray(a), np.asarray(b)
    assert a.shape == b.shape and a.ndim == 1 and len(a) > 1
    diff = b-a
    rng = np.random.default_rng(seed)
    ix = rng.integers(0, len(a), size=(10000, len(a)))
    boot_a = a[ix].mean(axis=1)
    boot_b = b[ix].mean(axis=1)
    pct = 100*(b.mean()/a.mean()-1)
    boot_pct = 100*(boot_b/boot_a-1)
    loo = np.array([100*(np.delete(b,i).mean()/np.delete(a,i).mean()-1) for i in range(len(a))])
    denom = np.abs(diff).sum()
    return dict(n=len(a), reference_mse=float(a.mean()), comparator_mse=float(b.mean()),
                relative_percent=float(pct), ci_low=float(np.quantile(boot_pct,.025)),
                ci_high=float(np.quantile(boot_pct,.975)), mean_difference=float(diff.mean()),
                difference_ci_low=float(np.quantile((b[ix]-a[ix]).mean(axis=1),.025)),
                difference_ci_high=float(np.quantile((b[ix]-a[ix]).mean(axis=1),.975)),
                wins=int(np.sum(b<a)), ties=int(np.sum(b==a)), losses=int(np.sum(b>a)),
                leave_one_out_min=float(loo.min()), leave_one_out_max=float(loo.max()),
                largest_absolute_difference_share=float(np.abs(diff).max()/denom) if denom else 0.,
                median_network_relative_percent=float(np.median(100*(b/a-1))))


def contrasts(means, pairs):
    lookup = {(r['condition'],r['pool'],r['budget'],r['method'],r['network_id']):r for r in means}
    strata = sorted({(r['condition'],r['pool'],r['budget']) for r in means})
    result = []
    for condition,pool,budget in strata:
        for reference,comparator in pairs:
            ids = sorted(r['network_id'] for r in means if (r['condition'],r['pool'],r['budget'],r['method']) == (condition,pool,budget,reference))
            if not ids or any((condition,pool,budget,comparator,nid) not in lookup for nid in ids):
                continue
            for metric in ['mse','normalized_mse']:
                a = [lookup[condition,pool,budget,reference,nid][metric] for nid in ids]
                b = [lookup[condition,pool,budget,comparator,nid][metric] for nid in ids]
                row = dict(condition=condition,pool=pool,budget=budget,reference=reference,
                           comparator=comparator,metric=metric,**paired(a,b))
                result.append(row)
    return result


def quality(rows, statuses):
    fits = {}
    for row in rows:
        key = tuple(row[k] for k in ['network_id','condition','truth_id','noise_id','nodes'])
        fits[key] = row
    failed = [r for r in fits.values() if r['optimizer_success'] != 'True']
    fallback = [r for r in fits.values() if r['fallback'] == 'True']
    return dict(evaluation_rows=len(rows), independent_networks=len({r['network_id'] for r in rows}),
                unique_fits=len(fits), failed_unique_fits=len(failed), fallback_unique_fits=len(fallback),
                total_worker_seconds=sum(s['elapsed_seconds'] for s in statuses),
                unique_failed_cases=[{k:r[k] for k in ['network_id','condition','truth_id','noise_id','nodes','nfev','fit_error']} for r in failed])


def agreement(designs, neurons=100):
    look={(d['network_id'],d['condition'],d['pool'],d['budget'],d['method'],d['target']):d for d in designs}
    output=[]
    for d in designs:
        if d['method'] not in ['local_vector','local_scalar']:
            continue
        family=d['method'].split('_')[1]
        other=look.get((d['network_id'],d['condition'],d['pool'],d['budget'],'ensemble_'+family,d['target']))
        if other is None:continue
        a,b=set(d['nodes']),set(other['nodes'])
        candidate_count=neurons-4 if d['pool']=='exclude_endpoints' else neurons
        chance=d['budget']/candidate_count
        retained=len(a&b)/len(a)
        output.append(dict(network_id=d['network_id'],condition=d['condition'],pool=d['pool'],budget=d['budget'],
                           family=family,target=d['target'],identical=a==b,retained_fraction=retained,
                           candidate_count=candidate_count,chance_retained_fraction=chance,
                           chance_adjusted_overlap=(retained-chance)/(1-chance),
                           jaccard=len(a&b)/len(a|b),
                           nominal_risk_reduction=float(np.mean(d['risk_nominal'])-np.mean(other['risk_nominal'])),
                           ensemble_risk_reduction=float(np.mean(d['risk_ensemble'])-np.mean(other['risk_ensemble']))))
    return output


def component_agreement(designs):
    look={(d['network_id'],d['condition'],d['budget'],d['method']):d for d in designs}
    rows=[]
    for d in designs:
        if d['method'] not in ['local_vector','ensemble_vector']:continue
        for other_method in ['ensemble_fixed_goal','ensemble_fixed_info']:
            other=look[d['network_id'],d['condition'],d['budget'],other_method]
            a,b=set(d['nodes']),set(other['nodes'])
            rows.append(dict(network_id=d['network_id'],condition=d['condition'],budget=d['budget'],
                             reference=d['method'],comparator=other_method,identical=a==b,
                             retained_fraction=len(a&b)/len(a)))
    summary=[]
    groups=defaultdict(list)
    for r in rows:groups[r['condition'],r['budget'],r['reference'],r['comparator']].append(r)
    for key,rs in sorted(groups.items()):
        summary.append(dict(zip(['condition','budget','reference','comparator'],key),
                            networks=len(rs),identical_count=sum(r['identical'] for r in rs),
                            mean_retained_fraction=float(np.mean([r['retained_fraction'] for r in rs]))))
    write_csv(OUT/'component_recording_agreement.csv',rows)
    write_csv(OUT/'component_agreement_summary.csv',summary)


def paired_mechanism_trends(ranking, overlap):
    lookup={(r['network_id'],r['prior_sd']):r for r in ranking}
    ids=sorted({r['network_id'] for r in ranking})
    rng=np.random.default_rng(20261018)
    ix=rng.integers(0,len(ids),size=(10000,len(ids)))
    rows=[]
    def add(metric,a,b,**extra):
        a,b=np.asarray(a),np.asarray(b);d=b-a
        rows.append(dict(metric=metric,**extra,low_mean=float(a.mean()),high_mean=float(b.mean()),
                         mean_change=float(d.mean()),ci_low=float(np.quantile(d[ix].mean(axis=1),.025)),
                         ci_high=float(np.quantile(d[ix].mean(axis=1),.975)),networks_decreased=int(np.sum(d<0))))
    for feature in ['nominal_ensemble_rank_correlation','mean_nominal_particle_rank_correlation']:
        add(feature,[lookup[i,.3][feature] for i in ids],[lookup[i,.9][feature] for i in ids])
    look={(r['network_id'],r['condition'],r['budget']):r for r in overlap}
    for budget in [5,10]:
        add('retained_fraction',[look[i,'gain_sd_0.3',budget]['retained_fraction'] for i in ids],
            [look[i,'gain_sd_0.9',budget]['retained_fraction'] for i in ids],budget=budget)
    (OUT/'paired_mechanism_trends.json').write_text(json.dumps(rows,indent=2)+'\n')


def plot_confirmation(means, effects):
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig, axes=plt.subplots(1,2,figsize=(9.5,4.1))
    for ax,budget in zip(axes,[5,10]):
        vals={method:{r['network_id']:r['mse'] for r in means if r['pool']=='exclude_endpoints' and r['budget']==budget and r['method']==method}
              for method in ['local_vector','ensemble_vector']}
        ids=sorted(vals['local_vector'])
        x=np.array([vals['local_vector'][i] for i in ids]);y=np.array([vals['ensemble_vector'][i] for i in ids])
        low=min(x.min(),y.min())*.65;high=max(x.max(),y.max())*1.4
        ax.plot([low,high],[low,high],color='#9B9B9B',lw=1)
        ax.scatter(x,y,color='#B14F77',s=28,alpha=.8,edgecolor='white',linewidth=.4)
        ax.set(xscale='log',yscale='log',xlim=(low,high),ylim=(low,high),xlabel='Nominal selection: response MSE',ylabel='Ensemble selection: response MSE')
        eff=next(e for e in effects if e['pool']=='exclude_endpoints' and e['budget']==budget and e['reference']=='local_vector' and e['comparator']=='ensemble_vector' and e['metric']=='mse')
        ax.set_title(f"{budget} recordings | {eff['n']} new networks",loc='left',fontweight='bold')
        ax.text(.04,.96,f"Mean effect {eff['relative_percent']:+.1f}%\n95% CI [{eff['ci_low']:+.1f}, {eff['ci_high']:+.1f}]%\nLower MSE: {eff['wins']}/{eff['n']}",transform=ax.transAxes,va='top',fontsize=9)
    fig.tight_layout()
    for ext in ['png','pdf']:fig.savefig(OUT/f'confirmation.{ext}',dpi=300)
    plt.close(fig)


def plot_pilot_comparison(effects):
    with (ROOT/'reference_data/original_n100_paired_effects.csv').open() as f:
        old=list(csv.DictReader(f))
    strata=[('all',5),('all',10),('exclude_endpoints',5),('exclude_endpoints',10)]
    labels=['All sites, 5','All sites, 10','Endpoints excluded, 5','Endpoints excluded, 10']
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),sharey=True)
    table=[]
    for ax,objective,title in zip(axes,['scalar','vector'],['Single response','Shared three responses']):
        for y,(pool,budget) in enumerate(strata):
            pilot=next(r for r in old if r['pool']==pool and int(r['budget'])==budget and r['contrast']==f'ensemble_{objective} - local_{objective}' and r['metric']=='mse')
            fresh=next(r for r in effects if r['pool']==pool and r['budget']==budget and r['reference']=='local_'+objective and r['comparator']=='ensemble_'+objective and r['metric']=='mse')
            x=100*float(pilot['relative_mse_difference']);lo=100*float(pilot['relative_mse_ci_low']);hi=100*float(pilot['relative_mse_ci_high'])
            ax.hlines(y-.12,lo,hi,color='#9C9C9C',lw=1.2)
            ax.scatter(x,y-.12,color='white',edgecolor='#777777',s=35,zorder=3,label='Original 8 networks' if y==0 else None)
            ax.hlines(y+.12,fresh['ci_low'],fresh['ci_high'],color='#B14F77',lw=1.8)
            ax.scatter(fresh['relative_percent'],y+.12,color='#B14F77',s=35,zorder=3,label='40 new networks' if y==0 else None)
            table.append(dict(objective=objective,pool=pool,budget=budget,pilot_percent=x,pilot_ci_low=lo,pilot_ci_high=hi,new_percent=fresh['relative_percent'],new_ci_low=fresh['ci_low'],new_ci_high=fresh['ci_high']))
        ax.axvline(0,color='#777777',lw=.8)
        ax.set_xscale('symlog',linthresh=10)
        ax.set_title(title,loc='left',fontweight='bold')
        ax.set(yticks=range(4),yticklabels=labels,xlabel='MSE change (%) | symmetric log scale',ylim=(3.5,-.5))
        ax.legend(frameon=False,fontsize=8,loc='best')
    fig.tight_layout()
    write_csv(OUT/'pilot_and_confirmation.csv',table)
    for ext in ['png','pdf']:fig.savefig(OUT/f'pilot_and_confirmation.{ext}',dpi=300)
    plt.close(fig)


def plot_mechanism(effects, overlap):
    conditions=['gain_sd_0.3','gain_sd_0.6','gain_sd_0.9']
    methods=['ensemble_vector','ensemble_fixed_goal','ensemble_fixed_info']
    labels=['Full ensemble','Goal fixed','Observation fixed']
    colors=['#B14F77','#447F9D','#B18438']
    fig,axes=plt.subplots(2,2,figsize=(10,7))
    for col,budget in enumerate([5,10]):
        ax=axes[0,col]
        for offset,method,label,color in zip([-.18,0,.18],methods,labels,colors):
            rows=[next(e for e in effects if e['condition']==c and e['budget']==budget and e['reference']=='local_vector' and e['comparator']==method and e['metric']=='mse') for c in conditions]
            y=np.array([r['relative_percent'] for r in rows]);lo=np.array([r['ci_low'] for r in rows]);hi=np.array([r['ci_high'] for r in rows])
            # Percentile intervals can exclude the point estimate for skewed samples.
            x=np.arange(3)+offset
            ax.vlines(x,lo,hi,color=color,lw=1.3)
            ax.scatter(x,y,color=color,s=28,label=label,zorder=3)
        ax.axhline(0,color='#999999',lw=.8)
        ax.set_yscale('symlog',linthresh=10)
        ax.set(xticks=range(3),xticklabels=['0.3','0.6','0.9'],xlabel='Matched gain-prior SD',ylabel='MSE change (%) | symmetric log scale')
        ax.set_title(f'{budget} recordings',loc='left',fontweight='bold')
        if col==0:ax.legend(frameon=False,fontsize=8)
        ax=axes[1,col]
        ax.axhline(budget/96,color='#999999',lw=.8,ls=':',label='Random-set expectation')
        for x,c in enumerate(conditions):
            vals=np.array([r['retained_fraction'] for r in overlap if r['condition']==c and r['budget']==budget and r['family']=='vector'])
            ax.scatter(x+np.linspace(-.13,.13,len(vals)),vals,color='#B14F77',alpha=.5,s=15)
            ax.plot([x-.18,x+.18],[vals.mean()]*2,color='#222222',lw=2)
        ax.set(xticks=range(3),xticklabels=['0.3','0.6','0.9'],xlabel='Matched gain-prior SD',ylabel='Fraction of recording sites retained',ylim=(-.04,1.04))
    fig.tight_layout()
    for ext in ['png','pdf']:fig.savefig(OUT/f'mechanism.{ext}',dpi=300)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('group',choices=['confirmation','mechanism']);args=parser.parse_args()
    rows,designs,ranking,statuses=load_runs(args.group)
    means=network_means(rows)
    pairs=[('local_vector','ensemble_vector'),('local_scalar','ensemble_scalar'),('random','ensemble_vector'),('local_activity','ensemble_vector'),('random','local_vector'),('local_activity','local_vector')]
    if args.group=='mechanism':
        pairs=[('local_vector','ensemble_vector'),('local_vector','ensemble_fixed_goal'),('local_vector','ensemble_fixed_info'),('ensemble_vector','ensemble_fixed_goal'),('ensemble_vector','ensemble_fixed_info')]
    effects=contrasts(means,pairs)
    overlap=agreement(designs)
    write_csv(OUT/f'{args.group}_network_means.csv',means)
    write_csv(OUT/f'{args.group}_effects.csv',effects)
    write_csv(OUT/f'{args.group}_recording_agreement.csv',overlap)
    q=quality(rows,statuses)
    (OUT/f'{args.group}_quality.json').write_text(json.dumps(q,indent=2)+'\n')
    (OUT/f'{args.group}_effects.json').write_text(json.dumps(effects,indent=2)+'\n')
    if args.group=='confirmation':
        plot_confirmation(means,effects)
        plot_pilot_comparison(effects)
    else:
        plot_mechanism(effects,overlap)
        component_agreement(designs)
        compact=[{k:v for k,v in r.items() if not isinstance(v,list)} for r in ranking]
        write_csv(OUT/'ranking_diagnostics.csv',compact)
        paired_mechanism_trends(ranking,overlap)
        # Relate pre-observation rankings to realized network-level effects.
        associations=[]
        lookup={(r['network_id'],r['condition'],r['budget'],r['method']):r['mse'] for r in means}
        for c in ['gain_sd_0.3','gain_sd_0.6','gain_sd_0.9']:
            for budget in [5,10]:
                ds=[d for d in compact if f"gain_sd_{d['prior_sd']:.1f}"==c]
                nid=[d['network_id'] for d in ds]
                effect=np.array([(lookup[i,c,budget,'ensemble_vector']-lookup[i,c,budget,'local_vector'])/lookup[i,c,budget,'local_vector'] for i in nid])
                for feature in ['nominal_ensemble_rank_correlation','mean_nominal_particle_rank_correlation','particle_nominal_best_agreement','nominal_relative_top_gap','first_step_ensemble_regret_of_nominal']:
                    x=np.array([d[feature] for d in ds]);rho,p=spearmanr(x,effect)
                    associations.append(dict(condition=c,budget=budget,feature=feature,n=len(ds),spearman_rho=float(rho),exploratory_p=float(p)))
        write_csv(OUT/'ranking_effect_associations.csv',associations)
        components=[]
        for d in designs:
            record={k:d[k] for k in ['network_id','condition','pool','budget','method','risk_observation_component','risk_target_component','risk_interaction_component']}
            record.update(risk_nominal=float(np.mean(d['risk_nominal'])),risk_ensemble=float(np.mean(d['risk_ensemble'])))
            components.append(record)
        write_csv(OUT/'risk_components.csv',components)
    import hashlib
    from datetime import datetime,timezone
    (OUT/f'{args.group}_analysis_receipt.json').write_text(json.dumps(dict(
        complete=True,timestamp_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        bootstrap_replicates=10000,bootstrap_seed=20261018,independent_unit='network',
        networks=q['independent_networks']),indent=2)+'\n')
    print(json.dumps(dict(group=args.group,quality=q,primary_or_full_vector_effects=[e for e in effects if e['pool']=='exclude_endpoints' and e['reference']=='local_vector' and e['comparator']=='ensemble_vector' and e['metric']=='mse']),indent=2))


if __name__=='__main__':main()
