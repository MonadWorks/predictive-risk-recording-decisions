"""Independent linear reference calibration of the published Fig.8 criterion.

This is not a reproduction of the published figure or a nonlinear benchmark.
The stable symmetric rank-30 network construction is an explicit adaptation.
No upstream implementation has been copied. Run from the workspace root:
 MPLCONFIGDIR=work/research_v2/svd_reference_results/mpl-cache \
 work/research-v2-env/bin/python work/research_v2/svd_reference.py
"""
from pathlib import Path
import csv
import hashlib
import json
import platform
import time
import warnings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
from threadpoolctl import threadpool_limits, threadpool_info

OUT = Path(__file__).parent / 'svd_reference_results'
N, RANK, NETWORKS, DRAWS, RANDOM_SETS = 100, 30, 12, 2048, 20
BUDGETS = [1, 2, 4, 8, 16]
SEED = 20261016


def mm(a, b):
    """Independent contraction kernel; no BLAS matmul is used in this kernel."""
    return np.einsum('ik,kj->ij', a, b, optimize=False)


def greedy(L, max_budget):
    """Published normalized residual-row score, in an orthonormal latent basis."""
    total = np.sum(L * L)
    P = np.eye(L.shape[1])
    chosen, history = [], []
    for k in range(max_budget):
        residual = mm(L, P)
        norms = np.sqrt(np.sum(residual * residual, axis=1))
        directions = residual / norms[:, None]
        scores = np.sum(mm(L, directions.T)**2, axis=0) / total
        scores[chosen] = -np.inf
        i = int(np.argmax(scores))
        v = directions[i]
        before = np.sum(mm(L, P)**2) / total
        P -= np.outer(v, v)
        P = (P + P.T) / 2
        after = np.sum(mm(L, P)**2) / total
        assert np.isclose(before-after, scores[i], atol=1e-12)
        chosen.append(i)
        history.append({'budget': k+1, 'original_neuron_id': i,
                        'incremental_score': float(scores[i]),
                        'remaining_risk': float(after),
                        'projector_defect': float(np.linalg.norm(mm(P, P)-P))})
    return chosen, history


def evaluate(L, indices, z, x_true):
    """Exact noiseless posterior mean, followed by full-vector reconstruction."""
    _, singular, vh = np.linalg.svd(L[indices], full_matrices=False)
    rank = int(np.sum(singular > singular[0] * 1e-12))
    V = vh[:rank].T
    P = np.eye(L.shape[1])-mm(V, V.T)
    # z_hat is the minimum-norm solution to L_S z_hat = x_S.
    z_hat = mm(mm(z, V), V.T)
    x_hat = mm(z_hat, L.T)
    assert np.max(np.abs(x_true[:, indices]-x_hat[:, indices])) < 1e-9
    energy = np.sum(L**2)
    theoretical = float(np.sum(mm(L, P)**2) / energy)
    squared_errors = np.sum((x_true-x_hat)**2, axis=1) / energy
    empirical = float(np.mean(squared_errors))
    empirical_se = float(np.std(squared_errors, ddof=1)/np.sqrt(len(z)))
    B = mm(mm(P, mm(L.T, L)), P)
    exact_se = float(np.sqrt(2*np.sum(B**2)/len(z))/energy)
    assert abs(empirical-theoretical) < 5.5*exact_se + 1e-10
    return theoretical, empirical, empirical_se, exact_se, rank


