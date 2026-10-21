"""Exploratory finite-error decomposition of saved fits, with all cross terms.

Generative gains are used only for this retrospective evaluation. This module
does not select recordings or change any fits or prespecified comparisons.
"""
from pathlib import Path
import sys, json, math
HERE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(HERE/'code'))
from followup6 import np, dump, case_for, combination_rows, POLICIES
from analyze6 import contrast, mean_interval
import argparse


def finite_error(case, truth, fitted):
    ends,_,_,basis=combination_rows(case)
    error=fitted-truth
    endpoint=np.zeros_like(error); endpoint[ends]=error[ends]
    internal=np.einsum('ai,i,aj->j',basis,error,basis)
    parts=np.array([endpoint,internal,error-endpoint-internal])
    hybrid=[]
    for mask in range(8):
        z=truth+sum((parts[i] for i in range(3) if mask & (1<<i)),np.zeros_like(truth))
        q,_=case['model'].responses(case['mu']+case['sd']*z,case['intervention'])
        hybrid.append(q[case['readouts']])
    hybrid=np.array(hybrid)
    contribution=np.zeros((3,3))
    for i in range(3):
        for mask in range(8):
            if mask & (1<<i):continue
            size=mask.bit_count()
            weight=math.factorial(size)*math.factorial(2-size)/math.factorial(3)
            contribution[i]+=weight*(hybrid[mask|(1<<i)]-hybrid[mask])
    assert np.allclose(contribution.sum(0),hybrid[7]-hybrid[0],rtol=1e-8,atol=1e-12)
    blocks=np.einsum('ik,jk->ij',contribution,contribution)/3
    mse=float(np.mean((hybrid[7]-hybrid[0])**2))
    assert np.isclose(blocks.sum(),mse,rtol=1e-8,atol=1e-12)
    return dict(hybrid_responses=hybrid.tolist(),contributions=contribution.tolist(),
                squared_error_blocks=blocks.tolist(),mse=mse)


def analyze(stage, cache_only=False):
    if stage=='historical':
        ids=list(range(60000,60040)); root=HERE.parent/'round5/runs/validation'
    else:
        ids=json.loads((HERE/'protocols/task_aligned_recording.json').read_text())['network_ids']
        root=HERE/'runs/validation'
    if cache_only:
        ids=[nid for nid in ids if (root/f'{nid}.json').exists()]
    networks=[]
    for nid in ids:
        destination=HERE/'runs'/f'{stage}_error_decomposition'/f'{nid}.json'
        original=json.loads((root/f'{nid}.json').read_text())
        repeats=[dict(records=original['records'])] if stage=='historical' else original['noise_repeats']
        if destination.exists():
            networks.append(json.loads(destination.read_text()));continue
        cfg,case=case_for(nid)
        truth=np.asarray(original['generating_z']); records=[]
        for repeat_id,repeat in enumerate(repeats):
            policies={r['policy']:r for r in repeat['records']}
            row={}
            for policy in POLICIES:
                source=policies[policy]
                result=finite_error(case,truth,np.asarray(source['best']['z']))
                assert np.isclose(result['mse'],source['response_mse'],rtol=1e-8,atol=1e-12)
                row[policy]=result
            records.append(row)
        d=dict(network_id=nid,scope='Exploratory finite parameter-error decomposition; all cross terms retained',repeats=records)
        dump(destination,d);networks.append(d)
    if cache_only:
        print(json.dumps(dict(stage=stage,cached_networks=len(networks))))
        return
    blocks={p:np.array([np.mean([r[p]['squared_error_blocks'] for r in d['repeats']],axis=0) for d in networks]) for p in POLICIES}
    comparisons={}
    for a,b in [('response5','random5'),('combination5','random5'),('response5','combination5')]:
        delta=blocks[a]-blocks[b]
        result={name:mean_interval(delta[:,i,i]) for i,name in enumerate(['endpoint','internal','orthogonal'])}
        result['cross']=mean_interval(delta.sum((1,2))-np.trace(delta,axis1=1,axis2=2))
        result['total']=mean_interval(delta.sum((1,2)))
        comparisons[f'{a}_vs_{b}']=result
    noise_decomposition={}
    if stage=='validation':
        per_policy={p:dict(squared_bias=[],noise_variance=[]) for p in POLICIES}
        for nid in ids:
            d=json.loads((root/f'{nid}.json').read_text())
            truthq=np.asarray(d['noise_repeats'][0]['q_true'])
            for p in POLICIES:
                q=np.array([next(r for r in rep['records'] if r['policy']==p)['best']['q_hat'] for rep in d['noise_repeats']])
                variance=float(np.var(q,axis=0,ddof=1).mean())
                bias=float(np.mean((q.mean(0)-truthq)**2)-variance/len(q))
                assert np.isclose(bias+variance,np.mean((q-truthq)**2),rtol=1e-9,atol=1e-12)
                per_policy[p]['squared_bias'].append(bias);per_policy[p]['noise_variance'].append(variance)
        noise_decomposition=dict(values=per_policy,description='Unbiased noise-replicate estimates; squared-bias estimates can be negative for individual networks',
            contrasts={f'{a}_vs_{b}':{m:mean_interval(np.asarray(per_policy[a][m])-np.asarray(per_policy[b][m])) for m in ['squared_bias','noise_variance']}
                for a,b in [('response5','random5'),('combination5','random5'),('response5','combination5')]})
    out=dict(stage=stage,n=len(ids),network_ids=ids,
        scope='Exploratory decomposition of realised error, distinct from the shared-reference covariance diagnostic',
        block_order=['endpoint','internal','orthogonal'],blocks={p:b.tolist() for p,b in blocks.items()},
        comparisons=comparisons,noise_decomposition=noise_decomposition)
    dump(HERE/'analysis'/f'{stage}_error_decomposition.json',out)
    print(json.dumps(dict(stage=stage,n=len(ids),comparisons=comparisons,noise_decomposition=noise_decomposition.get('contrasts',{})),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['historical','validation'])
    parser.add_argument('--cache-only',action='store_true')
    args=parser.parse_args();analyze(args.stage,args.cache_only)
