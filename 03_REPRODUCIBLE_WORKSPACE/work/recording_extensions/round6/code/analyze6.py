"""Network-cluster aggregation for the fixed fifth-recording follow-up."""
from pathlib import Path
import sys, json
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'code'))
from followup6 import np, dump, POLICIES


def contrast(a, b):
    a, b = np.asarray(a), np.asarray(b)
    ids = np.random.default_rng(20261021).integers(0, len(a), (30000, len(a)))
    ratios = a[ids].mean(1) / b[ids].mean(1)
    loo = [(np.sum(a)-x)/(np.sum(b)-y) for x, y in zip(a,b)]
    return dict(change_pct=float(100*(a.mean()/b.mean()-1)),
                ci95=(100*(np.percentile(ratios,[2.5,97.5])-1)).tolist(),
                mean_a=float(a.mean()), mean_b=float(b.mean()), wins=int(np.sum(a < b)),
                n=len(a), loo_pct=[float(100*(min(loo)-1)),float(100*(max(loo)-1))])


def mean_interval(values):
    a = np.asarray(values)
    ids = np.random.default_rng(20261022).integers(0, len(a), (30000,len(a)))
    return dict(mean=float(a.mean()), ci95=np.percentile(a[ids].mean(1),[2.5,97.5]).tolist())


def main():
    protocol=json.loads((HERE/'protocols/task_aligned_recording.json').read_text())
    data=[json.loads((HERE/'runs/validation'/f'{nid}.json').read_text()) for nid in protocol['network_ids']]
    assert all(d['complete'] and len(d['noise_repeats'])==protocol['noise_repeats'] for d in data)
    metrics={m:{p:[] for p in POLICIES} for m in ['response_mse','endpoint_mse','combination_mse','response_variance','internal_variance']}
    blocks={p:[] for p in POLICIES}
    finite_errors=[]
    for d in data:
        for p in POLICIES:
            rows=[next(r for r in rep['records'] if r['policy']==p) for rep in d['noise_repeats']]
            for m in ['response_mse','endpoint_mse','combination_mse']:
                metrics[m][p].append(float(np.mean([r[m] for r in rows])))
            for m in ['response_variance','internal_variance']:
                metrics[m][p].append(float(np.mean([rep['diagnostics']['metrics'][p][m] for rep in d['noise_repeats']])))
            blocks[p].append(np.mean([rep['diagnostics']['metrics'][p]['blocks'] for rep in d['noise_repeats']],axis=0).tolist())
        errors=[]
        for rep in d['noise_repeats']:
            modes=rep['diagnostics']['internal_modes']
            for radius_id in range(2):
                exact=np.array([m['local_slope'] for m in modes]); finite=np.array([m['finite'][radius_id]['response_slope'] for m in modes])
                errors.append(dict(radius=modes[0]['finite'][radius_id]['radius'], relative_error=float(np.linalg.norm(finite-exact)/max(np.linalg.norm(exact),1e-15))))
        finite_errors.append(errors)
    primary=contrast(metrics['response_mse']['response5'],metrics['response_mse']['random5'])
    secondary={}
    for a,b in [('response5','endpoints4'),('combination5','random5'),('response5','combination5'),('random5','endpoints4')]:
        secondary[f'{a}_vs_{b}']=contrast(metrics['response_mse'][a],metrics['response_mse'][b])
    diagnostic_contrasts={f'{m}/{a}_vs_{b}':contrast(metrics[m][a],metrics[m][b])
        for m in ['endpoint_mse','combination_mse','response_variance','internal_variance']
        for a,b in [('response5','random5'),('combination5','random5'),('response5','combination5')]}
    block_effects={}
    for a,b in [('response5','random5'),('combination5','random5'),('response5','combination5')]:
        delta=np.array(blocks[a])-np.array(blocks[b])
        effects={name:mean_interval(delta[:,i,i]) for i,name in enumerate(['endpoint','internal','orthogonal'])}
        effects['cross']=mean_interval(delta.sum((1,2))-np.trace(delta,axis1=1,axis2=2))
        effects['total']=mean_interval(delta.sum((1,2)))
        block_effects[f'{a}_vs_{b}']=effects
    records=[r for d in data for rep in d['noise_repeats'] for r in rep['records']]
    out=dict(network_ids=protocol['network_ids'],n=len(data),noise_repeats=protocol['noise_repeats'],
        primary=primary,secondary=secondary,metrics=metrics,diagnostic_contrasts=diagnostic_contrasts,
        covariance_blocks=blocks,block_effects=block_effects,finite_errors=finite_errors,
        same_site=sum(d['selection']['nodes']['response5']==d['selection']['nodes']['combination5'] for d in data),
        audit_repeats=sum(bool(rep['audits']) for d in data for rep in d['noise_repeats']),
        selected_failed=sum(not r['best']['success'] for r in records),
        above_generating=sum(r['best']['objective']>r['generating_objective']+1e-6 for r in records),
        unresolved=[dict(network_id=d['network_id'],noise_id=rep['noise_id'],flags=rep['unresolved_fit_flags']) for d in data for rep in d['noise_repeats'] if rep['unresolved_fit_flags']],
        seconds=sum(d['seconds'] for d in data))
    dump(HERE/'analysis/summary.json',out)
    print(json.dumps({k:out[k] for k in ['n','primary','secondary','diagnostic_contrasts','audit_repeats','selected_failed','above_generating','unresolved']},indent=2))
    return out


if __name__=='__main__': main()
