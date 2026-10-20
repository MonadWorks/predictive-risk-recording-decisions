"""Fixed network-level contrasts for the recording-to-combination study."""
from pathlib import Path
import sys, json
HERE5 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE5.parent / 'round4/code'))
from common4 import np, dump, bootstrap_change

POLICIES = ['endpoints4', 'random5', 'combination5', 'response5',
            'oracle_combinations', 'oracle_ordinary']
PRIMARY = [('response_mse', 'oracle_combinations', 'oracle_ordinary'),
           ('profile_width_squared', 'combination5', 'random5'),
           ('response_mse', 'combination5', 'random5')]


def contrast(a, b):
    result = bootstrap_change(a, b)
    ids = np.random.default_rng(20261021).integers(0, len(a), (30000, len(a)))
    values = 100 * (np.asarray(a)[ids].mean(1) / np.asarray(b)[ids].mean(1) - 1)
    result['ci_family_three'] = np.percentile(values, [100 * .05 / 6, 100 * (1 - .05 / 6)]).tolist()
    return result


def main():
    data = [json.loads((HERE5 / 'runs/validation' / f'{n}.json').read_text()) for n in range(60000, 60040)]
    assert all(d['complete'] for d in data)
    metrics = {}
    for metric in ['response_mse', 'combination_mse', 'endpoint_mse',
                   'profile_width_squared', 'combination_local_variance']:
        metrics[metric] = {}
        for policy in POLICIES:
            if policy.startswith('oracle') and metric in ['profile_width_squared', 'combination_local_variance']:
                continue
            rows = [next(r for r in d['records'] if r['policy'] == policy) for d in data]
            metrics[metric][policy] = [r['profile']['width'] ** 2 if metric == 'profile_width_squared' else r[metric] for r in rows]
    primary = {f'{m}/{a}_vs_{b}': contrast(metrics[m][a], metrics[m][b]) for m, a, b in PRIMARY}
    secondary = {}
    for m in metrics:
        for a, b in [('combination5', 'random5'), ('combination5', 'response5'),
                     ('random5', 'endpoints4'), ('combination5', 'endpoints4'), ('response5', 'random5')]:
            key = f'{m}/{a}_vs_{b}'
            if key not in primary:
                secondary[key] = contrast(metrics[m][a], metrics[m][b])
    selected = [r for d in data for r in d['records']]
    profiles = [r['profile'] for r in selected if 'profile' in r]
    out = dict(n=40, network_ids=[d['network_id'] for d in data], metrics=metrics,
               primary=primary, secondary=secondary,
               agreement={f'{a}_vs_{b}': sum(d['selection']['nodes'][a] == d['selection']['nodes'][b] for d in data)
                          for a, b in [('combination5', 'random5'), ('combination5', 'response5'), ('response5', 'random5')]},
               audit_networks=[d['network_id'] for d in data if d['audit']],
               failed_selected=sum(not r['best']['success'] for r in selected),
               above_generating=sum(r['best']['objective'] > r['generating_objective'] + 1e-6 for r in selected),
               unresolved_flags=[dict(network_id=d['network_id'], flags=d['unresolved_fit_flags']) for d in data if d['unresolved_fit_flags']],
               profile_searches=len(profiles) * 2,
               profile_successful_chosen=sum(s['chosen']['success'] for p in profiles for s in p['searches']),
               seconds=sum(d['seconds'] for d in data))
    dump(HERE5 / 'analysis/summary.json', out)
    print(json.dumps(dict(primary=primary, agreement=out['agreement'], audit_networks=out['audit_networks'],
                          unresolved_flags=out['unresolved_flags']), indent=2))
    return out


if __name__ == '__main__':
    main()
