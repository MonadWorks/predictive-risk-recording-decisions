"""Read-only checks of source freezes, paired data and retained fit records."""
from pathlib import Path
import json, hashlib, statistics, math

HERE = Path(__file__).resolve().parent.parent


def close(a, b):
    assert math.isclose(a, b, rel_tol=2e-9, abs_tol=1e-12), (a, b)


def main():
    protocol = json.loads((HERE / 'protocols/recording_information.json').read_text())
    for file, expected in protocol['source_hashes'].items():
        assert hashlib.sha256((HERE.parent / file).read_bytes()).hexdigest() == expected, file
    summary = json.loads((HERE / 'analysis/summary.json').read_text())
    assert sorted(int(p.stem) for p in (HERE/'runs/validation').glob('*.json'))==protocol['network_ids']
    data = []
    for nid in protocol['network_ids']:
        d = json.loads((HERE / 'runs/validation' / f'{nid}.json').read_text())
        assert d['complete'] and d['network_id'] == nid
        assert len(d['records']) == 6
        assert all(r['q_true']==d['records'][0]['q_true'] for r in d['records'])
        assert not d['unresolved_fit_flags'], (nid, d['unresolved_fit_flags'])
        ends = {d['stim'], *d['readouts']}
        for policy, field in [('combination5','combination_scores'),('response5','response_scores')]:
            extra = next(i for i in d['selection']['nodes'][policy] if i not in ends)
            index = d['selection']['candidate_sites'].index(extra)
            close(d['selection'][field][index], min(d['selection'][field]))
        close(sum(x*x for x in d['selection']['profile_row']),1.)
        for i, row in enumerate(d['internal_rows']):
            assert all(abs(row[k])<1e-10 for k in ends)
            for j, other in enumerate(d['internal_rows']):
                close(sum(a*b for a,b in zip(row,other)),float(i==j))
        for r in d['records']:
            assert len(r['fits']) == 9 + 9 * len(d['audit'])
            close(r['best']['objective'], min(f['objective'] for f in r['fits']))
            assert r['best']['success']
            assert r['best']['objective'] <= r['generating_objective'] + 1e-6
            close(r['response_mse'], statistics.mean((a-b)**2 for a,b in zip(r['best']['q_hat'],r['q_true'])))
            dz = [a-b for a,b in zip(r['best']['z'],d['generating_z'])]
            close(r['combination_mse'], statistics.mean(sum(a*b for a,b in zip(row,dz))**2 for row in d['internal_rows']))
            close(r['endpoint_mse'], statistics.mean(dz[i]**2 for i in ends))
            if r['policy'].startswith('oracle'):
                assert r['best']['constraint_rank']==8
                assert r['best']['constraint_error'] < 1e-10
                assert not ends.intersection(r['nodes'])
            else:
                assert ends.issubset(r['nodes'])
                assert len(r['nodes']) == (4 if r['policy']=='endpoints4' else 5)
                p = r['profile']
                close(p['width'], p['searches'][1]['chosen']['value']-p['searches'][0]['chosen']['value'])
                for search in p['searches']:
                    s = search['chosen']
                    assert s['source']=='slsqp' and s['success'],(nid,r['policy'],search['sign'])
                    assert s['cost'] <= r['best']['objective'] + p['delta'] + 1e-5
                    close(s['value'], sum(a*b for a,b in zip(p['row'],s['z'])))
                for other in d['records']:
                    if other['policy'].startswith('oracle'):
                        continue
                    if r['nodes'] == other['nodes']:
                        assert r['best'] == other['best'] and r['profile'] == other['profile']
        data.append(d)
    for metric, by_policy in summary['metrics'].items():
        for policy, values in by_policy.items():
            for d, value in zip(data, values):
                r = next(r for r in d['records'] if r['policy']==policy)
                expected = r['profile']['width']**2 if metric=='profile_width_squared' else r[metric]
                close(value, expected)
    for group in ['primary','secondary']:
        for key, c in summary[group].items():
            metric, comparison = key.split('/')
            a, b = comparison.split('_vs_')
            close(c['change_pct'],100*(statistics.mean(summary['metrics'][metric][a])/statistics.mean(summary['metrics'][metric][b])-1))
    checks = json.loads((HERE/'analysis/numerical_checks.json').read_text())
    assert checks['passed'] and checks['profile_relative_error'] < 1e-6
    return dict(status='PASS',independent_networks=len(data),retained_policy_records=sum(len(d['records']) for d in data),
                audit_networks=summary['audit_networks'],
                scope='Source freeze, all planned IDs, shared fits, MSE identities, profile feasibility and aggregation')


if __name__=='__main__':
    print(json.dumps(main(),indent=2))
