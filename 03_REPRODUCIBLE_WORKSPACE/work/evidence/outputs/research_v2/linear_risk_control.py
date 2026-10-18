"""Nondegenerate linear-Gaussian positive control, independent of experiment data.

Checks predictive risk against actual MAP error with the main design.choose.
No paired-stimulation cancellation is involved. This is a known exact identity,
not a new method, dataset or scientific finding. No formal result run is read.
"""
from pathlib import Path
import csv, hashlib, json, os, sys, time
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE/'linear_risk_control_results'
OUT.mkdir(parents=True,exist_ok=True)
sys.dont_write_bytecode=True
os.environ['NUMBA_CACHE_DIR']=str(OUT/'numba-cache')
os.environ['MPLCONFIGDIR']=str(OUT/'mpl-cache')
os.environ['XDG_CACHE_HOME']=str(OUT/'xdg-cache')
from design import choose
from threadpoolctl import threadpool_limits
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SYSTEMS,N,P,O,BUDGET,TARGETS,DRAWS,PARTICLES=12,12,24,5,3,3,8192,16
SEED=2026101617


def mm(a,b): return np.einsum('ik,kj->ij',a,b,optimize=False)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def save_csv(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def posterior_and_map(F,y):
    """Independent closed-form MAP; main inference module is not imported."""
    C=np.linalg.solve(np.eye(P)+mm(F.T,F),np.eye(P))
    theta_hat=mm(mm(y,F),C.T)
    return C,theta_hat


def main():
    start=time.perf_counter()
    rows,designs,checks=[],[],[]
    for sid in range(SYSTEMS):
        rng=np.random.default_rng(np.random.SeedSequence([SEED,sid,0]))
        F=rng.normal(size=(N,O,P))/np.sqrt(P)
        F*=np.exp(.35*rng.normal(size=N))[:,None,None]
        G=rng.normal(size=(TARGETS,P));G/=np.linalg.norm(G,axis=1,keepdims=True)
        info=np.einsum('nop,noq->npq',F,F)
        # Truth/noise are generated from an independent stream and never used
        # by selection. Full candidate-node noise is shared across designs.
        mc=np.random.default_rng(np.random.SeedSequence([SEED,sid,1]))
        theta=mc.normal(size=(DRAWS,P));noise=mc.normal(size=(DRAWS,N,O))
        q_true=mm(theta,G.T)
        rngcheck=[]
        for task in [0,1,2,-1]:
            W=(np.outer(G[task],G[task]) if task>=0 else mm(G.T,G)/TARGETS)
            local_nodes,local_path=choose(info[None],W[None],list(range(N)),BUDGET)
            ensemble_nodes,ensemble_path=choose(np.repeat(info[None],PARTICLES,axis=0),
                          np.repeat(W[None],PARTICLES,axis=0),list(range(N)),BUDGET)
            assert local_nodes==ensemble_nodes
            numerical_path_difference=float(np.max(np.abs(np.array(ensemble_path)-local_path)))
            assert numerical_path_difference<1e-12
            obs=F[local_nodes].reshape(BUDGET*O,P)
            y=mm(theta,obs.T)+noise[:,local_nodes,:].reshape(DRAWS,BUDGET*O)
            C,estimate=posterior_and_map(obs,y)
            # Explicitly recompute the ensemble's MAP using the independent
            # formula: identical selected inputs imply bitwise equal outputs.
            obs_e=F[ensemble_nodes].reshape(BUDGET*O,P)
            y_e=mm(theta,obs_e.T)+noise[:,ensemble_nodes,:].reshape(DRAWS,BUDGET*O)
            C_e,estimate_e=posterior_and_map(obs_e,y_e)
            assert np.array_equal(C,C_e) and np.array_equal(estimate,estimate_e)
            q_hat=mm(estimate,G.T);q_hat_e=mm(estimate_e,G.T)
            risk=np.einsum('tp,pq,tq->t',G,C,G,optimize=False)
            risk_e=np.einsum('tp,pq,tq->t',G,C_e,G,optimize=False)
            assert np.array_equal(risk,risk_e)
            errors=q_hat-q_true;errors_e=q_hat_e-q_true
            assert np.array_equal(errors,errors_e)
            # Error covariance identity is independently checked in parameter
            # space, including both prior variation and measurement noise.
            covariance=mm(C,C.T)+mm(mm(mm(C,obs.T),obs),C.T)
            covariance_error=float(np.max(np.abs(covariance-C)))
            assert covariance_error<1e-12
            assert np.all(np.isfinite(estimate)) and np.all(np.isfinite(errors))
            for target in range(TARGETS):
                mse=float(np.mean(errors[:,target]**2));mse_e=float(np.mean(errors_e[:,target]**2))
                variance=float(risk[target]);exact_se=np.sqrt(2/DRAWS)*variance
                z=(mse-variance)/exact_se
                assert variance>0 and abs(z)<5.5
                assert mse_e-mse==0. and float(risk_e[target]-risk[target])==0.
                rows.append(dict(system=sid,design_objective='scalar' if task>=0 else 'vector',
                    design_target=task,evaluation_target=target,
                    analytic_map_mse=variance,actual_mc_map_mse=mse,
                    exact_gaussian_mc_se=float(exact_se),standardized_mc_difference=float(z),
                    ensemble_minus_nominal_risk=float(risk_e[target]-risk[target]),
                    ensemble_minus_nominal_actual_mse=mse_e-mse,
                    selected_nodes=json.dumps(local_nodes)))
            designs.append(dict(system=sid,objective='scalar' if task>=0 else 'vector',target=task,
                local_nodes=local_nodes,ensemble_nodes=ensemble_nodes,identical_nodes=True,
                local_greedy_path=local_path,ensemble_greedy_path=ensemble_path,
                max_numerical_path_difference=numerical_path_difference,
                interpretation='Constant particles have identical mathematical costs; any path '
                               'difference is floating-point averaging residue, not improvement.'))
            rngcheck.append(covariance_error)
        checks.append(dict(system=sid,all_finite=True,
                    max_posterior_error_covariance_identity_defect=max(rngcheck)))
        if time.perf_counter()-start>55:raise RuntimeError('Incomplete: diagnostic time guard')
    save_csv('risk_vs_actual_mse.csv',rows)
    summary=[]
    for objective in ('scalar','vector'):
        group=[r for r in rows if r['design_objective']==objective]
        summary.append(dict(objective=objective,evaluations=len(group),
             mean_analytic_risk=float(np.mean([r['analytic_map_mse'] for r in group])),
             mean_actual_mc_mse=float(np.mean([r['actual_mc_map_mse'] for r in group])),
             max_abs_mc_standardized_difference=max(abs(r['standardized_mc_difference']) for r in group),
             ensemble_minus_nominal_risk=0.,ensemble_minus_nominal_actual_mse=0.))
    save_csv('summary.csv',summary)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axes=plt.subplots(1,2,figsize=(9.5,4.6))
    fig.subplots_adjust(left=.085,right=.985,bottom=.25,top=.85,wspace=.32)
    colors={'scalar':'#2166ac','vector':'#b35806'}
    for objective in ('scalar','vector'):
        group=[r for r in rows if r['design_objective']==objective]
        axes[0].scatter([r['analytic_map_mse'] for r in group],[r['actual_mc_map_mse'] for r in group],
                         s=20,alpha=.65,color=colors[objective],label=objective+' design')
    bounds=[min(r['analytic_map_mse'] for r in rows)*.9,max(r['analytic_map_mse'] for r in rows)*1.08]
    axes[0].plot(bounds,bounds,color='black',lw=1,ls='--',label='Exact equality')
    axes[0].set(xlabel='Analytic predictive risk: aᵀCa',ylabel='Actual MAP response MSE (Monte Carlo)',
                title='A  Nonzero target uncertainty is calibrated',xlim=bounds,ylim=bounds)
    axes[0].legend(frameon=False,fontsize=8)
    for objective,offset in [('scalar',-.08),('vector',.08)]:
        values=[]
        for sid in range(SYSTEMS):
            group=[r for r in rows if r['system']==sid and r['design_objective']==objective]
            values.append(np.mean([r['ensemble_minus_nominal_risk'] for r in group]))
        axes[1].scatter(np.arange(SYSTEMS)+offset,values,color=colors[objective],marker='o' if objective=='scalar' else 's',s=25,label=objective+' design')
    axes[1].axhline(0,color='black',lw=1,ls='--')
    axes[1].set(xlabel='Independent linear observation system',ylabel='Ensemble − nominal predictive risk',
                title='B  Constant derivatives give exactly zero gain',ylim=(-.01,.01),xticks=[0,3,6,9,11])
    axes[1].legend(frameon=False,fontsize=8)
    fig.suptitle('Linear-Gaussian positive control: predictive risk → actual MAP error',fontsize=12)
    fig.text(.085,.035,'12 independent systems; 24 parameters; 12 candidate nodes × 5 observations; budget 3; 3 linear targets.\n'
             'Each system uses 8,192 full prior truths and Gaussian-noise realizations. The two design criteria share identical F and G.\n'
             'Known mathematical control, not new data or a new finding. No paired-stimulation cancellation and no formal-result files.',fontsize=8)
    for ext in ('png','pdf'):fig.savefig(OUT/f'linear_risk_control.{ext}',dpi=220)
    plt.close(fig)
    report=dict(scope='Known, nondegenerate linear-Gaussian positive control only; no formal-result data are read.',
          protocol=dict(systems=SYSTEMS,candidate_nodes=N,parameters=P,observations_per_node=O,
                        budget=BUDGET,linear_targets=TARGETS,monte_carlo_draws=DRAWS,constant_particles=PARTICLES,
                        seed=SEED,prior='Normal(0,I)',observation_noise='Normal(0,I), already whitened',
                        source_F='iid Normal/sqrt(24), multiplied by independent log-normal node scale exp(.35 Normal)',
                        source_G='iid Normal row-normalized to unit target prior variance',
                        selection='Main design.choose, separately for nominal and 16 repeated constant particles',
                        MAP='C=(I+F_S.T F_S)^-1; theta_hat=C F_S.T y',
                        exact_risk='a.T C a; nonzero because prior/noise uncertainty remain',
                        exact_mc_se='sqrt(2/8192) * a.T C a',
                        acceptance='Every target/system/design: absolute MC discrepancy < 5.5 exact Gaussian MC SE',
                        inference_unit='12 systems; targets, objectives and MC draws are nested, not independent systems'),
          source_hashes={'design.py':sha(HERE/'design.py'),'linear_risk_control.py':sha(Path(__file__))},
          checks=checks,designs=designs,summary=summary,
          all_48_designs_match=True,all_fixed_set_risk_differences_exactly_zero=True,
          all_actual_mse_differences_exactly_zero=True,
          max_numerical_greedy_path_difference=max(d['max_numerical_path_difference'] for d in designs),
          maximum_absolute_mc_standardized_difference=max(abs(r['standardized_mc_difference']) for r in rows),
          mathematical_note='Final fixed-set E−N risks and actual paired MAP MSEs are exactly zero. '
               'A main-choose greedy-path difference of machine precision can arise when averaging 16 '
               'identical floating-point entries; it is explicitly retained and never interpreted as an effect.',
          wall_seconds=time.perf_counter()-start)
    (OUT/'report.json').write_text(json.dumps(report,indent=2))
    (OUT/'README.md').write_text('''# Nondegenerate linear-Gaussian positive control

This is a scientific positive control of the exact predictive-risk-to-MAP-MSE relation. It is a known identity, not new data, an empirical discovery, or an algorithm. Unlike the paired-stimulation additive-bias cancellation null, these linear targets have strictly positive uncertainty and nonzero MAP error.

There are 12 fixed-seed random observation systems, each with 24 parameters, 12 candidate recording nodes, five observations per node, budget three, and three linear targets. Prior and whitened noise are independent standard Gaussians. Three scalar-target and one vector-target selection are run through the unchanged main design.choose function. F/G are constant across parameters, so nominal and 16-particle ensemble designs have identical mathematical objectives; selected IDs must match. Final fixed-set E−N risk and paired actual MSE must be exactly zero. Any machine-precision difference in the numerical greedy cost paths is recorded separately, rather than called an effect.

For each system, a separate stream supplies 8,192 complete parameter truths and full candidate-node noise arrays. These are shared across selection objectives for paired comparison and never used for selection. MAP is independently implemented as (I+F_S.T F_S)^-1 F_S.T y. For each target a, analytic error is a.T C a; independent truth/noise Monte Carlo error is computed from actual MAP predictions. The exact standard error of its Monte Carlo mean squared error is sqrt(2/8192) times the analytic risk. Every cell must fall within the predeclared 5.5-SE bound; no cells are filtered or tuned. The parameter-error covariance identity C²+C F_S.T F_S C=C is also checked.

No formal experimental results or held-out data are read. No packages are installed, no algorithms or existing files are changed. Products use einsum, avoiding platform matmul warning behavior. All outputs must be finite. CSVs contain all 144 target/system/design evaluations. JSON contains protocol, IDs, source hashes, greedy paths, numerical residuals and runtime. PNG and vector PDF show risk/MSE agreement and exactly zero ensemble-minus-nominal fixed-set risk.

Run from workspace root:
```sh
work/research-v2-env/bin/python work/research_v2/linear_risk_control.py
```
''')
    print(json.dumps(dict(seconds=report['wall_seconds'],max_mc_z=report['maximum_absolute_mc_standardized_difference'],
        max_path_difference=report['max_numerical_greedy_path_difference'],summary=summary),indent=2))


if __name__=='__main__':
    with threadpool_limits(limits=2):main()