def main():
    start = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    records, checks, selections, warning_records = [], [], [], []
    # Warning capture records and re-emits, rather than silencing platform issues.
    for network in range(NETWORKS):
        rng_J = np.random.default_rng(np.random.SeedSequence([SEED, network, 0]))
        weights = np.exp(.7*rng_J.normal(size=N))
        Q, _ = np.linalg.qr(weights[:, None]*rng_J.normal(size=(N, RANK)))
        eigenvalues = np.geomspace(.08, .82, RANK)
        J = mm(Q*eigenvalues, Q.T)
        A = np.linalg.solve(np.eye(N)-J, J)
        L = Q*(eigenvalues/(1-eigenvalues))
        A_independent = mm(L, Q.T)
        assert np.max(np.abs(A-A_independent)) < 1e-12
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            A_matmul = L @ Q.T
        for w in caught:
            message = str(w.message)
            warning_records.append({'network': network, 'category': w.category.__name__,
                                    'message': message})
            warnings.warn(message, w.category, stacklevel=1)
        assert np.all(np.isfinite(A_matmul))
        assert np.max(np.abs(A_matmul-A_independent)) < 1e-12
        order, history = greedy(L, max(BUDGETS))
        # Independently check the first choice using the full original A SVD.
        _, s, vh = np.linalg.svd(A, full_matrices=False)
        normalized = A / np.linalg.norm(A, axis=1, keepdims=True)
        original_score = np.sum((mm(normalized, vh.T)*s)**2, axis=1)/np.sum(s*s)
        assert order[0] == int(np.argmax(original_score))
        # Explicit full-bias draws, independent of J and all selections.
        rng_b = np.random.default_rng(np.random.SeedSequence([SEED, network, 1]))
        biases = rng_b.normal(size=(DRAWS, N))
        z = mm(biases, Q)
        x_true = mm(z, L.T)
        rng_random = np.random.default_rng(np.random.SeedSequence([SEED, network, 2]))
        orders = [('greedy', 0, order)]
        orders += [('random', i, rng_random.permutation(N).tolist())
                   for i in range(RANDOM_SETS)]
        for method, rep, sequence in orders:
            for budget in BUDGETS:
                indices = sequence[:budget]
                analytic, empirical, empirical_se, exact_se, rank = evaluate(L, indices, z, x_true)
                records.append({'network': network, 'method': method, 'random_set': rep,
                                'budget': budget, 'analytic_normalized_risk': analytic,
                                'mc_normalized_mse': empirical, 'mc_estimated_se': empirical_se,
                                'mc_exact_se': exact_se, 'mc_standardized_difference':
                                (empirical-analytic)/exact_se, 'observation_rank': rank,
                                'selected_original_ids': json.dumps(indices)})
        checks.append({'network': network, 'spectral_radius_J': float(eigenvalues.max()),
                       'continuous_dynamics_max_real_eigenvalue': float(eigenvalues.max()-1),
                       'solve_vs_independent_max_abs': float(np.max(np.abs(A-A_independent))),
                       'matmul_vs_einsum_max_abs': float(np.max(np.abs(A_matmul-A_independent))),
                       'all_matmul_finite': bool(np.all(np.isfinite(A_matmul))),
                       'full_A_SVD_first_choice_agrees': True,
                       'max_projector_defect': max(h['projector_defect'] for h in history)})
        selections.append({'network': network, 'history': history})
        print(f'linear reference {network+1}/{NETWORKS}: {time.perf_counter()-start:.2f}s', flush=True)
        if time.perf_counter()-start > 110:
            raise RuntimeError('Time guard reached; incomplete experiment must not be presented as complete')
    with (OUT/'per_network_and_set.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader(); writer.writerows(records)
    aggregate = []
    for method in ('greedy', 'random'):
        for budget in BUDGETS:
            per_network = []
            for i in range(NETWORKS):
                rows = [r for r in records if r['method']==method and r['budget']==budget and r['network']==i]
                per_network.append((np.mean([r['analytic_normalized_risk'] for r in rows]),
                                    np.mean([r['mc_normalized_mse'] for r in rows])))
            values = np.array(per_network)
            aggregate.append({'method': method, 'budget': budget,
                              'analytic_mean': float(values[:, 0].mean()),
                              'mc_mean': float(values[:, 1].mean()),
                              'network_sd': float(values[:, 0].std(ddof=1)),
                              'network_sem': float(values[:, 0].std(ddof=1)/np.sqrt(NETWORKS))})
    with (OUT/'aggregate.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(aggregate[0])); writer.writeheader(); writer.writerows(aggregate)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                         'pdf.fonttype': 42, 'ps.fonttype': 42})
    fig, ax = plt.subplots(figsize=(7.0, 5.1))
    fig.subplots_adjust(left=.12, right=.98, bottom=.27, top=.91)
    for method, color, label in [('greedy','#2166ac','Normalized-row greedy'), ('random','#b35806','Random (20 sets / network)')]:
        data = [r for r in aggregate if r['method']==method]
        analytic = np.array([r['analytic_mean'] for r in data])
        sem = np.array([r['network_sem'] for r in data])
        ax.plot(BUDGETS, analytic, color=color, lw=1.8, label=label+' — analytic')
        ax.fill_between(BUDGETS, analytic-sem, analytic+sem, color=color, alpha=.13)
        ax.scatter(BUDGETS, [r['mc_mean'] for r in data], facecolor='white', edgecolor=color,
                   s=40, lw=1.3, zorder=3, label=label+' — Monte Carlo')
    ax.set(xlabel='Number of exactly observed neurons', ylabel='Remaining full-state error / prior error',
           xticks=BUDGETS, ylim=(0,1.03), title='Independent linear calibration of the Fig. 8 criterion')
    ax.legend(frameon=False, fontsize=8, loc='upper right')
    fig.text(.12,.035, 'N = 100; rank = 30; 12 independent networks; 2,048 bias draws / network\n'
            'Known stable J; isotropic bias; noiseless internal-state observations\n'
            'Shading: ±1 SEM across networks. Not a reproduction of the published figure.',
            fontsize=8, va='bottom')
    for suffix in ('png','pdf'):
        fig.savefig(OUT/f'linear_reference.{suffix}', dpi=220)
    plt.close(fig)
    source = Path('work/source_audit/pinned/nn_fig8_plots_de.py')
    report = {'scope': 'Independent mathematical calibration only; not original figure reproduction, '
                       'not novel research, and not a ranking against nonlinear noisy rate observations.',
              'source': {'article':'https://doi.org/10.1038/s41593-025-02080-4',
                         'repository':'https://github.com/emebeiran/connconstr',
                         'commit':'f5f397b88f8dd5c2a5c13558ce6039194a284586',
                         'file':str(source), 'lines':'138–181',
                         'sha256':hashlib.sha256(source.read_bytes()).hexdigest()},
              'protocol': {'N':N,'rank':RANK,'network_count':NETWORKS,'budgets':BUDGETS,
                           'random_sets_per_network':RANDOM_SETS,'bias_draws_per_network':DRAWS,
                           'seed':SEED,'construction':'Q=qr(exp(0.7 Normal) row-weighted Gaussian); '
                           'J=Q diag(geomspace(.08,.82,30)) Q.T. Stable symmetric low-rank adaptation.',
                           'observation':'x_S = [A b]_S, A=(I-J)^-1 J, b~Normal(0,I), no noise',
                           'estimator':'Gaussian conditional mean / exact minimum-norm inverse',
                           'risk':'E||x-xhat||^2 / E||x||^2 = ||A P||_F^2 / ||A||_F^2',
                           'statistics':'12 independent networks; random sets and Monte Carlo bias draws '
                           'are within-network evaluations, not additional independent networks.'},
              'numerical_checks':checks,'warnings':warning_records,
              'maximum_absolute_mc_standardized_difference':max(abs(r['mc_standardized_difference']) for r in records),
              'aggregate':aggregate,'selections':selections,
              'versions':{'python':platform.python_version(),'numpy':np.__version__,
                          'scipy':scipy.__version__,'matplotlib':matplotlib.__version__,
                          'threadpools':threadpool_info()},
              'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'wall_seconds':time.perf_counter()-start}
    (OUT/'report.json').write_text(json.dumps(report, indent=2))
    (OUT/'README.md').write_text('''# Independent linear reference calibration

This is a calibration of the published normalized-row/SVD selection criterion, not a reproduction of Fig. 8 and not a new scientific result. It must not be ranked directly against the main finite-time softplus experiment: here observations are noiseless internal state and the only unknown is additive bias.

Source: Beiran & Litwin-Kumar (2025), https://doi.org/10.1038/s41593-025-02080-4 ; fixed repository commit and source-file hash are in report.json. Code is independently implemented; no upstream source is copied.

We deliberately construct stable symmetric rank-30 networks with eigenvalues from 0.08 to 0.82 (N=100). Thus continuous dynamics -x+J(x+b) are stable and steady state is x=(I-J)^-1 J b. This construction is our adaptation, not the paper's network distribution. Isotropic b and exact observations make the orthogonal projection risk exact. Selected rows retain original neuron IDs.

Greedy uses the published normalized residual-row score and orthogonal-complement update. For random sampling, each of 20 independent random permutations supplies all five nested budgets. There are 12 independent networks. A separate random stream generates 2,048 full N-dimensional Gaussian bias draws per network; these are reused across methods for paired evaluation, never for selection. Full x vectors are explicitly reconstructed using the exact Gaussian conditional mean. The analytic risk is compared with Monte Carlo MSE, with its exact sampling standard error. The primary independent unit is the network. The curve shading is ±1 network SEM, not a confidence interval or 20×12 independent networks.

Checks include dense solve versus independent low-rank einsum evaluation, finite matmul output versus einsum, first selection against full A SVD, observation interpolation, and projection idempotence. Platform matmul warnings, if any, are re-emitted and recorded in report.json; they are not suppressed. Main numerical products use a separate einsum kernel.

Run from workspace root:
```sh
MPLCONFIGDIR=work/research_v2/svd_reference_results/mpl-cache work/research-v2-env/bin/python work/research_v2/svd_reference.py
```
Dependencies are preinstalled in the stated venv; this script installs nothing. Exact versions, hashes and measured runtime are in report.json. CSVs retain all network/random-set/budget measurements, including individual selected IDs. The PNG and vector PDF show analytic curves, Monte Carlo estimates and network-level variability.
''')
    print(json.dumps({'wall_seconds':report['wall_seconds'], 'warnings':len(warning_records),
                      'max_mc_z':report['maximum_absolute_mc_standardized_difference'],
                      'aggregate':aggregate}, indent=2))


if __name__ == '__main__':
    with threadpool_limits(limits=1):
        main()
