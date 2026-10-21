"""Read-only verification of the frozen protocol and every retained result."""
from pathlib import Path
import json, hashlib, math, statistics

HERE=Path(__file__).resolve().parent.parent


def close(a,b):
    assert math.isclose(a,b,rel_tol=2e-8,abs_tol=1e-12),(a,b)


def main():
    protocol=json.loads((HERE/'protocols/task_aligned_recording.json').read_text())
    for source,expected in protocol['source_hashes'].items():
        assert hashlib.sha256((HERE.parent/source).read_bytes()).hexdigest()==expected,source
    assert sorted(int(p.stem) for p in (HERE/'runs/validation').glob('*.json'))==protocol['network_ids']
    summary=json.loads((HERE/'analysis/summary.json').read_text())
    checks=json.loads((HERE/'analysis/numerical_checks.json').read_text())
    assert checks['status']=='PASS' and checks['gradient_relative_error']<1e-5
    assert not summary['unresolved'] and not summary['selected_failed'] and not summary['above_generating']
    count=0
    for index,nid in enumerate(protocol['network_ids']):
        d=json.loads((HERE/'runs/validation'/f'{nid}.json').read_text())
        assert d['complete'] and d['network_id']==nid
        assert [rep['noise_id'] for rep in d['noise_repeats']]==list(range(protocol['noise_repeats']))
        sel=d['selection']; ends=set(sel['nodes']['endpoints4'])
        assert len(ends)==4
        for policy,field in [('response5','response_scores'),('combination5','combination_scores')]:
            extra=set(sel['nodes'][policy])-ends
            assert len(extra)==1
            j=sel['candidate_sites'].index(extra.pop())
            close(sel[field][j],min(sel[field]))
        for rep in d['noise_repeats']:
            assert rep['q_true']==d['noise_repeats'][0]['q_true']
            assert [r['policy'] for r in rep['records']]==protocol['policies']
            assert not rep['unresolved_fit_flags']
            for r in rep['records']:
                assert r['nodes']==sel['nodes'][r['policy']]
                assert ends.issubset(r['nodes']) and len(r['nodes'])==(4 if r['policy']=='endpoints4' else 5)
                assert len(r['starts'])==9*(1+len(rep['audits']))
                assert r['best']['success']
                assert r['best']['objective']<=r['generating_objective']+1e-6
                close(r['best']['objective'],min(f['objective'] for f in r['starts']))
                close(r['response_mse'],statistics.mean((a-b)**2 for a,b in zip(r['best']['q_hat'],rep['q_true'])))
                close(r['endpoint_mse'],statistics.mean((r['best']['z'][i]-d['generating_z'][i])**2 for i in ends))
                for other in rep['records']:
                    if r['nodes']==other['nodes']: assert r['best']==other['best']
                diag=rep['diagnostics']['metrics'][r['policy']]
                close(sum(sum(row) for row in diag['blocks']),diag['response_variance'])
                close(sum(row[i] for i,row in enumerate(diag['internal_covariance']))/4,diag['internal_variance'])
                for key in ['response_variance','internal_variance']:
                    assert diag[key]<=rep['diagnostics']['metrics']['endpoints4'][key]+1e-10
                count+=1
        for metric,by_policy in summary['metrics'].items():
            for policy,values in by_policy.items():
                if metric.endswith('_variance'):
                    expected=statistics.mean(rep['diagnostics']['metrics'][policy][metric] for rep in d['noise_repeats'])
                else:
                    expected=statistics.mean(next(r for r in rep['records'] if r['policy']==policy)[metric] for rep in d['noise_repeats'])
                close(values[index],expected)
    a=summary['metrics']['response_mse']['response5']; b=summary['metrics']['response_mse']['random5']
    close(summary['primary']['change_pct'],100*(statistics.mean(a)/statistics.mean(b)-1))
    refined=json.loads((HERE/'analysis/integration_check.json').read_text())
    assert refined['n']==len(protocol['network_ids']) and abs(refined['primary_effect_drift_percentage_points'])<.1
    for stage in ['historical','validation']:
        expected_ids=protocol['historical_diagnostic_ids'] if stage=='historical' else protocol['network_ids']
        for nid in expected_ids:
            d=json.loads((HERE/'runs'/f'{stage}_error_decomposition'/f'{nid}.json').read_text())
            for rep in d['repeats']:
                for policy,result in rep.items():
                    q=result['hybrid_responses']; c=result['contributions']; blocks=result['squared_error_blocks']
                    for k in range(3):close(sum(row[k] for row in c),q[7][k]-q[0][k])
                    close(sum(sum(row) for row in blocks),result['mse'])
                    close(statistics.mean((x-y)**2 for x,y in zip(q[7],q[0])),result['mse'])
    return dict(status='PASS',independent_networks=len(protocol['network_ids']),retained_policy_records=count,
                scope='Frozen sources, complete paired cohorts, exact fitted-error aggregation and covariance-block identities')


if __name__=='__main__': print(json.dumps(main(),indent=2))
