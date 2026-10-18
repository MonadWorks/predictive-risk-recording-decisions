"""Development-only mechanism diagnostics; never loads a held-out run.

No selection, protocol, model or fitted result is modified. Frozen source is
imported verbatim. These are direct nonlinearity and selection diagnostics,
not evidence that correlations are causal or that a new method was invented.
"""
from pathlib import Path
import sys, os, json, csv, hashlib, time
import numpy as np

HERE = Path(__file__).resolve().parent
RUN = HERE/'development_run'
OUT = HERE/'mechanism_results'
OUT.mkdir(parents=True, exist_ok=True)
os.environ['NUMBA_CACHE_DIR'] = str(OUT/'numba-cache')
os.environ['MPLCONFIGDIR'] = str(OUT/'mpl-cache')
os.environ['XDG_CACHE_HOME'] = str(OUT/'xdg-cache')
sys.dont_write_bytecode = True
sys.path.insert(0, str(RUN/'source_snapshot'))
from models import public_case, generate_truth
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from threadpoolctl import threadpool_limits


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def write_csv(name, records):
    with (OUT/name).open('w', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader(); writer.writerows(records)


def average(values):
    values=[v for v in values if v is not None and np.isfinite(v)]
    return float(np.mean(values)) if values else None


def stats(values):
    values=[v for v in values if v is not None and np.isfinite(v)]
    return dict(mean=float(np.mean(values)) if values else None,
                sem=float(np.std(values,ddof=1)/np.sqrt(len(values))) if len(values)>1 else None,
                networks_available=len(values))


def main():
    start=time.perf_counter()
    cfg=json.loads((RUN/'protocol.json').read_text())
    assert cfg['phase']=='development'
    frozen_hashes=json.loads((RUN/'source_hashes.json').read_text())
    for name,digest in frozen_hashes.items():
        assert sha(RUN/'source_snapshot'/name)==digest
    assert sha(RUN/'protocol.json')==(RUN/'protocol.sha256').read_text().strip()
    receipts=json.loads((RUN/'models.json').read_text())
    receipts={(r['network_id'],r['condition']):r for r in receipts}
    # Check reconstructed truth Q against archived experiment values.
    archived={}
    with (RUN/'results.csv').open() as f:
        for r in csv.DictReader(f):
            key=(int(r['network_id']),r['condition'],int(r['truth_id']),int(r['target_id']))
            q=float(r['q_true'])
            if key in archived: assert archived[key]==q
            archived[key]=q
    qrows, arows, checks=[],[],[]
    for nid in cfg['network_ids']:
        for condition in cfg['conditions']:
            name=condition['name'];case=public_case(nid,cfg,condition);model=case['model']
            receipt=receipts[nid,name]
            assert case['stim']==receipt['stim']
            assert case['readouts'].tolist()==receipt['readouts']
            mu=case['mu']
            q0,g=model.responses(mu,case['intervention'],True)
            r0,d=model.simulate(mu,case['train'],True)
            r0=r0[:,::cfg['sample_stride']];d=d[:,::cfg['sample_stride']]
            for truth_id in range(cfg['truth_repeats']):
                theta=generate_truth(case,cfg,condition,truth_id);delta=theta-mu
                qtrue,_=model.responses(theta,case['intervention'])
                rtrue,_=model.simulate(theta,case['train']);rtrue=rtrue[:,::cfg['sample_stride']]
                rlinear=r0+np.einsum('ktnp,p->ktn',d,delta)
                rremain=rtrue-rlinear;actual_change=rtrue-r0
                remainder_norm=float(np.linalg.norm(rremain))
                change_norm=float(np.linalg.norm(actual_change))
                relative=remainder_norm/change_norm if change_norm>0 else None
                arows.append(dict(network_id=nid,condition=name,truth_id=truth_id,
                    calibration_remainder_norm=remainder_norm,
                    calibration_parameter_change_norm=change_norm,
                    relative_calibration_remainder=relative,
                    relative_denominator_valid=change_norm>0,
                    calibration_remainder_rmse=float(np.sqrt(np.mean(rremain**2))),
                    active_parameter_distance=float(np.linalg.norm(delta))))
                for tid,node in enumerate(case['readouts']):
                    linear_increment=float(np.dot(g[node],delta))
                    remain=float(qtrue[node]-q0[node]-linear_increment)
                    variance=float(receipt['prior_q_variance'][tid])
                    valid=bool(variance>cfg['scale_floor'])
                    sigma=float(np.sqrt(variance)) if valid else None
                    archive_error=float(abs(qtrue[node]-archived[nid,name,truth_id,tid]))
                    assert np.isclose(qtrue[node],archived[nid,name,truth_id,tid],rtol=1e-12,atol=1e-14)
                    qrows.append(dict(network_id=nid,condition=name,truth_id=truth_id,
                        target_id=tid,readout=int(node),stim=case['stim'],q_true=float(qtrue[node]),
                        q_nominal=float(q0[node]),linear_increment=linear_increment,
                        archive_q_absolute_difference=archive_error,
                        q_taylor_remainder=remain,abs_q_taylor_remainder=abs(remain),
                        squared_q_taylor_remainder=remain**2,
                        prior_mc_variance=variance,scale_floor=cfg['scale_floor'],
                        scale_valid=valid,common_prior_mc_sigma=sigma,
                        standardized_q_remainder=remain/sigma if valid else None,
                        squared_standardized_q_remainder=(remain/sigma)**2 if valid else None))
            checks.append(dict(network_id=nid,condition=name,archived_Q_matches=True,
                               stim_and_readouts_match=True))
        if time.perf_counter()-start>110: raise RuntimeError('120-second diagnostic budget exceeded')
    designs=json.loads((RUN/'designs.json').read_text())
    look={(d['network_id'],d['condition'],d['pool'],d['budget'],d['method'],d['target']):d for d in designs if d['method']!='random'}
    jrows, inclusion=[],[]
    for d in designs:
        if d['method'] not in ('local_scalar','local_vector','ensemble_scalar','ensemble_vector'):continue
        nid,name=d['network_id'],d['condition'];receipt=receipts[nid,name];chosen=set(d['nodes'])
        readouts=receipt['readouts'];target=d['target']
        if d['pool']=='all':
            fraction=(float(readouts[target] in chosen) if target>=0 else
                      float(np.mean([node in chosen for node in readouts])))
            inclusion.append(dict(network_id=nid,condition=name,budget=d['budget'],
                method=d['method'],target_id=target,
                target_readout_inclusion_fraction=fraction,
                any_readout_included=bool(set(readouts)&chosen),
                stimulus_included=receipt['stim'] in chosen))
        if not d['method'].startswith('local_'):continue
        family=d['method'].split('_',1)[1]
        other=look[nid,name,d['pool'],d['budget'],'ensemble_'+family,target]
        othernodes=set(other['nodes']);union=chosen|othernodes
        jrows.append(dict(network_id=nid,condition=name,pool=d['pool'],budget=d['budget'],
            family=family,target_id=target,jaccard=len(chosen&othernodes)/len(union),
            identical_set=chosen==othernodes,local_nodes=json.dumps(d['nodes']),
            ensemble_nodes=json.dumps(other['nodes'])))
    write_csv('q_taylor_remainders.csv',qrows)
    write_csv('calibration_taylor_remainders.csv',arows)
    write_csv('selection_jaccard.csv',jrows)
    write_csv('all_pool_readout_inclusion.csv',inclusion)
    names=[c['name'] for c in cfg['conditions']]
    nrows=[]
    for nid in cfg['network_ids']:
      for name in names:
        q=[r for r in qrows if r['network_id']==nid and r['condition']==name]
        a=[r for r in arows if r['network_id']==nid and r['condition']==name]
        normalized=average([r['squared_standardized_q_remainder'] for r in q])
        row=dict(network_id=nid,condition=name,
            raw_q_remainder_rms=float(np.sqrt(average([r['squared_q_taylor_remainder'] for r in q]))),
            standardized_q_remainder_rms=float(np.sqrt(normalized)) if normalized is not None else None,
            valid_scale_targets=sum(r['scale_valid'] for r in q)//cfg['truth_repeats'],
            total_targets=cfg['targets'],
            calibration_relative_remainder=average([r['relative_calibration_remainder'] for r in a]))
        for pool in cfg['pools']:
          for family in ('scalar','vector'):
            row[f'jaccard_{pool}_{family}']=average([r['jaccard'] for r in jrows if r['network_id']==nid and r['condition']==name and r['pool']==pool and r['family']==family])
        for method in ('local_scalar','ensemble_scalar','local_vector','ensemble_vector'):
            row[f'inclusion_{method}']=average([r['target_readout_inclusion_fraction'] for r in inclusion if r['network_id']==nid and r['condition']==name and r['method']==method])
        nrows.append(row)
    write_csv('network_level_diagnostics.csv',nrows)
    summary=[]
    metrics=[k for k in nrows[0] if k not in ('network_id','condition','valid_scale_targets','total_targets')]
    for name in names:
        for metric in metrics:
            sub=[r for r in nrows if r['condition']==name]
            summary.append(dict(condition=name,metric=metric,**stats([r[metric] for r in sub])))
    write_csv('condition_summary.csv',summary)
    labels=['Matched','Broad','Bias shift','Gain only','Bias only']
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axes=plt.subplots(2,3,figsize=(12.5,7.1))
    fig.subplots_adjust(left=.065,right=.985,top=.91,bottom=.17,wspace=.32,hspace=.43)
    for ax,metric,title in zip(axes[0],metrics[:3],['A  Response Taylor remainder (raw)','B  Response remainder / prior-MC sigma','C  Calibration relative Taylor remainder']):
        for x,name in enumerate(names):
            values=[r[metric] for r in nrows if r['condition']==name and r[metric] is not None]
            ax.scatter(x+np.linspace(-.13,.13,len(values)),values,s=20,color='#2166ac',alpha=.7)
            if values:ax.plot([x-.19,x+.19],[np.mean(values)]*2,color='black',lw=2)
            else:ax.text(x,.05,'NA',ha='center',transform=ax.get_xaxis_transform())
        ax.set_title(title,loc='left',fontsize=10)
        ax.set_xticks(range(5),labels,rotation=25,ha='right')
    # Use a log axis only if every available RMS is strictly positive; never
    # replace zero, omit it, or add an undocumented plotting pseudocount.
    for ax,metric in zip(axes[0,:2],metrics[:2]):
        available=[r[metric] for r in nrows if r[metric] is not None]
        if available and min(available)>0:ax.set_yscale('log')
    axes[0,0].set_ylabel('RMS of integrated-rate response remainder')
    axes[0,1].set_ylabel('RMS across valid-scaled readouts only')
    axes[0,2].set_ylabel('||r(true) − r(linear)|| / ||r(true) − r(mu)||')
    for ax,pool,title in zip(axes[1,:2],cfg['pools'],['D  Local–ensemble overlap: all pool','E  Local–ensemble overlap: endpoints excluded']):
        for family,color,offset in [('scalar','#2166ac',-.1),('vector','#b35806',.1)]:
            data=[next(r for r in summary if r['condition']==name and r['metric']==f'jaccard_{pool}_{family}') for name in names]
            ax.errorbar(np.arange(5)+offset,[r['mean'] for r in data],yerr=[r['sem'] for r in data],color=color,marker='o',lw=1,capsize=2,label=family)
        ax.set(title=title,ylabel='Set Jaccard, averaged within network',ylim=(-.03,1.03))
        ax.set_xticks(range(5),labels,rotation=25,ha='right');ax.legend(frameon=False,fontsize=8)
    ax=axes[1,2]
    for method,color,marker in [('local_scalar','#2166ac','o'),('ensemble_scalar','#2166ac','s'),('local_vector','#b35806','o'),('ensemble_vector','#b35806','s')]:
        data=[next(r for r in summary if r['condition']==name and r['metric']=='inclusion_'+method) for name in names]
        ax.plot(range(5),[r['mean'] for r in data],color=color,marker=marker,lw=1,label=method.replace('_',' '))
    ax.set(title='F  Direct readout inclusion: all pool',ylabel='Target-readout inclusion fraction',ylim=(-.03,1.03))
    ax.set_xticks(range(5),labels,rotation=25,ha='right');ax.legend(frameon=False,fontsize=7)
    fig.suptitle('Development-only diagnostics: nonlinearity and recording-set stability',fontsize=13)
    fig.text(.065,.035,'Dots in A–C: independent networks (n = 8); black ticks: network mean. D–E: mean ±1 network SEM.\n'
             'Truth, target and budget repetitions are nested. Invalid prior-MC scales remain NA; B summarizes available targets only.\n'
             'These diagnostics do not establish causality, a biological mechanism or a new design method. No held-out files were read.',fontsize=8)
    for ext in ('png','pdf'):fig.savefig(OUT/f'mechanism_diagnostics.{ext}',dpi=220)
    plt.close(fig)
    validity={name:{'valid_unique_targets':sum(r['scale_valid'] for r in qrows if r['condition']==name)//cfg['truth_repeats'],
                    'total_unique_targets':len(cfg['network_ids'])*cfg['targets']} for name in names}
    report=dict(scope='Exploratory development-only direct nonlinearity / working-point and selection stability diagnostics. '
                'No causal, biological-mechanism or new-method claim.',
        input_directory=str(RUN),input_files={f:sha(RUN/f) for f in ['protocol.json','models.json','designs.json','results.csv']},
        frozen_source_hashes=frozen_hashes,script_sha256=sha(Path(__file__)),
        formula_q='q(theta_true) - q(mu) - grad_q(mu)^T (theta_true-mu)',
        formula_activity='||r(theta_true)-r(mu)-D_r(mu)(theta_true-mu)|| / ||r(theta_true)-r(mu)||; noiseless sampled calibration rates',
        scales='Archived common independent nonlinear prior-MC variance, with exact original floor. Invalid entries retained as blank CSV / null JSON.',
        selection='Jaccard compares local vs ensemble same objective/target/budget/pool. Scalar inclusion refers to its own target; vector inclusion is fraction of three targets.',
        aggregation='Average nested repeats within each network first. Raw Q diagnostic is RMS; normalized RMS uses valid-scaled targets only and is not the same population if validity varies.',
        invalid_scale_policy='No case is dropped from raw diagnostics. Standardized fields are NA below protocol scale_floor.',
        validity=validity,reconstruction_checks=checks,
        maximum_archived_q_absolute_difference=max(r['archive_q_absolute_difference'] for r in qrows),
        condition_summary=summary,
        wall_seconds=time.perf_counter()-start)
    (OUT/'report.json').write_text(json.dumps(report,indent=2))
    (OUT/'README.md').write_text('''# Development-only mechanism diagnostics

Only development_run is read. Its frozen model snapshot, protocol, model receipts, designs and Q truths are hash-verified or cross-checked. No holdout data, model optimization or protocol changes are involved. All conditions, networks, truths and three readouts remain in raw tables; no error-based filtering is performed.

The signed Q Taylor remainder is q(true)-q(mu)-grad q(mu)^T(true-mu). It is recorded in raw integrated-rate units and divided by the same archived independent prior-MC sigma used in the experiment. The original variance floor is retained. Invalid scales are empty CSV fields and null JSON, not zero. Their counts are reported; normalized summaries use available scaled targets, so cannot silently represent all targets.

The calibration diagnostic is the norm of the sampled-rate first-order prediction remainder divided by the norm of the actual parameter-induced change. This uses noiseless teacher signals, the same calibrated trials and sample stride, and the nominal model gradient. It is not fitted error or measurement noise. A zero change denominator is NA.

Jaccard compares recording sets from local versus ensemble criteria within the same scalar/vector objective, pool, budget, and scalar target. Direct target inclusion is evaluated in the all pool: scalar refers to its own readout; vector reports the fraction of the three readouts included. Nested target/truth/budget repeats are averaged within J before network-level summaries; networks, not repetitions, are the independent unit. SD/SEM do not certify an effect.

These are descriptive tests of nonlinear approximation and recording-set stability, not causal mechanism attribution, biological validation or method innovation. Raw data and missingness must accompany any interpretation. All source and input hashes are in report.json. Runtime and figure versions are recorded by the outputs. Figure has been generated as both PNG and vector PDF.

Run from workspace root:
```sh
work/research-v2-env/bin/python work/research_v2/mechanism.py
```
No packages are installed. Python bytecode writes are disabled and Numba/plot/font caches are redirected under this result directory; the frozen experiment is unchanged.
''')
    print(json.dumps({'seconds':report['wall_seconds'],'validity':validity,'condition_summary':summary},indent=2))


if __name__=='__main__':
    with threadpool_limits(limits=2):main()
