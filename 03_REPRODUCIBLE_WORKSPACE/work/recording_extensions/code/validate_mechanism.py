"""Check the diagnostic ablations against direct finite-ensemble calculations."""
import copy
import json
from pathlib import Path

import numpy as np
from threadpoolctl import threadpool_limits

from design import build_bank, choose
from rank2_refined import refined_case
from run_mechanism import first_step_diagnostics, mechanism_designs


def main():
    root = Path(__file__).resolve().parent.parent
    cfg = json.loads((root/'protocols/mechanism.json').read_text())
    cfg.update(neurons=8, steps=40, ensemble_size=8, scale_samples=8, budgets=[1, 2])
    case = refined_case(19001, cfg, cfg['conditions'][-1], 2)
    bank = build_bank(case, cfg)
    pool = [i for i in range(8) if i not in {case['stim'], *case['readouts'].tolist()}]
    diag = first_step_diagnostics(bank, pool)
    paths = mechanism_designs(case, cfg, bank, 'exclude_endpoints', 1)
    fields = ['nominal_risks', 'ensemble_risks', 'fixed_goal_risks', 'fixed_info_risks']
    for design, field in zip(paths, fields):
        assert design['nodes'][0] == pool[int(np.argmin(diag[field]))]
        assert np.isclose(design['greedy_risk_path'][0], min(diag[field]), rtol=1e-11, atol=1e-14)
        r0 = float(np.mean(design['risk_nominal']))
        re = float(np.mean(design['risk_ensemble']))
        component_sum = sum(design[k] for k in [
            'risk_observation_component', 'risk_target_component', 'risk_interaction_component'])
        assert np.isclose(re-r0, component_sum, rtol=1e-10, atol=1e-14)
    # Averaging target weights before solving must equal explicit averaging
    # when all information matrices are fixed to the nominal one.
    count = cfg['ensemble_size']
    explicit = choose(np.repeat(bank['info'][:1], count, axis=0), bank['vector'][1:], pool, 2)
    reduced = choose(bank['info'][:1], bank['vector'][1:].mean(axis=0, keepdims=True), pool, 2)
    assert explicit[0] == reduced[0]
    assert np.allclose(explicit[1], reduced[1], rtol=1e-12, atol=1e-14)
    # If both components have no parameter dependence all four rules coincide.
    null = {k: v for k, v in bank.items() if k != '_paths'}
    for field in ['info', 'vector', 'goal', 'gradients']:
        null[field] = np.repeat(bank[field][:1], len(bank['particles']), axis=0)
    identical = mechanism_designs(case, cfg, null, 'exclude_endpoints', 2)
    assert all(d['nodes'] == identical[0]['nodes'] for d in identical)
    # Cached maximum-budget paths reproduce independently solved shorter paths.
    fresh = choose(bank['info'][1:], bank['vector'][1:], pool, 1)
    assert fresh[0] == paths[1]['nodes']
    assert np.allclose(fresh[1], paths[1]['greedy_risk_path'])
    result = dict(passed=True, checks=[
        'four rules match direct first-step risk calculation',
        'exact three-component risk decomposition',
        'fixed-information averaging identity',
        'parameter-invariant null gives identical choices',
        'maximum-budget prefix cache preserves greedy choice'],
        development_network=19001, production_networks_used=False)
    (root/'analysis/mechanism_validation.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    with threadpool_limits(limits=1):
        main()
