"""Read-only checks for the complete planned round-four records."""
from pathlib import Path
import json,hashlib,math,statistics
HERE=Path(__file__).resolve().parent.parent

def load(p):return json.loads((HERE/p).read_text())
def close(a,b):assert math.isclose(a,b,rel_tol=2e-10,abs_tol=1e-13),(a,b)
def fit(r,nfits=9):
    close(r['mse'],statistics.mean((a-b)**2 for a,b in zip(r['best']['q_hat'],r['q_true'])))
    close(r['best']['objective'],min(f['objective'] for f in r['fits']))
    assert len(r['fits'])==nfits
    assert all(math.isfinite(x) for f in r['fits'] for x in f['z'])

def main():
    for name in ['robustness','allocation','mechanism','combination_validation','oracle_matched_control','oracle_data_fit_audit']:
        plan=load(f'protocols/{name}.json')
        for file,h in plan.get('source_hashes',plan.get('sources',{})).items():
            assert hashlib.sha256((HERE/'code'/file).read_bytes()).hexdigest()==h,file
    counts={};conditions=load('protocols/robustness.json')['conditions']
    for stage in ['robustness','oracle_combinations','allocation','mechanism','mechanism_validation','oracle_matched_control']:
        ids=range(40000,40040) if stage=='mechanism' else range(55000,55040) if stage=='allocation' else range(50000,50040)
        count=0
        for nid in ids:
            paths=[f'runs/{stage}/{nid}_{c}.json' for c in conditions] if stage=='robustness' else [f'runs/{stage}/{nid}.json']
            for path in paths:
                d=load(path);assert d['complete'] and d['network_id']==nid;count+=1
                if stage.startswith('mechanism'):
                    assert d['max_identity_error']<1e-9
                    for r in d['records']:
                        for v in r['combinations'].values():
                            assert 0<=v['gradient_fraction']<=1+1e-10
                            assert all(x['max_constraint_error']<1e-10 for x in v['perturbations'].values())
                    continue
                for r in d['records']:
                    fit(r)
                    if stage in ['oracle_combinations','oracle_matched_control']:assert r['best']['constraint_error']<1e-10
                    else:assert len(r['nodes'])==(5 if stage=='robustness' else r['budget'])
                if stage=='robustness':assert len(d['records'])==2
                elif stage=='oracle_combinations':assert len(d['records'])==5
                elif stage=='oracle_matched_control':assert len(d['records'])==1
                else:
                    assert len(d['records'])==36
                    for r in d['records']:
                        same=[x for x in d['records'] if x['nodes']==r['nodes'] and x['precision']==r['precision']]
                        assert all(x['best']==r['best'] for x in same)
                    for b in [2,3]:
                        for precision in ['uniform','stimulus_noisy','readouts_noisy']:
                            r={x['policy']:x for x in d['designs'] if x['budget']==b and x['precision']==precision}
                            assert r['endpoint_pair']['ensemble_risk']<=r['ensemble_greedy']['ensemble_risk']+1e-10
                            assert r['endpoint_pair']['ensemble_risk']<=r['endpoint_joint']['ensemble_risk']+1e-10
        counts[stage]=count
    # Recompute the estimands independently with the standard library.
    for stage,summary in [('oracle_combinations','oracle_combinations_summary'),('allocation','allocation_summary')]:
        out=load(f'analysis/{summary}.json')
        ids=range(55000,55040) if stage=='allocation' else range(50000,50040)
        for p,values in out['metrics'].items():
            expected=[statistics.mean(r['mse'] for r in load(f'runs/{stage}/{nid}.json')['records'] if r['policy']==p) for nid in ids]
            for a,b in zip(values,expected):close(a,b)
        for key,c in out['comparisons'].items():
            a,b=key.split('_vs_');close(c['change_pct'],100*(statistics.mean(out['metrics'][a])/statistics.mean(out['metrics'][b])-1))
    control=load('analysis/oracle_matched_control_summary.json')
    close(control['comparison']['change_pct'],100*(statistics.mean(control['metrics']['endpoints_recurrence8'])/statistics.mean(control['metrics']['endpoint_ordinary8'])-1))
    for value,nid in zip(control['metrics']['endpoint_ordinary8'],range(50000,50040)):
        close(value,load(f'runs/oracle_matched_control/{nid}.json')['records'][0]['mse'])
    audited=load('analysis/oracle_data_fit_audit_summary.json')
    for nid in audited['audited_networks']:
        d=load(f'runs/oracle_data_fit_audit/{nid}.json');assert d['complete'] and len(d['records'])==6
        for r in d['records']:fit(r,26)
    for p,values in audited['metrics'].items():
        for value,nid in zip(values,range(50000,50040)):
            stage='oracle_data_fit_audit' if nid in audited['audited_networks'] else 'oracle_matched_control' if p=='endpoint_ordinary8' else 'oracle_combinations'
            close(value,next(r['mse'] for r in load(f'runs/{stage}/{nid}.json')['records'] if r['policy']==p))
    assert audited['failed_selected']==0 and audited['above_generating']==0
    counts['oracle_data_fit_audit']=len(audited['audited_networks'])
    for nid in range(50000,50040):assert load(f'runs/integration/{nid}.json')['complete']
    counts['integration']=40
    out=load('analysis/robustness_summary.json')
    fine=load('analysis/integration_summary.json')
    assert fine['matrix_product_max_relative_error']<1e-12
    for c,d in out.items():
        for p,values in d['metrics'].items():
            expected=[next(r['mse'] for r in load(f'runs/robustness/{nid}_{c}.json')['records'] if r['policy']==p) for nid in range(50000,50040)]
            for a,b in zip(values,expected):close(a,b)
        close(d['comparison']['change_pct'],100*(statistics.mean(d['metrics']['both'])/statistics.mean(d['metrics']['neither'])-1))
    for d in load('analysis/numerical_checks.json').values():
        assert d['gradient_relative_error']<1e-6 and d['response_gradient_relative_error']<1e-6
        assert d['refinement_relative_error']<1e-4
    assert load('analysis/allocation_checks.json')['original_formula_relative_error']<1e-10
    return dict(status='PASS',base_network_ids_added=80,completed_files=counts,
                scope='Frozen sources, all planned IDs, common fits, MSE identities, exact-factor reconstruction and gain constraints')
if __name__=='__main__':print(json.dumps(main(),indent=2))
