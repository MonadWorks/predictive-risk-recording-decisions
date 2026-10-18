"""Read-only scientific consistency checks using only the standard library."""
from pathlib import Path
import hashlib,json,math,statistics
ROOT=Path(__file__).resolve().parent

def read(path):return json.loads((ROOT/path).read_text())
def close(a,b):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-14),(a,b)
def mean(x):return statistics.mean(x)
def check_mse(r,key='mse'):
    q=r.get('best',r).get('q_hat')
    if q is not None and 'q_true' in r:close(r[key],mean([(a-b)**2 for a,b in zip(q,r['q_true'])]))
def main():
    numerical={'models.py','design.py','inference.py','run.py','run_rank2.py','rank2_refined.py','run_mechanism.py'}
    for manifest in (ROOT/'runs').glob('*/*source_hashes.json'):
        for name,h in json.loads(manifest.read_text()).items():
            if name in numerical:assert hashlib.sha256((ROOT/'code'/name).read_bytes()).hexdigest()==h,name
    assert hashlib.sha256((ROOT/'round2/code/explore.py').read_bytes()).hexdigest()==read('round2/protocol.json')['code_sha256']
    for path,key in [('round3/protocols/frozen_validation.json','source_hashes'),('round3/protocols/preconditioning_amendment.json','hashes')]:
        for name,h in read(path)[key].items():assert hashlib.sha256((ROOT/'round3/code'/name).read_bytes()).hexdigest()==h,name
    ps=read('round3/analysis/profile_summary.json');ms=read('round3/analysis/method_summary.json');os=read('round3/analysis/oracle_summary.json')
    profile=[];method=[]
    for nid in range(40000,40040):
        d=read(f'round3/runs/profile_validation/{nid}.json');assert d['complete'] and len(d['records'])==4;profile.append(d)
        oracle=read(f'round3/runs/oracle_refit/{nid}.json');assert oracle['complete'] and len(oracle['records'])==4
        for r in d['records']:
            check_mse(r);assert len(set(r['nodes']))==5
            close(r['best']['objective'],min(x['objective'] for x in r['fits']))
            cap=r['best']['objective']+2
            for s in r['profile']['searches']:assert s['chosen']['cost']<=cap+1e-5
            # Include every already known feasible fit, matching final_audit.py.
            lo=list(r['profile']['lower']);hi=list(r['profile']['upper'])
            for f in r['fits']:
                if f['objective']<=cap+1e-5:
                    lo=[min(a,b) for a,b in zip(lo,f['q_hat'])];hi=[max(a,b) for a,b in zip(hi,f['q_hat'])]
            close(mean([(b-a)**2 for a,b in zip(lo,hi)]),ps['metrics'][r['policy']]['width2'][nid-40000])
            close(r['mse'],ps['metrics'][r['policy']]['mse'][nid-40000])
        for r in oracle['records']:close(r['mse'],os['metrics'][r['policy']][nid-40000])
    for nid in range(45000,45040):
        d=read(f'round3/runs/method_validation/{nid}.json');assert d['complete'] and len(d['records'])==20;method.append(d)
        for r in d['records']:
            check_mse(r);assert len(set(r['nodes']))==5
            close(r['best']['objective'],min(x['objective'] for x in r['fits']))
        for p in ms['metrics']:close(mean([r['mse'] for r in d['records'] if r['policy']==p]),ms['metrics'][p][nid-45000])
    for folder,summary,start in [('round2/runs/endpoint','endpoint_summary',20000),('round2/validation/runs/endpoint','validation_summary',30000)]:
        means=read(f'round2/analysis/{summary}.json')['network_means']
        for nid in range(start,start+40):
            rows=[json.loads(x) for x in (ROOT/f'{folder}/{nid}.jsonl').read_text().splitlines()]
            assert len(rows)==48
            for p in sorted({r['policy'] for r in rows}):close(mean([r['response_mse'] for r in rows if r['policy']==p]),means[p][nid-start])
    audit=read('round3/analysis/method_fit_audit.json');replacements={}
    for f in (ROOT/'round3/runs/method_fit_audit').glob('*.json'):
        d=json.loads(f.read_text())
        for r in d['records']:replacements[d['network_id'],d['truth_id'],d['noise_id'],r['policy']]=r
    assert len(replacements)==55
    for d in method:
        for p in audit['metrics']:
            vals=[replacements.get((d['network_id'],r['truth_id'],r['noise_id'],p),r)['mse'] for r in d['records'] if r['policy']==p]
            close(mean(vals),audit['metrics'][p][d['network_id']-45000])
    for summary,metrics,comparisons in [(ps,ps['metrics'],ps['comparisons'])]:
        for key,values in comparisons.items():
            a,b=key.split('_vs_')
            for metric,effect in values.items():close(effect['change_pct'],100*(mean(metrics[a][metric])/mean(metrics[b][metric])-1))
    for s in [ms,os,audit]:
        for key,effect in s['comparisons'].items():
            a,b=key.split('_vs_');close(effect['change_pct'],100*(mean(s['metrics'][a])/mean(s['metrics'][b])-1))
    return dict(status='PASS',independent_new_networks=160,mechanism_networks=40,method_networks=40,
                checked_endpoint_fit_records=3840,checked_mechanism_conditions=160,checked_method_records=800,
                checked_oracle_conditions=160,matched_fitting_audit_datasets=11,
                scope='Source freezes, raw-to-network aggregation, MSE identities and numerical feasibility; no new simulations')
if __name__=='__main__':print(json.dumps(main(),indent=2))
