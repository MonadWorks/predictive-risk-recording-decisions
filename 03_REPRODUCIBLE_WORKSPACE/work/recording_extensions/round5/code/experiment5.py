"""Fresh-cohort information confirmation and a recording-to-combination test.

The extra-site criteria are existing local A-optimal design objectives. The
experiment tests whether acquiring recurrent-combination information through
actual recordings improves estimation and response prediction.
"""
from pathlib import Path
import sys

HERE5 = Path(__file__).resolve().parent.parent
EXT = HERE5.parent
sys.path.insert(0, str(EXT / 'round4/code'))
from common4 import np, json, time, seeded, dump, make_case, starts, paired_allocations
from design import build_bank
from oracle_combinations import constrained_fit
from fast_values import FastProblem
from scipy.optimize import minimize
from scipy.linalg import solve_triangular
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse


def combination_rows(case):
    m = case['model']
    ends = [int(case['stim']), *map(int, case['readouts'])]
    e = np.eye(m.P)[ends]
    a = np.einsum('ai,ib->abi', m.right, m.left).reshape(-1, m.P) * case['sd']
    internal = a.copy()
    internal[:, ends] = 0
    _, s, v = np.linalg.svd(internal, full_matrices=False)
    b = v[s > s[0] * 1e-10]
    assert len(b) == 4
    return ends, e, a, b


def risks(info, goals, sets):
    values = []
    p = info.shape[-1]
    for begin in range(0, len(sets), 12):
        batch = sets[begin:begin + 12]
        h = np.array([np.eye(p)[None] + info[:, s].sum(1) for s in batch])
        rhs = np.broadcast_to(goals.transpose(0, 2, 1)[None],
                              (*h.shape[:2], p, goals.shape[1]))
        sol = np.linalg.solve(h, rhs)
        value = np.mean(np.einsum('lkp,blpk->bl', goals, sol) / goals.shape[1], axis=1)
        values.extend(value.tolist())
    return np.asarray(values)


def select_sites(case, cfg):
    tick = time.perf_counter()
    ends, e, a, b = combination_rows(case)
    bank = build_bank(case, cfg)
    info = bank['info'][1:]
    pool = [i for i in range(case['model'].N) if i not in ends]
    sets = [sorted(ends + [i]) for i in pool]
    goals = np.broadcast_to(b, (len(info), *b.shape))
    cs = risks(info, goals, sets)
    qs = risks(info, bank['gradients'][1:], sets)
    random_site = next(i for i in paired_allocations(case)['both'] if i not in ends)
    policies = dict(endpoints4=sorted(ends), random5=sorted(ends + [random_site]),
                    combination5=sets[int(np.argmin(cs))], response5=sets[int(np.argmin(qs))])
    # The profiled direction is fixed before calibration outcomes are generated:
    # the leading recurrent-combination variance direction after four endpoints.
    h = np.eye(case['model'].P)[None] + info[:, ends].sum(1)
    sol = np.linalg.solve(h, np.broadcast_to(b.T, (len(info), *b.T.shape)))
    k = np.mean(np.einsum('kp,lpj->lkj', b, sol), axis=0)
    eigenvalues, eigenvectors = np.linalg.eigh(k)
    row = np.einsum('i,ij->j', eigenvectors[:, -1], b)
    return dict(nodes=policies, candidate_sites=pool, combination_scores=cs.tolist(),
                response_scores=qs.tolist(), profile_row=row.tolist(),
                profile_prior_variance=float(row @ row),
                endpoint_combination_variances=eigenvalues.tolist(),
                bank_seconds=bank['seconds'], seconds=time.perf_counter() - tick)


