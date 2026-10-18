"""Network-cluster analysis of frozen recording-design experiments.

Usage: python analyze.py --run RUN_DIRECTORY --out ANALYSIS_DIRECTORY
No methods or experiment protocols are changed by this script. Partial runs
require explicit --allow-partial and are labelled exploratory throughout.
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
from scipy.stats import spearmanr

METHODS = ['local_scalar', 'ensemble_scalar', 'local_vector', 'ensemble_vector', 'local_activity', 'random']
LABELS = dict(zip(METHODS, ['LS', 'ES', 'LV', 'EV', 'Activity', 'Random']))
COLORS = dict(zip(METHODS, ['#0072B2', '#56B4E9', '#D55E00', '#E69F00', '#009E73', '#555555']))
MARKERS = dict(zip(METHODS, ['o', 's', '^', 'D', 'P', 'x']))
BOOTSTRAP_SEED = 870231
BASE_KEYS = ['network_id', 'condition', 'pool', 'budget', 'method']
FLOATS = ['q_true', 'q_hat', 'error', 'squared_error', 'abs_error', 'prior_mc_variance',
          'normalized_squared_error', 'risk_nominal', 'risk_ensemble', 'map_q_variance',
          'passive_mse', 'fit_seconds', 'nfev', 'fit_objective']
INTS = ['network_id', 'truth_id', 'noise_id', 'target_id', 'readout', 'stim', 'budget', 'design_repeat']
BOOLS = ['scale_valid', 'covered_95', 'optimizer_success', 'fallback']


def bool_value(value):
    if value in ('True', 'true', '1'): return True
    if value in ('False', 'false', '0'): return False
    raise ValueError('Invalid boolean: ' + repr(value))


def read_rows(path):
    with path.open(newline='') as f:
        rows = list(csv.DictReader(f))
    if not rows: raise ValueError('Empty results table')
    required = set(BASE_KEYS + FLOATS + INTS + BOOLS)
    if not required.issubset(rows[0]): raise ValueError('Missing fields: ' + str(required - set(rows[0])))
    for row in rows:
        for name in FLOATS: row[name] = float(row[name])
        for name in INTS: row[name] = int(row[name])
        for name in BOOLS: row[name] = bool_value(row[name])
        finite_required = [k for k in FLOATS if k not in ('normalized_squared_error', 'fit_objective')]
        if not all(np.isfinite(row[k]) for k in finite_required):
            raise ValueError('Nonfinite prediction/diagnostic; investigate rather than silently exclude')
        if not np.isfinite(row['fit_objective']) and not row['fallback']:
            raise ValueError('Nonfinite fit objective without a flagged fallback')
        if row['scale_valid'] != np.isfinite(row['normalized_squared_error']):
            raise ValueError('Scale-valid flag inconsistent with normalized error')
        if row['map_q_variance'] < 0: raise ValueError('Negative MAP predictive variance')
    return rows


def grouped(rows, names):
    groups = {}
    for row in rows: groups.setdefault(tuple(row[k] for k in names), []).append(row)
    return groups


def write_csv(path, rows):
    if not rows: return
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def clean_json(obj):
    if isinstance(obj, dict): return {k: clean_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)): return [clean_json(v) for v in obj]
    if isinstance(obj, (np.integer,)): return int(obj)
    if isinstance(obj, (np.floating, float)): return float(obj) if np.isfinite(obj) else None
    if isinstance(obj, np.ndarray): return clean_json(obj.tolist())
    return obj


def validate(rows, cfg, status, allow_partial):
    complete = bool(status.get('complete', False))
    if not complete and not allow_partial:
        raise ValueError('Run is incomplete. Use --allow-partial only for labelled exploratory output.')
    present = sorted(set(r['network_id'] for r in rows))
    planned = cfg['network_ids']
    if not set(present).issubset(planned): raise ValueError('Unexpected network IDs')
    if complete and present != sorted(planned): raise ValueError('Complete status but missing networks')
    if sorted(status.get('networks_completed', present)) != present:
        raise ValueError('Status/checkpoint disagreement: retry after a whole-network checkpoint')
    if status.get('evaluated_rows', len(rows)) != len(rows):
        raise ValueError('Status/results row-count mismatch; retry after checkpoint')
    expected = set(itertools.product(present, [c['name'] for c in cfg['conditions']],
                                    cfg['pools'], cfg['budgets'], cfg['methods']))
    groups = grouped(rows, BASE_KEYS)
    if set(groups) != expected: raise ValueError('Missing/unexpected complete network-stratum-method cells')
    for key, cell in groups.items():
        reps = cfg['random_sets'] if key[-1] == 'random' else 1
        expected_nested = set(itertools.product(range(cfg['truth_repeats']), range(cfg['noise_repeats']),
                                              range(cfg['targets']), range(reps)))
        observed = [(r['truth_id'], r['noise_id'], r['target_id'], r['design_repeat']) for r in cell]
        if len(set(observed)) != len(observed) or set(observed) != expected_nested:
            raise ValueError('Unbalanced/duplicate nested repeats in ' + repr(key))
    # The common nonlinear prior-MC scale cannot vary with method or observed truth/noise.
    for key, cell in grouped(rows, ['network_id', 'condition', 'target_id']).items():
        if len(set(r['prior_mc_variance'] for r in cell)) != 1:
            raise ValueError('Method-dependent task scale: ' + repr(key))
    return dict(complete=complete, partial=not complete, planned_networks=len(planned),
                evaluated_networks=len(present), network_ids=present,
                nested_balance_verified=True, common_task_scale_verified=True)


def network_metrics(rows, extra_keys=()):
    output = []
    for key, cell in sorted(grouped(rows, BASE_KEYS + list(extra_keys)).items()):
        item = dict(zip(BASE_KEYS + list(extra_keys), key))
        mean = lambda field: float(np.mean([r[field] for r in cell]))
        valid = all(r['scale_valid'] for r in cell)
        item.update(mse=mean('squared_error'), mae=mean('abs_error'),
                    normalized_mse=mean('normalized_squared_error') if valid else float('nan'),
                    scale_valid_fraction=mean('scale_valid'), passive_mse=mean('passive_mse'),
                    risk_nominal=mean('risk_nominal'), risk_ensemble=mean('risk_ensemble'),
                    map_q_variance=mean('map_q_variance'), coverage_95=mean('covered_95'),
                    mean_interval_width_95=float(np.mean([3.92 * np.sqrt(r['map_q_variance']) for r in cell])),
                    optimizer_failure_rate=1 - mean('optimizer_success'), fallback_rate=mean('fallback'),
                    fit_seconds_evaluation_weighted=mean('fit_seconds'), nfev_evaluation_weighted=mean('nfev'),
                    evaluated_rows=len(cell))
        output.append(item)
    return output


def ci(values, indices, level=0.95, transform=None):
    values = np.asarray(values, dtype=float)
    if not np.isfinite(values).all(): return [float('nan'), float('nan')]
    samples = values[indices].mean(axis=1)
    if transform is not None: samples = transform(samples)
    return np.quantile(samples, [(1-level)/2, 1-(1-level)/2]).tolist()


def estimate(records, cfg):
    summaries = []; effects = []; influence = []
    strata = grouped(records, ['condition', 'pool', 'budget'])
    for skey, cell in sorted(strata.items()):
        base = dict(zip(['condition', 'pool', 'budget'], skey))
        nets = sorted(set(r['network_id'] for r in cell))
        # Stable shared resamples for every method, metric and contrast in this stratum.
        indices = np.random.default_rng(BOOTSTRAP_SEED).integers(0, len(nets), (cfg['bootstrap_replicates'], len(nets)))
        lookup = {(r['network_id'], r['method']): r for r in cell}
        methods = [m for m in METHODS if (nets[0], m) in lookup]
        for method in methods:
            out = dict(base, method=method, networks=len(nets))
            out['normalized_mse_networks_evaluable'] = sum(np.isfinite(lookup[n, method]['normalized_mse']) for n in nets)
            for metric in ['mse', 'mae', 'normalized_mse', 'passive_mse', 'coverage_95',
                           'mean_interval_width_95', 'optimizer_failure_rate', 'fallback_rate',
                           'risk_nominal', 'risk_ensemble', 'map_q_variance', 'fit_seconds_evaluation_weighted']:
                vals = np.array([lookup[n, method][metric] for n in nets])
                out[metric] = float(vals.mean()); low, high = ci(vals, indices)
                out[metric+'_ci95_low'] = low; out[metric+'_ci95_high'] = high
            mses = np.array([lookup[n, method]['mse'] for n in nets])
            out['rmse'] = float(np.sqrt(mses.mean()))
            out['rmse_ci95_low'], out['rmse_ci95_high'] = ci(mses, indices, transform=np.sqrt)
            summaries.append(out)
        comparisons = [('ensemble_scalar', 'local_scalar'), ('ensemble_vector', 'local_vector'),
                       ('local_scalar', 'local_vector'), ('ensemble_scalar', 'ensemble_vector'),
                       ('ensemble_scalar', 'random'), ('ensemble_vector', 'random'),
                       ('local_scalar', 'local_activity')]
        primary_spec = cfg.get('primary_stratum') or {}
        primary_stratum = skey == (primary_spec.get('condition'),
                                  primary_spec.get('pool'),
                                  primary_spec.get('budget'))
        primary_pairs = [tuple(x) for x in cfg.get('primary_comparisons', [])]
        for a, b in comparisons:
            if a not in methods or b not in methods: continue
            for metric in ['mse', 'normalized_mse', 'mae', 'rmse', 'coverage_95', 'passive_mse']:
                source = 'mse' if metric == 'rmse' else metric
                va = np.array([lookup[n, a][source] for n in nets]); vb = np.array([lookup[n, b][source] for n in nets])
                primary = primary_stratum and (a, b) in primary_pairs and metric == 'mse'
                level = 0.975 if primary else 0.95
                finite = np.isfinite(va).all() and np.isfinite(vb).all()
                if finite:
                    if metric == 'rmse':
                        difference = float(np.sqrt(va.mean()) - np.sqrt(vb.mean()))
                        boots = np.sqrt(va[indices].mean(axis=1)) - np.sqrt(vb[indices].mean(axis=1))
                    else:
                        difference = float((va-vb).mean()); boots = (va-vb)[indices].mean(axis=1)
                    lower, upper = np.quantile(boots, [(1-level)/2, 1-(1-level)/2])
                else: difference = lower = upper = float('nan')
                relative = relative_low = relative_high = float('nan')
                if finite and metric == 'mse' and vb.mean() > 0:
                    denominator = vb[indices].mean(axis=1)
                    if np.all(denominator > 0):
                        relative = float(va.mean()/vb.mean()-1)
                        relative_low, relative_high = np.quantile(va[indices].mean(axis=1)/denominator-1,
                                                                  [(1-level)/2,1-(1-level)/2])
                effects.append(dict(base, contrast=a+' - '+b, metric=metric, effect=difference,
                                    ci_low=float(lower), ci_high=float(upper), confidence_level=level,
                                    primary=primary, networks=len(nets),
                                    relative_mse_difference=relative,
                                    relative_mse_ci_low=float(relative_low),relative_mse_ci_high=float(relative_high),
                                    interval='paired network-cluster percentile bootstrap',
                                    interpretation='negative favors first method for error metrics'))
                if metric == 'mse':
                    delta = va-vb
                    for j, net in enumerate(nets):
                        influence.append(dict(base, contrast=a+' - '+b, omitted_network_id=net,
                                              leave_one_out_mean=float(np.delete(delta,j).mean()) if len(nets)>1 else float('nan'),
                                              full_mean=difference, individual_paired_difference=float(delta[j])))
        if all(m in methods for m in METHODS[:4]):
            for metric in ['mse', 'normalized_mse']:
                delta = np.array([lookup[n, 'ensemble_scalar'][metric] - lookup[n, 'local_scalar'][metric]
                                  - lookup[n, 'ensemble_vector'][metric] + lookup[n, 'local_vector'][metric] for n in nets])
                lower, upper = ci(delta, indices)
                effects.append(dict(base, contrast='(ES - LS) - (EV - LV)', metric=metric,
                                    effect=float(delta.mean()), ci_low=lower, ci_high=upper,
                                    confidence_level=0.95, primary=False, networks=len(nets),
                                    relative_mse_difference=float('nan'),relative_mse_ci_low=float('nan'),relative_mse_ci_high=float('nan'),
                                    interval='paired network-cluster percentile bootstrap',
                                    interpretation='exploratory 2x2 interaction'))
    return summaries, effects, influence


def figure_config():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.titlesize': 10,
                         'axes.labelsize': 9, 'legend.fontsize': 8, 'pdf.fonttype': 42,
                         'ps.fonttype': 42, 'savefig.dpi': 300, 'axes.spines.top': False,
                         'axes.spines.right': False})


def save(fig, out, name):
    fig.savefig(out/(name+'.png'), dpi=300, bbox_inches='tight')
    fig.savefig(out/(name+'.pdf'), bbox_inches='tight')
    plt.close(fig)


def risk_figures(records, summaries, cfg, out, banner):
    strata = sorted(grouped(records, ['condition', 'pool', 'budget']))
    ncols = min(4, len(strata)); nrows = int(np.ceil(len(strata)/ncols))
    for metric, ylabel, name in [('mse', 'Response MSE (q units squared)', 'raw_risk'),
                                  ('normalized_mse', 'MSE / common prior-MC variance', 'normalized_risk')]:
        fig, axes = plt.subplots(nrows, ncols, figsize=(4*ncols, 3.2*nrows), squeeze=False)
        rng = np.random.default_rng(107)
        for ax, skey in zip(axes.flat, strata):
            cell = [r for r in records if (r['condition'],r['pool'],r['budget']) == skey]
            methods = [m for m in METHODS if any(r['method']==m for r in cell)]
            for i, method in enumerate(methods):
                vals = np.array([r[metric] for r in cell if r['method']==method])
                ax.scatter(i+rng.uniform(-.16,.16,len(vals)), vals, s=11, color=COLORS[method],
                           alpha=.55, marker=MARKERS[method], linewidths=.55)
                s = next(s for s in summaries if (s['condition'],s['pool'],s['budget'],s['method'])==(*skey,method))
                y=s[metric]; lo=s[metric+'_ci95_low']; hi=s[metric+'_ci95_high']
                if np.isfinite([y,lo,hi]).all():
                    ax.errorbar(i, y, yerr=np.array([[max(0,y-lo)],[max(0,hi-y)]]), fmt='_',
                                markersize=15, color='black', capsize=3, linewidth=1.3)
            labels=[]
            for m in methods:
                values=[r[metric] for r in cell if r['method']==m]
                missing=sum(not np.isfinite(v) for v in values)
                labels.append(LABELS[m]+(f' (NA={missing})' if missing else ''))
            ax.set_xticks(range(len(methods)), labels, rotation=35)
            ax.set_title(f'{skey[0]} | {skey[1]} | M={skey[2]}')
            ax.set_ylabel(ylabel); ax.set_ylim(bottom=0)
        for ax in list(axes.flat)[len(strata):]: ax.set_visible(False)
        title=('All network means retained\nBlack marks: mean and pointwise 95% cluster CI'
               '\nPanel y ranges differ; do not compare visual heights across panels')
        if metric=='normalized_mse':title+='\nNA-labelled networks have invalid task scales; full-cell mean/CI omitted if any NA'
        fig.suptitle((banner+'\n' if banner else '')+title,y=1.01,fontsize=10)
        fig.tight_layout(); save(fig,out,name)


def paired_figure(records, effects, cfg, out, banner):
    primary = cfg.get('primary_stratum') or dict(condition='broad',pool='exclude_endpoints',budget=3)
    cell = [r for r in records if all(r.get(k)==v for k,v in primary.items())]
    if not cell: return
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.8), squeeze=False)
    plot_data = []; rng = np.random.default_rng(108)
    for ax, (a,b) in zip(axes.flat, cfg.get('primary_comparisons', [METHODS[1::-1],METHODS[3:1:-1]])):
        lookup={(r['network_id'],r['method']):r for r in cell}
        nets=sorted(set(r['network_id'] for r in cell))
        vals=np.array([lookup[n,a]['mse']-lookup[n,b]['mse'] for n in nets])
        e=next(x for x in effects if all(x[k]==v for k,v in primary.items()) and x['contrast']==a+' - '+b and x['metric']=='mse')
        ax.scatter(rng.uniform(-.10,.10,len(vals)), vals, s=24, color=COLORS[a], alpha=.75)
        ax.errorbar(.35,e['effect'],yerr=[[max(0,e['effect']-e['ci_low'])],[max(0,e['ci_high']-e['effect'])]],
                    fmt='s', color='black',capsize=5,markersize=6)
        ax.axhline(0,color='#777777',linewidth=.9)
        ax.set_xticks([0,.35],['Paired networks',f'Mean, {100*e["confidence_level"]:g}% CI'])
        ax.set_title(LABELS[a]+' - '+LABELS[b]); ax.set_ylabel('Paired MSE difference (q units squared)')
        for n,d in zip(nets,vals): plot_data.append(dict(primary,contrast=a+' - '+b,network_id=n,paired_mse_difference=float(d)))
    pool_label='Endpoints excluded' if primary['pool']=='exclude_endpoints' else 'All recording sites eligible'
    title=('Primary response-prediction comparison\n'
           f'Condition: {primary["condition"]} | {pool_label} | M = {primary["budget"]}')
    fig.suptitle((banner+'\n' if banner else '')+title,fontsize=10,y=.985)
    network_count=len(set(r['network_id'] for r in cell))
    levels=sorted(set(e['confidence_level'] for e in effects if
                      all(e.get(k)==v for k,v in primary.items()) and e['metric']=='mse' and
                      any(e['contrast']==a+' - '+b for a,b in cfg.get('primary_comparisons',[]))))
    confidence='/'.join(f'{100*x:g}%' for x in levels)
    footer=(f'n = {network_count} independent networks; {cfg["truth_repeats"]} truths × '
            f'{cfg["noise_repeats"]} noise draws × {cfg["targets"]} readouts per network.\n'
            f'Dots: network MSE differences; black marks: mean and {confidence} paired network-cluster bootstrap CI.\n'
            'Negative values favor ensemble; all networks retained.')
    fig.text(.5,.015,footer,ha='center',va='bottom',fontsize=8)
    fig.tight_layout(rect=(0,.17,1,.82 if banner else .87))
    save(fig,out,'primary_paired_effects'); write_csv(out/'primary_paired_plot_data.csv',plot_data)


def calibration_figure(records, cfg, out, banner):
    primary=cfg.get('primary_stratum') or dict(condition='broad',pool='exclude_endpoints',budget=3)
    cell=[r for r in records if all(r.get(k)==v for k,v in primary.items())]
    if not cell:return []
    fig,axes=plt.subplots(1,2,figsize=(10,4.7)); diagnostics=[]; binned=[]
    for ax,risk in zip(axes,['risk_nominal','risk_ensemble']):
        all_values=[]
        for method in METHODS:
            data=[r for r in cell if r['method']==method]
            if not data:continue
            x=np.array([r[risk] for r in data]);y=np.array([r['mse'] for r in data])
            ax.scatter(x,y,s=22,alpha=.65,c=COLORS[method],marker=MARKERS[method],label=LABELS[method])
            rho=float(spearmanr(x,y).statistic) if len(x)>2 and np.ptp(x)>0 and np.ptp(y)>0 else float('nan')
            diagnostics.append(dict(primary,method=method,risk=risk,network_spearman_descriptive=rho,networks=len(data),
                                    mean_predicted_variance=float(x.mean()),mean_actual_mse=float(y.mean())))
            # Equal-count bins of whole-network points; no row-level independent inference.
            for bi,ids in enumerate(np.array_split(np.argsort(x,kind='stable'),min(4,len(x)))):
                binned.append(dict(primary,method=method,risk=risk,bin=bi,networks=len(ids),
                                   mean_predicted_variance=float(x[ids].mean()),mean_actual_mse=float(y[ids].mean())))
            all_values.extend(x.tolist()+y.tolist())
        upper=max(all_values)*1.03 if all_values else 1
        ax.plot([0,upper],[0,upper],color='#777777',linewidth=.8,linestyle='--',label='y = x')
        ax.set_xlim(0,upper);ax.set_ylim(0,upper)
        ax.set_xlabel(risk.replace('_',' ')+' (q units squared)');ax.set_ylabel('Actual network mean squared error')
        ax.set_title('Independent unit: connection matrix J');ax.legend(frameon=False,ncol=2)
    fig.suptitle((banner+'\n' if banner else '')+'Prior local risk versus held-out nonlinear error; primary stratum',fontsize=10)
    fig.tight_layout();save(fig,out,'risk_vs_actual_mse');write_csv(out/'risk_calibration_bins.csv',binned)
    return diagnostics


def distribution_figure(records,cfg,out,banner):
    primary=cfg.get('primary_stratum') or dict(condition='broad',pool='exclude_endpoints',budget=3)
    cell=[r for r in records if all(r.get(k)==v for k,v in primary.items())]
    if not cell:return
    fig,axes=plt.subplots(1,2,figsize=(10,4.5))
    for ax,metric in zip(axes,['mse','normalized_mse']):
        for method in METHODS:
            vals=np.sort([r[metric] for r in cell if r['method']==method])
            if not len(vals):continue
            total=len(vals);vals=vals[np.isfinite(vals)]
            if not len(vals):continue
            label=LABELS[method]+(f' ({len(vals)}/{total} finite)' if len(vals)!=total else '')
            ax.step(np.r_[0,vals],np.r_[0,np.arange(1,len(vals)+1)/len(vals)],where='post',
                    color=COLORS[method],label=label,linewidth=1.4)
        ax.set_xlabel('Network '+metric.replace('_',' '));ax.set_ylabel('Empirical cumulative proportion of networks')
        ax.set_xlim(left=0);ax.set_ylim(0,1.02)
        if ax.get_legend_handles_labels()[0]:ax.legend(frameon=False,ncol=2)
        else:ax.text(.5,.5,'No finite network values',ha='center',va='center',transform=ax.transAxes)
    fig.suptitle((banner+'\n' if banner else '')+
                 'Primary-stratum distributions; tails retained\nNormalized ECDF shows finite networks only (counts in legend); not a full-stratum estimate',fontsize=10)
    fig.tight_layout();save(fig,out,'network_risk_distributions')


def main(run,out,allow_partial=False):
    cfg=json.loads((run/'protocol.json').read_text());status=json.loads((run/'status.json').read_text())
    actual_digest=hashlib.sha256((run/'protocol.json').read_bytes()).hexdigest()
    if (run/'protocol.sha256').exists() and (run/'protocol.sha256').read_text().strip()!=actual_digest:
        raise ValueError('Frozen protocol hash mismatch')
    rows=read_rows(run/'results.csv');integrity=validate(rows,cfg,status,allow_partial)
    out.mkdir(parents=True,exist_ok=True)
    records=network_metrics(rows);summaries,effects,influence=estimate(records,cfg)
    eligible=integrity['complete'] and cfg.get('phase')=='frozen_holdout' and integrity['evaluated_networks']>1
    for effect in effects:effect['confirmatory_eligible']=eligible and effect['primary']
    write_csv(out/'network_metrics.csv',records);write_csv(out/'stratum_metrics.csv',summaries)
    write_csv(out/'paired_effects.csv',effects);write_csv(out/'leave_one_network_out.csv',influence)
    write_csv(out/'network_target_metrics.csv',network_metrics(rows,extra_keys=['target_id']))
    task_scales=[]
    for key,cell in sorted(grouped(rows,['network_id','condition','target_id']).items()):
        task_scales.append(dict(zip(['network_id','condition','target_id'],key),
                                prior_mc_variance=cell[0]['prior_mc_variance'],
                                scale_valid=cell[0]['scale_valid'],stim=cell[0]['stim'],readout=cell[0]['readout']))
    write_csv(out/'task_scales.csv',task_scales)
    banner='PARTIAL EXPLORATORY' if integrity['partial'] else ('' if eligible else 'EXPLORATORY / IMPLEMENTATION CHECK')
    figure_config();risk_figures(records,summaries,cfg,out,banner)
    paired_figure(records,effects,cfg,out,banner)
    diagnostics=calibration_figure(records,cfg,out,banner)
    write_csv(out/'risk_calibration_network_summary.csv',diagnostics)
    distribution_figure(records,cfg,out,banner)
    reported_primary=[e for e in effects if e['primary']]
    if not reported_primary:
        primary_interval_text='not applicable: no primary comparison specified; all reported contrast intervals exploratory 95%'
    elif eligible:
        primary_interval_text='97.5% paired network-cluster percentile CI; Bonferroni two-comparison family'
    else:
        primary_interval_text='reference comparisons use protocol-specified 97.5% paired cluster intervals; exploratory only, no confirmatory inference'
    available_figures=[name for name in ['raw_risk','normalized_risk','primary_paired_effects',
                                         'network_risk_distributions','risk_vs_actual_mse']
                       if (out/(name+'.png')).is_file() and (out/(name+'.pdf')).is_file()]
    summary=dict(integrity=integrity,phase=cfg.get('phase'),status='partial_exploratory' if integrity['partial'] else 'complete',
                 predeclared_primary_inference_eligible=eligible,
                 analysis=dict(independent_unit='connection matrix J',
                    within_network='equal means over the balanced truth, noise, target and random-design repeats',
                    bootstrap_replicates=cfg['bootstrap_replicates'],bootstrap_seed=BOOTSTRAP_SEED,
                    primary_metric='raw q mean squared error' if reported_primary else 'not applicable: no primary comparison specified',
                    primary_interval=primary_interval_text,
                    other_intervals='pointwise exploratory 95%; no p-values or equivalence claims',
                    rmse='sqrt(mean network MSE); CI recomputes this transformation for each cluster resample',
                    relative_mse='mean MSE(first)/mean MSE(second)-1, paired bootstrap ratio; not mean of network ratios',
                    failure_rates='evaluation-weighted within each network, not counts of independent optimizer calls',
                    normalization='common independent nonlinear prior-MC response variance; no method-specific denominator',
                    invalid_scale_policy='do not silently drop: normalized cell is NA if any scale is invalid',
                    calibration='descriptive whole-network averages, no row-level significance test',
                    partial_interpretation='No confirmation claim from an incomplete run, even for predeclared contrasts'),
                 primary_effects=reported_primary,
                 available_figures=available_figures,
                 metric_summaries=summaries,calibration_diagnostics=diagnostics,
                 raw_rows=len(rows),scale_invalid_rows=sum(not r['scale_valid'] for r in rows),
                 scale_invalid_network_condition_targets=sum(not r['scale_valid'] for r in task_scales),
                 actual_optimizer_calls=status.get('actual_optimizer_calls'),
                 cached_dataset_reuses=status.get('cached_dataset_reuses'),
                 experiment_elapsed_seconds=status.get('elapsed_seconds'),
                 protocol_sha256=hashlib.sha256((run/'protocol.json').read_bytes()).hexdigest(),
                 results_sha256=hashlib.sha256((run/'results.csv').read_bytes()).hexdigest(),
                 analysis_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 environment=dict(numpy=np.__version__,matplotlib=matplotlib.__version__),
                 provenance=dict(run=str(run.resolve()),command=f'python analyze.py --run {run} --out {out}'+(' --allow-partial' if allow_partial else '')))
    (out/'summary.json').write_text(json.dumps(clean_json(summary),indent=2,allow_nan=False))
    figure_notes=[]
    if 'raw_risk' in available_figures:
        figure_notes.append('`raw_risk`: response MSE in raw q units squared, all strata. Black marks are means and pointwise 95% network-cluster percentile intervals; colored points retain all network means and outliers. Panel y ranges differ; compare numerical axes rather than visual heights across panels.')
    if 'normalized_risk' in available_figures:
        figure_notes.append(f'`normalized_risk`: per-case squared error divided by the common independent nonlinear prior-MC variance. The variance floor remains {cfg["scale_floor"]}. A network metric is NA if any target is invalid; no valid-target substitution or floor change is made. A full-stratum standardized mean and interval are NA if any network is NA. Axis labels give missing-network counts. `task_scales.csv` lists all scale flags; {sum(not r["scale_valid"] for r in task_scales)} network-condition-target scales are invalid. Panel y ranges differ.')
    if 'primary_paired_effects' in available_figures:
        label='predeclared primary' if eligible else 'protocol reference (exploratory)'
        figure_notes.append(f'`primary_paired_effects`: one paired MSE difference per network in the {label} stratum; negative favors the first method. {primary_interval_text}. This figure does not upgrade development or partial results to confirmation.')
    if 'network_risk_distributions' in available_figures:
        figure_notes.append('`network_risk_distributions`: complete raw-risk ECDFs in the specified reference stratum, including tails. Standardized ECDFs show finite network metrics only, with retained/total counts in the legend. This conditional display does not replace a full-stratum estimate and is exploratory.')
    if 'risk_vs_actual_mse' in available_figures:
        figure_notes.append('`risk_vs_actual_mse`: nominal-point and ensemble-averaged local predictive variances against nonlinear actual MSE, aggregated within J; dashed y=x is a calibration reference. Correlations and risk bins are descriptive, not row-level significance tests.')
    data_notes=['`network_metrics.csv` supplies independent-unit metric summaries and risk-plot coordinates.']
    if (out/'primary_paired_plot_data.csv').is_file():
        data_notes.append('`primary_paired_plot_data.csv` contains the paired-dot coordinates.')
    for filename in ['risk_calibration_bins.csv','risk_calibration_network_summary.csv']:
        if (out/filename).is_file():data_notes.append(f'`{filename}` documents exploratory calibration summaries.')
    notes=f'''# Analysis and figure notes

Phase: `{cfg.get('phase')}`. Status: `{summary['status']}`. Independent connection matrices: {integrity['evaluated_networks']} of {integrity['planned_networks']} planned.

Each plotted point is one connection matrix J, after equal averaging of the balanced {cfg['truth_repeats']} truth draws, {cfg['noise_repeats']} noise draws, {cfg['targets']} prespecified targets and (for random designs) {cfg['random_sets']} design draws. These nested rows are not independent experimental units. All finite predictions, optimizer failures and fallback predictions are retained. Failure rates are evaluation-weighted summaries, not counts of independent optimizer calls.

Primary inference: {primary_interval_text}. Other contrast intervals are exploratory pointwise 95%. Bootstrap resamples {cfg['bootstrap_replicates']} whole networks with replacement (seed {BOOTSTRAP_SEED}); methods share resample indices within each stratum. Development, scale diagnostics, smoke checks and partial runs cannot supply confirmation claims. No p-values, equivalence conclusions or post-hoc sample expansion are computed.

Figures actually available in this directory: {', '.join('`'+name+'`' for name in available_figures)}.

{chr(10).join(chr(10)+paragraph for paragraph in figure_notes)}

{' '.join(data_notes)} RMSE is sqrt(mean network MSE); bootstrap recomputes this transformation. Relative MSE differences are ratios of aggregate mean MSEs minus one, not averages of per-network ratios. `leave_one_network_out.csv` reports influence without dropping influential networks. All designs use the same MAP fitting procedure. Coverage refers to a model-internal local Gaussian interval for a noiseless response, not a certified biological or clinical confidence interval. Figures are 300-dpi PNG plus vector PDF with embedded TrueType fonts, fixed method order/colors and shape coding.

Reproduce: `{summary['provenance']['command']}`.
'''
    (out/'figure_captions_and_analysis.md').write_text(notes)
    print(json.dumps(clean_json(dict(status=summary['status'],networks=integrity['evaluated_networks'],
                                    raw_rows=len(rows),primary_effects=summary['primary_effects'],out=str(out))),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--allow-partial',action='store_true')
    args=parser.parse_args();main(args.run,args.out,args.allow_partial)
