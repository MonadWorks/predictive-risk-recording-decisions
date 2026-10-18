"""Exploratory, dimensionless synthetic-network feasibility study.

Independent implementation of a softplus rate-model family motivated by
Beiran & Litwin-Kumar (2025), not a reproduction of their figures or data.
Observation criteria use established local Gaussian goal/V/A-optimal design.
No experimental biological data and no novelty claim. See frozen protocol.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, platform, time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.special import expit
from threadpoolctl import threadpool_limits, threadpool_info


def simulate(theta, J, U, dt, sensitivity=False, linear=False):
    """x'= -x + J rate(x,theta) + u; known x0=0, Euler integration.

    Nonlinear rate_i = exp(log_gain_i) softplus(x_i+bias_i).
    Strict linear null: rate=x+bias, known J, only bias unknown.
    U has independent trials x time x neuron; time is dimensionless.
    """
    K, T, N = U.shape
    P = len(theta)
    x = np.zeros((K, N))
    S = np.zeros((K, N, P))
    R = np.empty((K, T, N))
    D = np.empty((K, T, N, P)) if sensitivity else None
    eye = np.eye(N)
    g = np.ones(N) if linear else np.exp(theta[:N])
    b = theta if linear else theta[N:]
    for t in range(T):
        z = x + b
        r = z if linear else g * np.logaddexp(0., z)
        R[:, t] = r
        if sensitivity:
            if linear:
                dr = S + eye[None]
            else:
                slope = g * expit(z)
                dr = slope[:, :, None] * S
                dr[:, :, :N] += r[:, :, None] * eye[None]
                dr[:, :, N:] += slope[:, :, None] * eye[None]
            D[:, t] = dr
            S += dt * (-S + np.einsum('ij,kjp->kip', J, dr))
        x += dt * (-x + r @ J.T + U[:, t])
    return R, D


def make_case(seed, cfg):
    rng = np.random.default_rng(seed)
    N, dt, T = cfg['neurons'], cfg['dt'], cfg['steps']
    signs = np.ones(N)
    signs[-max(1, N // 5):] = -1
    J = np.abs(rng.normal(size=(N, N))) * (rng.random((N, N)) < .3)
    np.fill_diagonal(J, 0.)
    J *= signs[None, :]
    J *= cfg['connectivity_norm'] / max(np.linalg.norm(J, 2), 1e-12)
    tt = np.arange(T) * dt
    train = np.zeros((2, T, N))
    passive_test = np.zeros_like(train)
    channels = rng.choice(N, size=3, replace=False)
    for k in range(2):
        for j, node in enumerate(channels):
            train[k, :, node] = .4 * np.sin((.6 + .3*j)*tt + k*.7)
            passive_test[k, :, node] = .4 * np.sin((.9 + .2*j)*tt + k*.4 + 1.3)
    stim, readout = map(int, rng.choice(N, size=2, replace=False))
    # Pair defined before seeing truth/response; all pairs retained.
    intervention = np.zeros((2, T, N))
    intervention[1, (tt >= 1.) & (tt < 2.), stim] = .6
    shuffled = np.zeros_like(intervention)
    shuffled[1, (tt >= 1.) & (tt < 2.), (stim + 1) % N] = .6
    shuffled_readout = (readout + 1) % N
    theta0 = np.zeros(2*N)
    sd = np.r_[np.full(N, cfg['log_gain_sd']), np.full(N, cfg['bias_sd'])]
    truth = rng.normal(size=2*N) * sd
    return dict(J=J, train=train, passive_test=passive_test,
                intervention=intervention, shuffled=shuffled, stim=stim,
                readout=readout, shuffled_readout=shuffled_readout,
                theta0=theta0, sd=sd, truth=truth)


def response(theta, J, U, readout, dt, sensitivity=False):
    R, D = simulate(theta, J, U, dt, sensitivity)
    q = float(dt * np.sum(R[1, :, readout] - R[0, :, readout]))
    grad = None if D is None else dt * np.sum(D[1, :, readout] - D[0, :, readout], axis=0)
    return q, grad


def prospective_design(case, cfg, budget, pool):
    """This function never reads case['truth'] or observed/test outcomes."""
    J, theta0, sd = case['J'], case['theta0'], case['sd']
    _, D = simulate(theta0, J, case['train'], cfg['dt'], True)
    D = D[:, ::cfg['sample_stride']]
    H0 = np.diag(1/sd**2)
    # Explicit contraction avoids a platform BLAS floating-status warning;
    # no warnings are suppressed and all information matrices are finite.
    gram = lambda F: np.einsum('ki,kj->ij', F, F)
    info = {i: gram(D[:, :, i].reshape(-1, len(sd))) / cfg['noise_sd']**2 for i in pool}
    flat = D.reshape(-1, len(sd))
    B = gram(flat) / flat.shape[0]
    _, Di = simulate(theta0, J, case['intervention'], cfg['dt'], True)
    Fi = Di.reshape(-1, len(sd))
    # Same target inputs/window; stronger baseline reconstructs the complete
    # vector of integrated stimulus-minus-baseline responses, of which q is one.
    Gresponse = cfg['dt'] * np.sum(Di[1]-Di[0], axis=0)
    _, goal = response(theta0, J, case['intervention'], case['readout'], cfg['dt'], True)
    _, wrong = response(theta0, J, case['shuffled'], case['shuffled_readout'], cfg['dt'], True)
    matrices = {'activity': B, 'stimulus_state': gram(Fi)/len(Fi),
                'response_state': gram(Gresponse)/len(Gresponse), 'goal': np.outer(goal, goal),
                'shuffled_goal': np.outer(wrong, wrong), 'parameter': np.eye(len(sd))}
    assert all(np.isfinite(v).all() for v in [*info.values(), *matrices.values()])
    result = {}
    for method, W in matrices.items():
        H = H0.copy()
        selected = []
        for _ in range(budget):
            options = [(float(np.trace(np.linalg.solve(H + info[i], W))), i)
                       for i in pool if i not in selected]
            _, i = min(options)
            selected.append(i)
            H += info[i]
        C = np.linalg.inv(H)
        result[method] = dict(nodes=selected, predicted_q_variance=float(goal@C@goal))
    return result, float(np.sum((goal*sd)**2))


def fit_map(case, cfg, selected, observed):
    J, sd, theta0 = case['J'], case['sd'], case['theta0']
    saved = {}
    def evaluate(theta):
        key = theta.tobytes()
        if saved.get('key') != key:
            R, D = simulate(theta, J, case['train'], cfg['dt'], True)
            pred = R[:, ::cfg['sample_stride'], selected]
            jac = D[:, ::cfg['sample_stride'], selected, :]
            saved.update(key=key,
                residual=np.r_[((pred-observed)/cfg['noise_sd']).ravel(), theta/sd],
                jacobian=np.vstack([jac.reshape(-1, len(theta))/cfg['noise_sd'], np.diag(1/sd)]))
        return saved
    fit = least_squares(lambda x: evaluate(x)['residual'], theta0,
                        jac=lambda x: evaluate(x)['jacobian'],
                        max_nfev=cfg['max_nfev'], xtol=1e-7, ftol=1e-7, gtol=1e-7)
    qhat, grad = response(fit.x, J, case['intervention'], case['readout'], cfg['dt'], True)
    H = np.einsum('ki,kj->ij', fit.jac, fit.jac)
    qvar = float(grad @ np.linalg.solve(H, grad))
    qwrong, _ = response(fit.x, J, case['shuffled'], case['shuffled_readout'], cfg['dt'])
    return fit, qhat, max(qvar, 0.), qwrong


def checks(cfg):
    c = make_case(17, cfg)
    th = c['truth']; J = c['J']; dt = cfg['dt']
    R, D = simulate(th, J, c['train'], dt, True)
    h = 1e-5
    fd = np.empty_like(D)
    for i in range(len(th)):
        direction = np.zeros_like(th); direction[i] = h
        plus, _ = simulate(th+direction, J, c['train'], dt)
        minus, _ = simulate(th-direction, J, c['train'], dt)
        fd[..., i] = (plus-minus)/(2*h)
    relative = float(np.linalg.norm(fd-D)/np.linalg.norm(fd))
    # q for known linear dynamics, only bias unknown, paired interventions.
    N = cfg['neurons']; rng = np.random.default_rng(18)
    qs = []; grads = []
    for _ in range(12):
        b = rng.normal(0, .3, N)
        rr, dd = simulate(b, J, c['intervention'], dt, True, linear=True)
        qs.append(dt*np.sum(rr[1, :, c['readout']]-rr[0, :, c['readout']]))
        grads.append(dt*np.sum(dd[1, :, c['readout']]-dd[0, :, c['readout']], axis=0))
    # Finite dt check uses the same piecewise-constant input at half the step.
    q1, _ = response(th, J, c['intervention'], c['readout'], dt)
    q2, _ = response(th, J, np.repeat(c['intervention'], 2, axis=1), c['readout'], dt/2)
    # A direct information-budget audit: design invariant under changed truth.
    pool = list(range(N))
    d1, _ = prospective_design(c, cfg, cfg['budgets'][0], pool)
    c2 = dict(c, truth=np.full_like(th, 10.))
    d2, _ = prospective_design(c2, cfg, cfg['budgets'][0], pool)
    out = dict(derivative_relative_error=relative,
               linear_bias_null_q_range=float(np.ptp(qs)),
               linear_bias_null_max_gradient=float(np.max(np.abs(grads))),
               dt_half_absolute_q_change=abs(q2-q1),
               dt_half_relative_q_change=abs(q2-q1)/max(abs(q2), 1e-12),
               design_independent_of_truth=d1 == d2)
    assert relative < 1e-5, out
    assert out['linear_bias_null_q_range'] < 1e-10, out
    assert out['linear_bias_null_max_gradient'] < 1e-10, out
    assert out['design_independent_of_truth'], out
    return out


def summarize(rows, cfg, elapsed):
    groups = {}
    for r in rows:
        groups.setdefault((r['pool'], r['budget'], r['method']), []).append(r)
    summaries = []
    for (pool, budget, method), rr in sorted(groups.items()):
        summaries.append(dict(pool=pool, budget=budget, method=method, n=len(rr),
            q_rmse=float(np.sqrt(np.mean([r['q_error']**2 for r in rr]))),
            median_abs_q_error=float(np.median([abs(r['q_error']) for r in rr])),
            normalized_q_rmse=float(np.sqrt(np.mean([r['q_error']**2/max(r['prior_q_variance'],1e-12) for r in rr]))),
            passive_mse=float(np.mean([r['passive_mse'] for r in rr])),
            coverage_95=float(np.mean([r['covered_95'] for r in rr])),
            success_fraction=float(np.mean([r['optimizer_success'] for r in rr])),
            mean_fit_seconds=float(np.mean([r['fit_seconds'] for r in rr]))))
    paired = []
    for pool in cfg['pools']:
        for budget in cfg['budgets']:
            for competitor in [m for m in cfg['methods'] if m != 'goal']:
                a = {r['seed']:r for r in rows if r['pool']==pool and r['budget']==budget and r['method']=='goal'}
                b = {r['seed']:r for r in rows if r['pool']==pool and r['budget']==budget and r['method']==competitor}
                seeds=sorted(a.keys() & b.keys())
                if not seeds: continue
                diff=np.array([abs(a[s]['q_error'])-abs(b[s]['q_error']) for s in seeds])
                rng=np.random.default_rng(987)
                boot=np.mean(rng.choice(diff, size=(4000,len(diff)), replace=True), axis=1)
                paired.append(dict(pool=pool,budget=budget,competitor=competitor,n=len(seeds),
                    mean_abs_error_difference=float(diff.mean()),
                    exploratory_bootstrap_95=list(map(float,np.quantile(boot,[.025,.975]))),
                    goal_wins=int(np.sum(diff<0)), ties=int(np.sum(np.abs(diff)<1e-12))))
    return dict(status='exploratory synthetic pilot; not biological validation',
                elapsed_seconds=elapsed, fits=len(rows), groups=summaries, paired=paired,
                interpretation='Negative error difference favors goal. Intervals exploratory; same J per seed across methods. No confirmatory claims.')


def plot(rows, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    pools=sorted({r['pool'] for r in rows}); budgets=sorted({r['budget'] for r in rows})
    fig,axs=plt.subplots(len(pools),len(budgets),figsize=(10,4*len(pools)),squeeze=False)
    for ax,(pool,budget) in zip(axs.ravel(),[(p,b) for p in pools for b in budgets]):
        methods=['activity','stimulus_state','response_state','goal','random','shuffled_goal','parameter']
        vals=[[abs(r['q_error'])/np.sqrt(max(r['prior_q_variance'],1e-12)) for r in rows if r['pool']==pool and r['budget']==budget and r['method']==m] for m in methods]
        ax.boxplot(vals, tick_labels=['Calibration','Stimulus','Response','Goal','Random','Other goal','Parameter'],showfliers=True)
        ax.tick_params(axis='x', rotation=35)
        ax.set_title(f'{pool}; recorded neurons M={budget}')
        ax.set_ylabel('|response error| / prior response SD')
        ax.grid(axis='y', alpha=.2)
    fig.suptitle('Synthetic feasibility pilot — independent networks, no biological data',fontsize=12)
    fig.tight_layout();fig.savefig(out/'pilot_response_errors.png',dpi=180);plt.close(fig)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--teachers',type=int,default=12)
    ap.add_argument('--seed-start',type=int,default=100)
    ap.add_argument('--neurons',type=int,default=12)
    ap.add_argument('--smoke',action='store_true')
    ap.add_argument('--wall-limit',type=float,default=600.)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    cfg=dict(neurons=args.neurons,dt=.05,steps=120,sample_stride=4,noise_sd=.05,
             connectivity_norm=.65,log_gain_sd=.18,bias_sd=.18,max_nfev=60,
             teachers=args.teachers,seed_start=args.seed_start,
             budgets=[3] if args.smoke else [3,6],
             pools=['all'] if args.smoke else ['all','exclude_endpoints'],
             methods=['activity','stimulus_state','response_state','goal','random','shuffled_goal','parameter'],
             wall_limit_seconds=args.wall_limit,threads=2,
             protocol_status='exploratory; frozen before this run',
             design='prior nominal theta=0 only; no truth/measurements/test outcomes',
             scope='dimensionless Dale-signed synthetic softplus rate network; no connectome or wet-lab data')
    encoded=json.dumps(cfg,indent=2,sort_keys=True)
    (args.out/'protocol.json').write_text(encoded)
    (args.out/'protocol.sha256').write_text(hashlib.sha256(encoded.encode()).hexdigest()+'\n')
    (args.out/'source.sha256').write_text(hashlib.sha256(Path(__file__).read_bytes()).hexdigest()+'\n')
    start=time.perf_counter();rows=[]
    with threadpool_limits(limits=2):
        diagnostic=checks(cfg)
        for seed in range(args.seed_start,args.seed_start+args.teachers):
            c=make_case(seed,cfg);N=cfg['neurons']
            true_train,_=simulate(c['truth'],c['J'],c['train'],cfg['dt'])
            rng=np.random.default_rng(seed+10000)
            obs=true_train[:,::cfg['sample_stride']]+rng.normal(0,cfg['noise_sd'],true_train[:,::cfg['sample_stride']].shape)
            true_passive,_=simulate(c['truth'],c['J'],c['passive_test'],cfg['dt'])
            qtrue,_=response(c['truth'],c['J'],c['intervention'],c['readout'],cfg['dt'])
            qwrong_true,_=response(c['truth'],c['J'],c['shuffled'],c['shuffled_readout'],cfg['dt'])
            for pool_name in cfg['pools']:
                pool=[i for i in range(N) if pool_name=='all' or i not in [c['stim'],c['readout']]]
                for budget in cfg['budgets']:
                    designs,prior_qvar=prospective_design(c,cfg,budget,pool)
                    rand=np.random.default_rng(seed+20000).choice(pool,size=budget,replace=False).tolist()
                    designs['random']=dict(nodes=rand,predicted_q_variance=None)
                    for method in cfg['methods']:
                        selected=designs[method]['nodes'];t=time.perf_counter()
                        fit,qhat,qvar,qwrong=fit_map(c,cfg,selected,obs[:,:,selected])
                        rhat,_=simulate(fit.x,c['J'],c['passive_test'],cfg['dt'])
                        rows.append(dict(seed=seed,pool=pool_name,budget=budget,method=method,
                            nodes=';'.join(map(str,selected)),stim=c['stim'],readout=c['readout'],
                            includes_stim=c['stim'] in selected,includes_readout=c['readout'] in selected,
                            q_true=qtrue,q_hat=qhat,q_error=qhat-qtrue,q_variance=qvar,prior_q_variance=prior_qvar,
                            other_q_true=qwrong_true,other_q_hat=qwrong,other_q_error=qwrong-qwrong_true,
                            design_q_variance=designs[method]['predicted_q_variance'],
                            passive_mse=float(np.mean((rhat-true_passive)**2)),
                            covered_95=abs(qhat-qtrue)<=1.96*np.sqrt(qvar),
                            optimizer_success=bool(fit.success),nfev=int(fit.nfev),
                            objective=float(fit.cost),optimality=float(fit.optimality),
                            fit_seconds=time.perf_counter()-t))
            print(json.dumps(dict(seed=seed,fits=len(rows),elapsed_seconds=round(time.perf_counter()-start,2))),flush=True)
            with (args.out/'results.csv').open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
            if time.perf_counter()-start>args.wall_limit: break
        elapsed=time.perf_counter()-start
        summary=summarize(rows,cfg,elapsed)
        summary.update(checks=diagnostic,completed_teachers=len({r['seed'] for r in rows}),
                       environment=dict(python=platform.python_version(),numpy=np.__version__,machine=platform.machine(),threadpools=threadpool_info()))
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2))
    plot(rows,args.out)
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