def profile_combination(problem, best, row, delta=2., maxiter=120):
    z = np.asarray(best['z'])
    jac = problem.evaluate(z)['jac']
    h = np.einsum('ki,kj->ij', jac, jac)
    transform = solve_triangular(np.linalg.cholesky(h).T, np.eye(len(z)), lower=False)
    gradient = np.einsum('i,ij->j', row, transform)
    variance = float(gradient @ gradient)
    scale = np.sqrt(max(variance, 1e-16))
    direction = gradient * np.sqrt(2 * delta / max(variance, 1e-16))
    center = float(row @ z)
    limit = best['objective'] + delta
    searches = []
    for sign in [-1, 1]:
        candidates = [dict(z=z.tolist(), value=center, cost=best['objective'],
                           success=True, feasible=True, source='map')]
        attempts = []
        for sid, initial in enumerate([np.zeros(len(z)), .6 * sign * direction]):
            def full(v):
                return z + np.einsum('ij,j->i', transform, v)
            fit = minimize(lambda v: -sign * float(gradient @ v) / scale, initial,
                           jac=lambda v: -sign * gradient / scale, method='SLSQP',
                           constraints=[dict(type='ineq',
                               fun=lambda v: (limit - problem.cost_value(full(v))) / delta,
                               jac=lambda v: -np.einsum('i,ij->j', problem.evaluate(full(v))['grad'], transform) / delta)],
                           options=dict(maxiter=maxiter, ftol=1e-8))
            point = full(fit.x)
            cost = float(problem.cost_value(point))
            value = float(row @ point)
            rec = dict(z=point.tolist(), value=value, cost=cost,
                       success=bool(fit.success), feasible=bool(cost <= limit + 1e-5),
                       source='slsqp', start=sid, nit=int(fit.nit), message=str(fit.message))
            attempts.append(rec)
            if rec['feasible'] and np.isfinite(value):
                candidates.append(rec)
        searches.append(dict(sign=sign, chosen=max(candidates, key=lambda x: sign * x['value']),
                             attempts=attempts))
    width = searches[1]['chosen']['value'] - searches[0]['chosen']['value']
    return dict(delta=delta, row=row.tolist(), center=center, width=float(width),
                local_variance=variance, searches=searches)


def add_fits(problem, rows, truthz, start_list, previous=()):
    fits = list(previous)
    for initial in start_list:
        fits.append(problem.fit(initial, 400) if rows is None else
                    constrained_fit(problem, rows, truthz, initial))
    return min(fits, key=lambda f: f['objective']), fits


def worker(nid, stage='validation'):
    path = HERE5 / 'runs' / stage / f'{nid}.json'
    if path.exists():
        return dict(network_id=nid, cached=True)
    tick = time.perf_counter()
    # Selection uses only the public model/prior. No realised observations or
    # generating parameters are passed to select_sites.
    from common4 import case_for, data_for
    cfg, case = case_for(nid)
    cfg['max_nfev'] = 400
    selection = select_sites(case, cfg)
    ends, e, a, b = combination_rows(case)
    theta, clean, noise, trueq = data_for(case, cfg)
    truthz = (theta - case['mu']) / case['sd']
    sigma = cfg['noise_sd']
    ordinary = paired_allocations(case)['neither']
    perm = seeded(95231, nid).permutation([i for i in range(case['model'].N)
                                         if i not in ends and i not in ordinary]).tolist()
    oracle_rows = dict(oracle_combinations=np.row_stack((e, a)),
                       oracle_ordinary=np.eye(case['model'].P)[ends + perm[:4]])
    objects = {}
    fits_by_key = {}
    policies = list(selection['nodes']) + list(oracle_rows)
    for policy in policies:
        nodes = selection['nodes'].get(policy, ordinary)
        rows = oracle_rows.get(policy)
        key = policy if rows is not None else tuple(nodes)
        if key not in objects:
            objects[key] = FastProblem(case, cfg, nodes, clean[:, :, nodes] + sigma * noise[:, :, nodes], sigma)
            fits_by_key[key] = add_fits(objects[key], rows, truthz, starts(nid))
    audit = []
    profiles = {}
    for iteration in range(3):
        flags = []
        lowest = {}
        for policy in policies:
            nodes = selection['nodes'].get(policy, ordinary)
            rows = oracle_rows.get(policy)
            key = policy if rows is not None else tuple(nodes)
            p = objects[key]
            best, fits = fits_by_key[key]
            feasible_cost = float(p.cost_value(truthz))
            if not best['success'] or best['objective'] > feasible_cost + 1e-6:
                flags.append(dict(policy=policy, reason='fit_or_feasible_cost'))
            if rows is None and key not in profiles:
                profiles[key] = profile_combination(p, best, np.asarray(selection['profile_row']))
            if rows is None:
                candidates = [s for x in profiles[key]['searches'] for s in x['attempts']]
                candidate = min(candidates, key=lambda x: x['cost'])
                if candidate['cost'] < best['objective'] - .01:
                    flags.append(dict(policy=policy, reason='lower_profile_objective'))
                    lowest[key] = np.asarray(candidate['z'])
        if not flags or iteration == 2:
            break
        audit.append(dict(round=iteration + 1, flags=flags))
        extra = seeded(96031 + iteration, nid).normal(size=(8, case['model'].P))
        seen = set()
        for policy in policies:
            rows = oracle_rows.get(policy)
            nodes = selection['nodes'].get(policy, ordinary)
            key = policy if rows is not None else tuple(nodes)
            if key in seen:
                continue
            seen.add(key)
            best, fits = fits_by_key[key]
            own = lowest.get(key, np.asarray(best['z']))
            fits_by_key[key] = add_fits(objects[key], rows, truthz, [own, *extra], fits)
        profiles = {}
    records = []
    for policy in policies:
        rows = oracle_rows.get(policy)
        nodes = selection['nodes'].get(policy, ordinary)
        key = policy if rows is not None else tuple(nodes)
        p = objects[key]
        best, fits = fits_by_key[key]
        dz = np.asarray(best['z']) - truthz
        rec = dict(policy=policy, nodes=nodes, best=best, fits=fits, q_true=trueq.tolist(),
                   response_mse=float(np.mean((np.asarray(best['q_hat']) - trueq) ** 2)),
                   combination_mse=float(np.mean(np.einsum('ki,i->k', b, dz) ** 2)),
                   endpoint_mse=float(np.mean(dz[ends] ** 2)),
                   generating_objective=float(p.cost_value(truthz)))
        if rows is None:
            jac = p.evaluate(np.asarray(best['z']))['jac']
            h = np.einsum('ki,kj->ij', jac, jac)
            covariance = np.einsum('ki,ij->kj', b, np.linalg.solve(h, b.T))
            rec.update(combination_local_variance=float(np.trace(covariance) / len(b)),
                       profile=profiles[key])
        records.append(rec)
    out = dict(network_id=nid, complete=True, stage=stage, seconds=time.perf_counter() - tick,
               selection=selection, stim=int(case['stim']), readouts=case['readouts'].tolist(),
               internal_rows=b.tolist(), generating_z=truthz.tolist(), records=records,
               audit=audit, unresolved_fit_flags=flags)
    dump(path, out)
    return dict(network_id=nid, seconds=out['seconds'], audit_rounds=len(audit),
                unresolved=len(flags), distinct_recording_sets=len({tuple(s) for s in selection['nodes'].values()}))


