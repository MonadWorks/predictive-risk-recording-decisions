"""Check held-out response evaluation at twice the integration resolution."""
from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(HERE/'code'))
from followup6 import np,dump,case_for,POLICIES


def main():
    protocol=json.loads((HERE/'protocols/task_aligned_recording.json').read_text())
    original=json.loads((HERE/'analysis/summary.json').read_text())
    mse={p:[] for p in POLICIES}; drifts=[]; per_network=[]
    for nid in protocol['network_ids']:
        d=json.loads((HERE/'runs/validation'/f'{nid}.json').read_text())
        _,case=case_for(nid);m=case['model'];m.substeps=4
        trueq,_=m.responses(case['mu']+case['sd']*np.asarray(d['generating_z']),case['intervention'])
        trueq=trueq[case['readouts']]
        oldtrue=np.asarray(d['noise_repeats'][0]['q_true'])
        delta=[float(np.linalg.norm(trueq-oldtrue))]
        per_policy={p:[] for p in POLICIES}
        for rep in d['noise_repeats']:
            for r in rep['records']:
                q,_=m.responses(case['mu']+case['sd']*np.asarray(r['best']['z']),case['intervention'])
                q=q[case['readouts']]
                delta.append(float(np.linalg.norm(q-np.asarray(r['best']['q_hat']))))
                per_policy[r['policy']].append(float(np.mean((q-trueq)**2)))
        for p in POLICIES:mse[p].append(float(np.mean(per_policy[p])))
        drifts.extend(delta)
        per_network.append(dict(network_id=nid,max_response_drift=max(delta),mse={p:mse[p][-1] for p in POLICIES}))
    effect=100*(np.mean(mse['response5'])/np.mean(mse['random5'])-1)
    change=effect-original['primary']['change_pct']
    out=dict(scope='Refined target evaluation at fixed fitted gains; calibration fits are unchanged',
             n=len(per_network),substeps=4,primary_change_pct=float(effect),
             primary_effect_drift_percentage_points=float(change),
             max_response_vector_drift=max(drifts),networks=per_network)
    dump(HERE/'analysis/integration_check.json',out)
    assert abs(change)<.1,change
    print(json.dumps({k:v for k,v in out.items() if k!='networks'},indent=2))


if __name__=='__main__':main()
