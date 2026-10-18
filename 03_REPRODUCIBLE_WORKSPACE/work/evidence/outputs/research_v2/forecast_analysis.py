"""Analyze the separately frozen, independent risk-forecast follow-up.

Compare risk forecasts on identical recording sets and point predictions.
This is an MSE-functional score comparison, not a Gaussian-likelihood or
complete probabilistic-calibration claim. No first-study primary is changed.
"""
import argparse
import csv
import hashlib
import itertools
import json
import os
from pathlib import Path

import numpy as np

os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parent / '.mpl-cache'))
os.environ.setdefault('XDG_CACHE_HOME', '/tmp/icbr-v2-analysis-xdg-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BOOTSTRAP_SEED = 870232
KEYS = ['network_id', 'condition', 'pool', 'budget', 'recording_policy']
NOMINAL_COLOR = '#777777'
ENSEMBLE_COLOR = '#0072B2'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def truth(value):
    if value in ['True', 'true', '1']: return True
    if value in ['False', 'false', '0']: return False
    raise ValueError('Unrecognized boolean ' + repr(value))


def grouped(rows, keys):
    output = {}
    for row in rows: output.setdefault(tuple(row[k] for k in keys), []).append(row)
    return output


def write_csv(path, rows):
    if not rows: return
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def clean(value):
    if isinstance(value, dict): return {k: clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [clean(v) for v in value]
    if isinstance(value, np.integer): return int(value)
    if isinstance(value, (float, np.floating)): return float(value) if np.isfinite(value) else None
    if isinstance(value, np.ndarray): return clean(value.tolist())
    return value


def load(run, freeze):
    cfg = json.loads((run/'protocol.json').read_text()); status = json.loads((run/'status.json').read_text())
    receipt = json.loads(freeze.read_text())
    if not status['complete']: raise ValueError('Follow-up must finish before analysis; partial outcomes are not read')
    if sha(run/'protocol.json') != receipt['protocol_sha256']: raise ValueError('Frozen follow-up protocol mismatch')
    if (run/'protocol.sha256').read_text().strip() != receipt['protocol_sha256']: raise ValueError('Run protocol receipt mismatch')
    if cfg['phase'] != 'independent_risk_forecast_followup': raise ValueError('Wrong study phase')
    rows = []
    with (run/'results.csv').open(newline='') as f:
        for source in csv.DictReader(f):
            row = {k: int(source[k]) for k in ['network_id', 'budget', 'truth_id', 'noise_id', 'target_id', 'design_repeat']}
            row.update(condition=source['condition'], pool=source['pool'], recording_policy=source['method'], nodes=source['nodes'])
            for k in ['q_true', 'q_hat', 'error', 'squared_error', 'abs_error', 'risk_nominal', 'risk_ensemble']:
                row[k] = float(source[k])
                if not np.isfinite(row[k]): raise ValueError('Nonfinite forecast or prediction; do not filter silently')
            if min(row['risk_nominal'], row['risk_ensemble']) < 0: raise ValueError('Negative risk forecast')
            if not np.isclose(row['q_hat']-row['q_true'],row['error'],rtol=1e-12,atol=1e-15): raise ValueError('Error mismatch')
            if not np.isclose(row['error']**2,row['squared_error'],rtol=1e-12,atol=1e-25): raise ValueError('Squared-error mismatch')
            row.update(optimizer_success=truth(source['optimizer_success']),fallback=truth(source['fallback']))
            floor = cfg['forecast_variance_floor']
            vn=max(row['risk_nominal'],floor);ve=max(row['risk_ensemble'],floor)
            row.update(nominal_score=float(np.log(vn)+row['squared_error']/vn),
                       ensemble_score=float(np.log(ve)+row['squared_error']/ve),
                       nominal_effective_risk=vn,ensemble_effective_risk=ve,
                       effective_case_risk_ratio=ve/vn,
                       nominal_below_floor=row['risk_nominal']<floor,
                       ensemble_below_floor=row['risk_ensemble']<floor,
                       nominal_at_or_below_floor=row['risk_nominal']<=floor,
                       ensemble_at_or_below_floor=row['risk_ensemble']<=floor)
            row['score_difference']=row['ensemble_score']-row['nominal_score']
            if not np.isfinite([row['nominal_score'],row['ensemble_score'],row['score_difference']]).all():
                raise ValueError('Nonfinite score; retain data and investigate')
            rows.append(row)
    if len(rows) != status['evaluated_rows']: raise ValueError('Checkpoint row-count mismatch')
    if sorted(set(r['network_id'] for r in rows)) != sorted(cfg['network_ids']): raise ValueError('Missing networks')
    cells=grouped(rows,KEYS)
    expected=set(itertools.product(cfg['network_ids'],[c['name'] for c in cfg['conditions']],cfg['pools'],cfg['budgets'],cfg['methods']))
    if set(cells)!=expected: raise ValueError('Missing/unexpected network-stratum-policy cells')
    expected_repeats=set(itertools.product(range(cfg['truth_repeats']),range(cfg['noise_repeats']),range(cfg['targets']),[0]))
    for key,cell in cells.items():
        actual=[tuple(r[k] for k in ['truth_id','noise_id','target_id','design_repeat']) for r in cell]
        if len(actual)!=len(set(actual)) or set(actual)!=expected_repeats:
            raise ValueError('Unbalanced nested repeats: '+repr(key))
    return cfg,status,receipt,rows


def aggregate(rows):
    result=[]
    for key,cell in sorted(grouped(rows,KEYS).items()):
        mean=lambda field:float(np.mean([r[field] for r in cell]))
        item=dict(zip(KEYS,key))
        item.update(raw_mse=mean('squared_error'),raw_mae=mean('abs_error'),
                    nominal_score=mean('nominal_score'),ensemble_score=mean('ensemble_score'),
                    score_difference=mean('score_difference'),nominal_risk=mean('risk_nominal'),
                    ensemble_risk=mean('risk_ensemble'),nominal_effective_risk=mean('nominal_effective_risk'),
                    ensemble_effective_risk=mean('ensemble_effective_risk'),
                    mean_effective_case_risk_ratio=mean('effective_case_risk_ratio'),
                    optimizer_failure_rate=1-mean('optimizer_success'),fallback_rate=mean('fallback'),
                    rows=len(cell))
        for forecast in ['nominal','ensemble']:
            item[forecast+'_below_floor']=sum(r[forecast+'_below_floor'] for r in cell)
            item[forecast+'_at_or_below_floor']=sum(r[forecast+'_at_or_below_floor'] for r in cell)
        item['risk_ratio_of_network_means']=item['ensemble_risk']/item['nominal_risk'] if item['nominal_risk']>0 else float('nan')
        result.append(item)
    return result


def interval(boot): return np.quantile(boot,[.025,.975]).tolist()


def summarize(networks,cfg):
    results=[];loo=[]
    for key,cell in sorted(grouped(networks,['condition','pool','budget','recording_policy']).items()):
        cell=sorted(cell,key=lambda r:r['network_id'])
        n=len(cell);indices=np.random.default_rng(BOOTSTRAP_SEED).integers(0,n,(cfg['forecast_bootstrap_replicates'],n))
        item=dict(zip(['condition','pool','budget','recording_policy'],key))
        primary=cfg['forecast_primary']
        item.update(primary=all(item.get(k)==primary[k] for k in ['condition','pool','budget','recording_policy']),
                    independent_networks=n,confidence_level=.95)
        for metric in ['raw_mse','raw_mae','nominal_score','ensemble_score','score_difference','nominal_risk','ensemble_risk',
                       'nominal_effective_risk','ensemble_effective_risk','mean_effective_case_risk_ratio',
                       'optimizer_failure_rate','fallback_rate']:
            values=np.array([r[metric] for r in cell]);item[metric]=float(values.mean())
            item[metric+'_ci_low'],item[metric+'_ci_high']=interval(values[indices].mean(1))
        mse=np.array([r['raw_mse'] for r in cell]);item['raw_rmse']=float(np.sqrt(mse.mean()))
        item['raw_rmse_ci_low'],item['raw_rmse_ci_high']=interval(np.sqrt(mse[indices].mean(1)))
        vn=np.array([r['nominal_risk'] for r in cell]);ve=np.array([r['ensemble_risk'] for r in cell])
        item['risk_ratio_of_aggregate_means']=float(ve.mean()/vn.mean()) if vn.mean()>0 else float('nan')
        denominator=vn[indices].mean(1)
        if np.all(denominator>0):ratio_interval=interval(ve[indices].mean(1)/denominator)
        else:ratio_interval=[float('nan')]*2
        item['risk_ratio_of_aggregate_means_ci_low'],item['risk_ratio_of_aggregate_means_ci_high']=ratio_interval
        for forecast in ['nominal','ensemble']:
            item[forecast+'_below_floor']=sum(r[forecast+'_below_floor'] for r in cell)
            item[forecast+'_at_or_below_floor']=sum(r[forecast+'_at_or_below_floor'] for r in cell)
        d=np.array([r['score_difference'] for r in cell])
        item.update(negative_networks=int(sum(d<0)),positive_networks=int(sum(d>0)),exact_ties=int(sum(d==0)),
                    raw_mse_identical_for_forecasts=True)
        for j,r in enumerate(cell):
            loo.append(dict(condition=key[0],pool=key[1],budget=key[2],recording_policy=key[3],
                            omitted_network_id=r['network_id'],full_score_difference=float(d.mean()),
                            leave_one_out_score_difference=float(np.delete(d,j).mean()),
                            individual_score_difference=float(d[j])))
        item['loo_min']=min(x['leave_one_out_score_difference'] for x in loo[-n:])
        item['loo_max']=max(x['leave_one_out_score_difference'] for x in loo[-n:])
        results.append(item)
    return results,loo


def save(fig,out,name):
    fig.savefig(out/(name+'.png'),dpi=300,bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');plt.close(fig)


def figures(networks,strata,cfg,out):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':9,
                         'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    primary=next(r for r in strata if r['primary'])
    cell=[r for r in networks if all(r[k]==primary[k] for k in ['condition','pool','budget','recording_policy'])]
    d=np.array([r['score_difference'] for r in cell]);rng=np.random.default_rng(8401)
    fig,ax=plt.subplots(figsize=(6.5,4.7))
    ax.scatter(rng.uniform(-.10,.10,len(d)),d,s=24,color=ENSEMBLE_COLOR,alpha=.75)
    center=primary['score_difference'];low=primary['score_difference_ci_low'];high=primary['score_difference_ci_high']
    ax.errorbar(.37,center,yerr=[[max(0,center-low)],[max(0,high-center)]],fmt='s',color='black',capsize=5,markersize=6)
    ax.axhline(0,color='#777777',linewidth=.8);ax.set_xticks([0,.37],['Independent networks','Mean, 95% CI'])
    ax.set_ylabel('Score difference: ensemble − nominal')
    fig.suptitle('Independent follow-up: risk forecast comparison\nBroad prior | endpoints excluded | M = 3 | local-scalar recordings',fontsize=10)
    fig.text(.5,.015,f'n = {len(cell)} independent networks; {cfg["truth_repeats"]} truths × {cfg["noise_repeats"]} noise draws × {cfg["targets"]} readouts per network.\n'
             'Identical recording sets and point predictions; negative score difference favors ensemble.\n'
             '95% paired network-cluster bootstrap CI; all networks retained.',ha='center',va='bottom',fontsize=8)
    fig.tight_layout(rect=(0,.15,1,.9));save(fig,out,'forecast_primary_score_difference')
    fig,axes=plt.subplots(len(cfg['conditions']),len(cfg['methods']),figsize=(10,3.1*len(cfg['conditions'])),squeeze=False)
    for i,condition in enumerate(cfg['conditions']):
      for j,policy in enumerate(cfg['methods']):
        ax=axes[i,j];data=[r for r in networks if r['condition']==condition['name'] and r['recording_policy']==policy]
        s=next(r for r in strata if r['condition']==condition['name'] and r['recording_policy']==policy)
        y=np.array([r['score_difference'] for r in data]);ax.scatter(rng.uniform(-.10,.10,len(y)),y,s=18,c=ENSEMBLE_COLOR,alpha=.7)
        z=s['score_difference'];ax.errorbar(.35,z,yerr=[[max(0,z-s['score_difference_ci_low'])],[max(0,s['score_difference_ci_high']-z)]],fmt='s',color='black',capsize=4)
        ax.axhline(0,color='#777777',linewidth=.8);ax.set_xticks([0,.35],['Networks','Mean, 95% CI'])
        ax.set_title(condition['name']+' | '+policy+(' | PRIMARY' if s['primary'] else ' | exploratory'))
        ax.set_ylabel('Score difference: ensemble − nominal')
    fig.suptitle('Independent follow-up: all prespecified strata\nPanel y ranges differ; do not compare visual heights across panels',fontsize=10)
    fig.tight_layout();save(fig,out,'forecast_all_score_differences')
    fig,axes=plt.subplots(1,2,figsize=(10,4.5));maxval=max(max(r['raw_mse'],r['nominal_risk'],r['ensemble_risk']) for r in cell)*1.04
    for ax,forecast,color in zip(axes,['nominal','ensemble'],[NOMINAL_COLOR,ENSEMBLE_COLOR]):
        ax.scatter([r[forecast+'_risk'] for r in cell],[r['raw_mse'] for r in cell],s=24,color=color,alpha=.75)
        ax.plot([0,maxval],[0,maxval],color='#777777',linestyle='--',linewidth=.8)
        ax.set_xlim(0,maxval);ax.set_ylim(0,maxval);ax.set_xlabel('Mean predicted raw risk (q units squared)')
        ax.set_ylabel('Realized network MSE (q units squared)');ax.set_title(forecast.capitalize()+' risk forecast')
    fig.suptitle('Primary follow-up: network means, descriptive risk comparison\nIdentical realized MSE for both forecasts; no full probability-calibration claim',fontsize=10)
    fig.tight_layout();save(fig,out,'forecast_risk_vs_actual')
    fig,axes=plt.subplots(1,2,figsize=(10,4.5))
    ratios=np.array([r['risk_ratio_of_network_means'] for r in cell]);valid=np.isfinite(ratios)
    axes[0].scatter(rng.uniform(-.1,.1,sum(valid)),ratios[valid],s=24,color=ENSEMBLE_COLOR,alpha=.75)
    z=primary['risk_ratio_of_aggregate_means'];lo=primary['risk_ratio_of_aggregate_means_ci_low'];hi=primary['risk_ratio_of_aggregate_means_ci_high']
    if np.isfinite([z,lo,hi]).all():axes[0].errorbar(.35,z,yerr=[[max(0,z-lo)],[max(0,hi-z)]],fmt='s',color='black',capsize=4)
    axes[0].axhline(1,color='#777777',linewidth=.8);axes[0].set_xticks([0,.35],['Network risk ratios','Ratio of aggregate means'])
    axes[0].set_ylabel('Mean ensemble risk / mean nominal risk');axes[0].set_title(f'Primary risk ratios; {sum(valid)}/{len(ratios)} finite')
    sorted_d=np.sort(d);axes[1].step(sorted_d,np.arange(1,len(d)+1)/len(d),where='post',color=ENSEMBLE_COLOR)
    axes[1].axvline(0,color='#777777',linewidth=.8);axes[1].set_xlabel('Network score difference: ensemble − nominal')
    axes[1].set_ylabel('Empirical cumulative proportion');axes[1].set_ylim(0,1.02);axes[1].set_title('All primary-network differences; tails retained')
    fig.suptitle('Independent follow-up: forecast size and score distribution\nBlack ratio mark is ratio of aggregate means, not mean of network ratios',fontsize=10)
    fig.tight_layout();save(fig,out,'forecast_ratios_and_distribution')


def main(run,out,freeze):
    cfg,status,receipt,rows=load(run,freeze);networks=aggregate(rows);strata,loo=summarize(networks,cfg)
    out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'paired_case_scores.csv',rows);write_csv(out/'network_metrics.csv',networks)
    write_csv(out/'stratum_metrics.csv',strata);write_csv(out/'leave_one_network_out.csv',loo)
    figures(networks,strata,cfg,out)
    summary=dict(study='independent risk-forecast follow-up',first_study_primary_unchanged=True,
                 hypotheses_frozen_before_followup_outcomes=True,freeze_receipt=receipt,
                 primary=next(r for r in strata if r['primary']),all_strata=strata,
                 raw_rows=len(rows),independent_networks=len(cfg['network_ids']),
                 experiment_elapsed_seconds=status['elapsed_seconds'],actual_optimizer_calls=status['actual_optimizer_calls'],
                 point_predictions_shared=True,raw_mse_identical_for_forecasts=True,
                 score='S(v,e) = log(max(v,1e-24)) + e²/max(v,1e-24)',
                 score_interpretation='MSE-functional consistent score, not a Gaussian assumption or complete probability-calibration claim',
                 expected_score='For positive v and finite MSE: E S(v,e) = log(v) + MSE/v; derivative (v-MSE)/v². Minimum at MSE, or the floor on the clipped domain.',
                 analysis=dict(independent_unit='connection matrix J',nested_repeats='equal averaging of balanced truth/noise/readout repeats within J',
                   bootstrap_replicates=cfg['forecast_bootstrap_replicates'],bootstrap_seed=BOOTSTRAP_SEED,primary_interval='single prespecified 95% paired network-cluster percentile interval',
                   exploratory='all other strata, risk ratios and descriptive risk plots; no equivalence claim',
                   raw_risk_ratio='mean raw ensemble risk / mean raw nominal risk, aggregated across all J; cluster-bootstrap ratio interval',
                   case_ratio='mean effective casewise ratio after the fixed floor, reported separately; not a ratio of aggregate means',
                   failure_policy='all finite point predictions, flagged optimizer failures and fallback predictions retained',
                   score_floor=cfg['forecast_variance_floor']),
                 nominal_below_floor=sum(r['nominal_below_floor'] for r in rows),ensemble_below_floor=sum(r['ensemble_below_floor'] for r in rows),
                 nominal_at_or_below_floor=sum(r['nominal_at_or_below_floor'] for r in rows),ensemble_at_or_below_floor=sum(r['ensemble_at_or_below_floor'] for r in rows),
                 optimizer_failure_rows=sum(not r['optimizer_success'] for r in rows),fallback_rows=sum(r['fallback'] for r in rows),
                 results_sha256=sha(run/'results.csv'),protocol_sha256=sha(run/'protocol.json'),analysis_sha256=sha(Path(__file__)),
                 provenance=dict(run=str(run.resolve()),freeze=str(freeze.resolve()),command=f'python forecast_analysis.py --run {run} --out {out} --freeze {freeze}'),
                 scoring_history_reference='Gneiting and Raftery (2007), doi:10.1198/016214506000001437; score consistency here follows directly by differentiation, no new-score claim',
                 scoring_history_author_copy='https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf',
                 reference_access_note='Author-hosted paper metadata and introduction verified; its general proper-score history is separate from the direct MSE-functional calculation used here')
    (out/'summary.json').write_text(json.dumps(clean(summary),indent=2,allow_nan=False))
    notes=f'''# Independent risk-forecast follow-up: figures and estimand

The first study's primary tests remain unchanged. A separate hypothesis was frozen before a new independent set of {len(cfg['network_ids'])} simulated networks (IDs {min(cfg['network_ids'])}–{max(cfg['network_ids'])}) was generated. The sole follow-up primary is condition broad, endpoints excluded, M=3, local-scalar recording policy. All other conditions/policies are exploratory. Each network contributes {cfg['truth_repeats']} parameter truths × {cfg['noise_repeats']} noise draws × {cfg['targets']} readouts. These are nested repeats, not independent samples. All rows and all networks, including outliers and flagged failures, are retained.

For the identical point prediction and the identical chosen recording set in each row, the nominal and ensemble risk columns are scored by S(v,e)=log(max(v,10^-24))+e²/max(v,10^-24). Consequently the two forecasts have exactly the same realized raw MSE; any difference is forecast-score performance, not an improvement in the point prediction or a different recording decision. For v>0 and finite MSE, E S=log(v)+MSE/v and its derivative is (v−MSE)/v², so its unique positive optimum is v=MSE (or the floor when restricting to v≥floor). This is a consistent score for the MSE functional. It neither requires Gaussian errors nor demonstrates complete probability calibration, and is not a new scoring rule. General scoring-rule history: [Gneiting & Raftery, 2007](https://doi.org/10.1198/016214506000001437), with the [verified author-hosted copy](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf). That general background is separate from the direct MSE-functional calculation above.

Scores and errors are first averaged within each J; the paired score difference is ensemble minus nominal, negative favoring ensemble. Ten thousand paired resamples of whole networks (seed {BOOTSTRAP_SEED}) give a single primary 95% percentile interval. Other intervals are pointwise exploratory 95%. RMSE is sqrt(mean network MSE), with that transform recomputed per resample. The first study's outcomes are not pooled into this follow-up and its primary comparisons are not relabelled.

Risk ratios have separate definitions. `risk_ratio_of_aggregate_means` is mean(raw ensemble risk)/mean(raw nominal risk), with a paired cluster-bootstrap ratio interval. `mean_effective_case_risk_ratio` averages individual floor-adjusted case ratios, and need not equal the ratio of means. `risk_ratio_of_network_means` is provided only for the per-network distribution. A zero raw denominator gives NA rather than a silent replacement. Floor counts distinguish strictly-below-floor clipping from at-or-below-floor effective values. In this run nominal/ensemble below-floor counts are {summary['nominal_below_floor']}/{summary['ensemble_below_floor']} of {len(rows)} rows. There are {summary['optimizer_failure_rows']} flagged optimizer-failure rows and {summary['fallback_rows']} fallback rows; rows remain nested in J.

`forecast_primary_score_difference`: every primary J difference, zero reference and mean with 95% paired cluster CI. `forecast_all_score_differences`: all six condition/policy strata; y ranges differ and heights must not be compared across panels without numerical axes. `forecast_risk_vs_actual`: descriptive J means, common axes and y=x reference; same realized MSE in both panels. `forecast_ratios_and_distribution`: all finite network ratios plus the ratio of aggregate means, and a complete score-difference ECDF with tails retained. Figures are vector PDF with embedded TrueType fonts and 300dpi PNG; no outliers are suppressed.

`paired_case_scores.csv` contains exact row-level scores and forecasts. `network_metrics.csv` supplies the plotted independent-unit values; `stratum_metrics.csv` gives effects and intervals; `leave_one_network_out.csv` diagnoses influence without dropping networks. Reproduce: `{summary['provenance']['command']}`.
'''
    (out/'figure_captions_and_analysis.md').write_text(notes)
    print(json.dumps(clean(dict(primary=summary['primary'],raw_rows=len(rows),analysis_sha256=summary['analysis_sha256'])),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--freeze',type=Path,default=Path(__file__).resolve().parent/'risk_forecast_followup_freeze.json')
    a=p.parse_args();main(a.run,a.out,a.freeze)
