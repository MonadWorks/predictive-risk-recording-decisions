"""Independent fifth-recording confirmation and shared-reference diagnostics.

Uses the frozen round-five selectors and inference model. Selection receives
the public model/prior only. Noise repeats are averaged within network.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent.parent
EXT = HERE.parent
sys.path.insert(0, str(EXT / 'round5/code'))
from experiment5 import np, json, time, seeded, dump, starts, select_sites, combination_rows, FastProblem
from common4 import case_for, data_for
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse
import hashlib
from datetime import datetime, timezone

POLICIES = ['endpoints4', 'random5', 'combination5', 'response5']
NETWORKS = list(range(61000, 61080))
NOISE_REPEATS = 3


def covariance_metrics(h, gradient, basis, endpoints):
    """Exact block decomposition of the local three-response variance."""
    endpoint = np.zeros_like(gradient)
    endpoint[:, endpoints] = gradient[:, endpoints]
    internal = np.einsum('ki,ai,aj->kj', gradient, basis, basis)
    other = gradient - endpoint - internal
    parts = np.asarray([endpoint, internal, other])
    rhs = parts.reshape(-1, h.shape[0]).T
    solved = np.linalg.solve(h, rhs).T.reshape(parts.shape)
    blocks = np.einsum('aki,bki->ab', parts, solved) / len(gradient)
    total = float(np.einsum('ki,ik->', gradient, np.linalg.solve(h, gradient.T)) / len(gradient))
    cb = np.einsum('ai,ib->ab', basis, np.linalg.solve(h, basis.T))
    assert np.isclose(blocks.sum(), total, atol=1e-12, rtol=1e-9)
    return dict(response_variance=total, internal_variance=float(np.trace(cb) / len(basis)),
                blocks=blocks.tolist(), internal_covariance=cb.tolist())


def diagnostics(case, cfg, selection, baseline_z, finite=True):
    """Evaluate all sets at the SAME four-endpoint fit, keeping linearization fixed.

    The extra site's observed values and the generating gains are not used.
    These calculations diagnose information acquisition, not selection.
    """
    m = case['model']
    ends, _, _, basis = combination_rows(case)
    theta = case['mu'] + case['sd'] * baseline_z
    nodes = sorted({i for s in selection['nodes'].values() for i in s})
    _, derivative = m.simulate(theta, case['train'], True, nodes)
    f = derivative[:, ::cfg['sample_stride']].transpose(2, 0, 1, 3).reshape(len(nodes), -1, m.P)
    f = f * case['sd'][None, None, :] / cfg['noise_sd']
    info = np.einsum('nki,nkj->nij', f, f)
    _, g = m.responses(theta, case['intervention'], True)
    g = g[case['readouts']] * case['sd'][None, :]
    metrics = {}
    for policy in POLICIES:
        ids = [nodes.index(i) for i in selection['nodes'][policy]]
        metrics[policy] = covariance_metrics(np.eye(m.P) + info[ids].sum(0), g, basis, ends)
    base = metrics['endpoints4']
    for policy in POLICIES[1:]:
        # At a common linearization, adding an observation is positive information.
        for key in ['response_variance', 'internal_variance']:
            assert metrics[policy][key] <= base[key] + 1e-10 * max(1., base[key])
    perturbations = []
    if finite:
        values, vectors = np.linalg.eigh(base['internal_covariance'])
        for i in range(len(values)):
            direction = np.einsum('a,ai->i', vectors[:, i], basis)
            local = np.einsum('ki,i->k', g, direction)
            changes = []
            for radius in [.1, .3]:
                responses = []
                for sign in [-1, 1]:
                    q, _ = m.responses(theta + sign * radius * case['sd'] * direction,
                                       case['intervention'])
                    responses.append(q[case['readouts']])
                slope = (responses[1] - responses[0]) / (2 * radius)
                changes.append(dict(radius=radius, response_slope=slope.tolist(),
                                    mean_squared_slope=float(np.mean(slope ** 2))))
            perturbations.append(dict(variance=float(values[i]), local_slope=local.tolist(),
                                      mean_squared_local_slope=float(np.mean(local ** 2)), finite=changes))
    return dict(reference='four-endpoint MAP, shared across all sets', metrics=metrics,
                internal_modes=perturbations)


def compact_fit(fit):
    return {k: v for k, v in fit.items() if k != 'z'}


def worker(nid, stage='validation'):
    path = HERE / 'runs' / stage / f'{nid}.json'
    if path.exists():
        saved = json.loads(path.read_text())
        assert saved['complete']
        return dict(network_id=nid, cached=True)
    tick = time.perf_counter()
    cfg, case = case_for(nid)
    cfg['max_nfev'] = 400
    selection = select_sites(case, cfg)
    ends, _, _, basis = combination_rows(case)
    repeats = []
    for noise_id in range(NOISE_REPEATS):
        theta, clean, noise, trueq = data_for(case, cfg, tid=0, noiseid=noise_id)
        truthz = (theta - case['mu']) / case['sd']
        objects, fits_by_key = {}, {}
        for policy in POLICIES:
            key = tuple(selection['nodes'][policy])
            if key in objects:
                continue
            ids = list(key)
            problem = FastProblem(case, cfg, ids, clean[:, :, ids] + cfg['noise_sd'] * noise[:, :, ids], cfg['noise_sd'])
            objects[key] = problem
            fits_by_key[key] = [problem.fit(initial, 400) for initial in starts(nid)]
        audits = []
        for iteration in range(3):
            flags = []
            for key, problem in objects.items():
                best = min(fits_by_key[key], key=lambda x: x['objective'])
                if not best['success'] or best['objective'] > problem.cost_value(truthz) + 1e-6:
                    flags.append(list(key))
            if not flags or iteration == 2:
                break
            audits.append(dict(iteration=iteration + 1, flagged_sets=flags))
            extra = seeded(97631 + iteration, nid, noise_id).normal(size=(8, case['model'].P))
            for key, problem in objects.items():
                best = min(fits_by_key[key], key=lambda x: x['objective'])
                fits_by_key[key].extend(problem.fit(initial, 400) for initial in [np.asarray(best['z']), *extra])
        records = []
        for policy in POLICIES:
            key = tuple(selection['nodes'][policy])
            best = min(fits_by_key[key], key=lambda x: x['objective'])
            dz = np.asarray(best['z']) - truthz
            records.append(dict(policy=policy, nodes=list(key), best=best,
                                starts=[compact_fit(f) for f in fits_by_key[key]],
                                response_mse=float(np.mean((np.asarray(best['q_hat']) - trueq) ** 2)),
                                endpoint_mse=float(np.mean(dz[ends] ** 2)),
                                combination_mse=float(np.mean(np.einsum('ai,i->a', basis, dz) ** 2)),
                                generating_objective=float(objects[key].cost_value(truthz))))
        baseline_z = np.asarray(records[0]['best']['z'])
        diagnostic = diagnostics(case, cfg, selection, baseline_z)
        repeats.append(dict(noise_id=noise_id, q_true=trueq.tolist(), records=records,
                            diagnostics=diagnostic, audits=audits, unresolved_fit_flags=flags))
    out = dict(network_id=nid, complete=True, stage=stage, seconds=time.perf_counter() - tick,
               selection=selection, generating_z=truthz.tolist(), noise_repeats=repeats)
    dump(path, out)
    return dict(network_id=nid, seconds=round(out['seconds'], 2),
                unresolved=sum(bool(r['unresolved_fit_flags']) for r in repeats))


def freeze():
    path = HERE / 'protocols/task_aligned_recording.json'
    assert not path.exists(), 'Frozen protocol already exists'
    assert not list((HERE / 'runs/validation').glob('*.json')), 'Validation outcomes already exist'
    sources = ['round6/code/followup6.py', 'round6/code/analyze6.py',
               'round5/code/experiment5.py', 'round4/code/common4.py', 'round3/code/common.py',
               'round3/code/fast_values.py', 'code/models.py', 'code/rank2_refined.py', 'code/design.py',
               'protocols/confirmation.json']
    dump(path, dict(timestamp_utc=datetime.now(timezone.utc).isoformat(), network_ids=NETWORKS,
        physiological_draws_per_network=1, noise_repeats=NOISE_REPEATS, targets=3,
        model='Frozen 100-unit rank-two signed-gain model and held-out stimulus task',
        policies=POLICIES, selectors='Unmodified round-five select_sites, 32 common prior particles; selection precedes data',
        primary='Mean response MSE: response5 versus random5, one primary comparison',
        secondary=['response5 versus endpoints4', 'combination5 versus random5',
                   'response5 versus combination5', 'random5 versus endpoints4'],
        aggregation='Average response MSE over three targets and three noise draws within network; independent paired network bootstrap',
        uncertainty='95% paired-network bootstrap with 30000 draws; secondary intervals descriptive pointwise; leave-one-network influence retained',
        sample_size='80 new independent networks, fixed before outcomes; no outcome-adaptive extension or stopping; precision expansion rather than a power guarantee',
        fitting='Nine common prior starts, max_nfev 400; selected failure or cost above generating feasible cost triggers one best and eight new common starts for all distinct sets, up to two rounds; retain all networks and flags',
        mechanism='Secondary shared-reference local covariance decomposition at the four-endpoint MAP: endpoint, internal-combination and orthogonal gradient blocks, including all cross terms. Finite central response changes along the four internal covariance modes at prior-standardized lengths 0.1 and 0.3.',
        interpretation='Local covariance changes are diagnostics, not a causal decomposition of realised squared error. Generating parameters are used only for evaluation and feasible-cost audits.',
        development_network_ids=[60980], historical_diagnostic_ids=list(range(60000, 60040)),
        source_hashes={s: hashlib.sha256((EXT / s).read_bytes()).hexdigest() for s in sources}))


def historical():
    for nid in range(60000, 60040):
        path = HERE / 'runs/historical_diagnostics' / f'{nid}.json'
        if path.exists():
            continue
        original = json.loads((EXT / 'round5/runs/validation' / f'{nid}.json').read_text())
        cfg, case = case_for(nid)
        baseline = next(r for r in original['records'] if r['policy'] == 'endpoints4')
        result = diagnostics(case, cfg, original['selection'], np.asarray(baseline['best']['z']))
        dump(path, dict(network_id=nid, source='round5/validation, retrospective', diagnostics=result))
    print('Historical diagnostics complete', flush=True)


def checks():
    rng = np.random.default_rng(4107)
    a = rng.normal(size=(12, 12)); h = np.eye(12) + np.einsum('ki,kj->ij', a, a)
    basis = np.eye(12)[2:6]; g = rng.normal(size=(3, 12))
    result = covariance_metrics(h, g, basis, [0, 1])
    assert np.isclose(np.asarray(result['blocks']).sum(), np.trace(g @ np.linalg.inv(h) @ g.T) / 3)
    cfg, case = case_for(60980)
    ends, _, _, basis = combination_rows(case)
    assert np.allclose(basis[:, ends], 0) and np.allclose(basis @ basis.T, np.eye(4))
    z = rng.normal(size=100) * .1
    m = case['model']; theta = case['mu'] + case['sd'] * z
    _, g = m.responses(theta, case['intervention'], True)
    direction = rng.normal(size=100); direction /= np.linalg.norm(direction)
    epsilon = 1e-5
    plus, _ = m.responses(theta + epsilon * case['sd'] * direction, case['intervention'])
    minus, _ = m.responses(theta - epsilon * case['sd'] * direction, case['intervention'])
    exact = np.einsum('ki,i->k', g, case['sd'] * direction)
    error = np.linalg.norm((plus-minus)/(2*epsilon)-exact) / max(np.linalg.norm(exact), 1e-15)
    assert error < 1e-5
    result = dict(status='PASS', gradient_relative_error=float(error), covariance_decomposition='PASS')
    dump(HERE / 'analysis/numerical_checks.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['check', 'development', 'freeze', 'run', 'historical'])
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.action == 'check': checks()
    elif args.action == 'development': print(json.dumps(worker(60980, 'development')))
    elif args.action == 'freeze': freeze()
    elif args.action == 'historical': historical()
    else:
        protocol = json.loads((HERE / 'protocols/task_aligned_recording.json').read_text())
        for source, expected in protocol['source_hashes'].items():
            assert hashlib.sha256((EXT / source).read_bytes()).hexdigest() == expected, source
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(worker, nid) for nid in protocol['network_ids']]
            for future in as_completed(futures):
                print(json.dumps(future.result()), flush=True)
