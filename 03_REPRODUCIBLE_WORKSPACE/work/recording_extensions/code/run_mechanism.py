"""Matched-family mechanism experiments, using the original model and MAP fit.

The two hybrid criteria are component ablations of the existing risk formula.
They are diagnostics, not proposed new recording policies.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

import run
from design import build_bank, choose, risks_for_set
from rank2_refined import refined_case


def choose_vector(info, gradients, pool, budget):
    """Evaluate exactly trace(H^-1 G^T G/K) using K right-hand sides.

    The criterion and deterministic greedy rule are unchanged; only the
    linear algebra avoids constructing all P columns of the inverse.
    """
    count, _, p, _ = info.shape
    k = gradients.shape[1]
    h = np.tile(np.eye(p), (count, 1, 1))
    selected, costs = [], []
    rhs = gradients.transpose(0, 2, 1)
    for _ in range(budget):
        candidates = np.array([i for i in pool if i not in selected], dtype=np.int64)
        hs = h[:, None] + info[:, candidates]
        solved = np.linalg.solve(hs, np.broadcast_to(rhs[:, None], (count, len(candidates), p, k)))
        risk = np.einsum('lpk,lcpk->lc', rhs, solved).mean(axis=0)/k
        j = int(np.argmin(risk))
        node = int(candidates[j])
        selected.append(node)
        costs.append(float(risk[j]))
        h += info[:, node]
    return selected, costs


def first_step_diagnostics(bank, pool):
    info = bank['info'][:, pool]
    p = info.shape[-1]
    h = info + np.eye(p)
    c = np.linalg.solve(h, np.broadcast_to(np.eye(p), h.shape))
    w = bank['vector']
    full = np.einsum('lnij,lji->ln', c, w)
    observation = np.einsum('lnij,ji->ln', c, w[0])
    target = np.einsum('nij,lji->ln', c[0], w)
    nominal = full[0]
    averaged = full[1:].mean(axis=0)
    correlations = [float(spearmanr(nominal, row).statistic) for row in full[1:]]
    ordered = np.sort(nominal)
    best = int(np.argmin(nominal))
    return {
        'candidate_nodes': list(map(int, pool)),
        'nominal_risks': nominal.tolist(),
        'ensemble_risks': averaged.tolist(),
        'fixed_goal_risks': observation[1:].mean(axis=0).tolist(),
        'fixed_info_risks': target[1:].mean(axis=0).tolist(),
        'nominal_ensemble_rank_correlation': float(spearmanr(nominal, averaged).statistic),
        'mean_nominal_particle_rank_correlation': float(np.mean(correlations)),
        'particle_nominal_best_agreement': float(np.mean(np.argmin(full[1:], axis=1) == best)),
        'nominal_relative_top_gap': float((ordered[1] - ordered[0]) / max(abs(ordered[0]), 1e-30)),
        'first_choice_changed': bool(best != int(np.argmin(averaged))),
        'first_step_ensemble_regret_of_nominal': float((averaged[best] - averaged.min()) / max(abs(averaged[best]), 1e-30)),
    }


def mechanism_designs(case, cfg, bank, pool_name, budget):
    excluded = {case['stim'], *case['readouts'].tolist()}
    pool = [i for i in range(case['model'].N) if pool_name == 'all' or i not in excluded]
    paths = bank.setdefault('_paths', {})
    designs = []
    import time
    for method in cfg['methods']:
        start = time.perf_counter()
        key = (pool_name, method)
        if key not in paths:
            if method == 'local_vector':
                info, w = bank['info'][:1], bank['vector'][:1]
                g = bank['gradients'][:1]
            elif method == 'ensemble_vector':
                info, w = bank['info'][1:], bank['vector'][1:]
                g = bank['gradients'][1:]
            elif method == 'ensemble_fixed_goal':
                info = bank['info'][1:]
                w = np.broadcast_to(bank['vector'][0], bank['vector'][1:].shape)
                g = np.broadcast_to(bank['gradients'][0], bank['gradients'][1:].shape)
            elif method == 'ensemble_fixed_info':
                # With fixed observation information the risk is linear in W.
                # Average W before solving; this is the same finite-ensemble criterion.
                info = bank['info'][:1]
                w = bank['vector'][1:].mean(axis=0, keepdims=True)
            else:
                raise ValueError(method)
            if method == 'ensemble_fixed_info':
                paths[key] = choose(info, w, pool, max(cfg['budgets']))
            else:
                paths[key] = choose_vector(info, g, pool, max(cfg['budgets']))
        nodes, costs = paths[key]
        selected = nodes[:budget]
        nom, ens = risks_for_set(bank, selected)
        p = bank['info'].shape[-1]
        h = np.eye(p)[None] + bank['info'][:, selected].sum(axis=1)
        c = np.linalg.solve(h, np.broadcast_to(np.eye(p), h.shape))
        w = bank['vector']
        r0 = float(np.einsum('ij,ji->', c[0], w[0]))
        re = float(np.einsum('lij,lji->l', c[1:], w[1:]).mean())
        ri = float(np.einsum('lij,ji->l', c[1:], w[0]).mean())
        rg = float(np.einsum('ij,lji->l', c[0], w[1:]).mean())
        designs.append(dict(method=method, target=-1, replicate=0, nodes=selected,
                            risk_nominal=nom, risk_ensemble=ens,
                            risk_fixed_goal=ri, risk_fixed_info=rg,
                            risk_observation_component=ri-r0,
                            risk_target_component=rg-r0,
                            risk_interaction_component=re-ri-rg+r0,
                            greedy_risk_path=costs[:budget], seconds=time.perf_counter()-start))
    return designs


def execute(protocol, out):
    cfg = json.loads(protocol.read_text())
    if out.exists() and any(out.iterdir()):
        raise RuntimeError('fresh output directory required')
    out.mkdir(parents=True)
    snapshot = out/'supplement_source_snapshot'
    snapshot.mkdir()
    hashes = {}
    for source in Path(__file__).parent.glob('*.py'):
        shutil.copy2(source, snapshot/source.name)
        hashes[source.name] = hashlib.sha256(source.read_bytes()).hexdigest()
    (out/'supplement_source_hashes.json').write_text(json.dumps(hashes, indent=2))
    run.public_case = lambda nid, config, condition: refined_case(nid, config, condition, 2)
    run.recording_designs = mechanism_designs

    def bank_with_diagnostics(case, config):
        bank = build_bank(case, config)
        pool = [i for i in range(case['model'].N) if i not in {case['stim'], *case['readouts'].tolist()}]
        row = first_step_diagnostics(bank, pool)
        row.update(network_id=case['network_id'], prior_sd=float(case['sd'][0]),
                   pool='exclude_endpoints', scope='common empty-prefix ranking, before truth or data')
        with (out/'ranking_diagnostics.jsonl').open('a') as f:
            f.write(json.dumps(row)+'\n')
        return bank

    run.build_bank = bank_with_diagnostics
    run.execute(protocol, out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    execute(args.protocol, args.out)