def checks():
    rng = np.random.default_rng(96001)
    f = rng.normal(size=(2, 6, 9, 5))
    info = np.einsum('lnkp,lnkq->lnpq', f, f)
    g = rng.normal(size=(2, 4, 5))
    sets = [[0, 2], [1, 3, 5]]
    value = risks(info, g, sets)
    direct = [np.mean([np.trace(g[l] @ np.linalg.inv(np.eye(5) + info[l, s].sum(0)) @ g[l].T) / 4
                       for l in range(2)]) for s in sets]
    risk_error = float(np.max(abs(value - direct)))
    assert np.allclose(value, direct, rtol=1e-11, atol=1e-13)
    class Quadratic:
        def __init__(self):
            self.jac = np.row_stack((rng.normal(size=(8, 5)), np.eye(5)))
            self.h = self.jac.T @ self.jac
        def evaluate(self, z):
            return dict(jac=self.jac, grad=self.h @ z)
        def cost_value(self, z):
            return float(.5 * z @ self.h @ z)
    p = Quadratic()
    row = rng.normal(size=5)
    profile = profile_combination(p, dict(z=[0.] * 5, objective=0.), row)
    expected = 2 * np.sqrt(4 * row @ np.linalg.solve(p.h, row))
    profile_error = abs(profile['width'] / expected - 1)
    assert profile_error < 1e-6
    _, case, _, _, _, _, _ = make_case(59980, 'matched_rank2')
    ends, e, a, b = combination_rows(case)
    def projector(rows):
        _, s, v = np.linalg.svd(rows, full_matrices=False)
        v = v[s > s[0] * 1e-10]
        return v.T @ v
    rowspace_error = float(np.max(abs(projector(np.row_stack((e, a))) - projector(np.row_stack((e, b))))))
    assert rowspace_error < 1e-10
    out = dict(passed=True, risk_absolute_error=risk_error, profile_relative_error=profile_error,
               conditional_rowspace_error=rowspace_error,
               orthonormal_error=float(np.max(abs(b @ b.T - np.eye(4)))))
    dump(HERE5 / 'analysis/numerical_checks.json', out)
    print(json.dumps(out))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--start', type=int, default=60000)
    ap.add_argument('--count', type=int, default=40)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--stage', default='validation')
    args = ap.parse_args()
    if args.check:
        checks()
    else:
        with ProcessPoolExecutor(args.workers) as pool:
            jobs = [pool.submit(worker, nid, args.stage) for nid in range(args.start, args.start + args.count)]
            for job in as_completed(jobs):
                print(json.dumps(job.result()), flush=True)
