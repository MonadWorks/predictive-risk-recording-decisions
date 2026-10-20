"""Retrospective fitting sensitivity; all frozen primary outputs stay unchanged.

Generating parameters only flag a certifiably suboptimal MAP objective. Every
selector for the flagged dataset receives the same additional prior starts;
truth is never a starting point or a fit-selection criterion.
"""
from common import *
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone

def worker(key):
    nid,tid,nid_noise=key;dest=HERE/f'runs/method_fit_audit/{nid}_{tid}_{nid_noise}.json'
    if dest.exists():return dict(dataset=key,cached=True)
    cfg,c=case_for(nid);theta,y,eps,trueq=data_for(c,cfg,tid,nid_noise)
    raw=json.loads((HERE/f'runs/method_validation/{nid}.json').read_text());records=[];cache={}
    rng=seeded(94031,nid);starts=[*.25*rng.normal(size=(4,c['model'].P)),*rng.normal(size=(4,c['model'].P))]
    for old in [r for r in raw['records'] if r['truth_id']==tid and r['noise_id']==nid_noise]:
        nodes=old['nodes'];keynodes=tuple(nodes)
        if keynodes not in cache:
            p=Problem(c,cfg,nodes,y[:,:,nodes]+cfg['noise_sd']*eps[:,:,nodes],cfg['noise_sd'])
            fits=[p.fit(np.array(old['best']['z']),600)]+[p.fit(s) for s in starts]
            best=min([old['best']]+fits,key=lambda r:r['objective']);cache[keynodes]=(best,fits)
        best,fits=cache[keynodes]
        records.append(dict(policy=old['policy'],best=best,additional_fits=fits,original_best=old['best'],
            teacher_objective=old['teacher_objective'],mse=float(np.mean((np.array(best['q_hat'])-trueq)**2))))
    dump(dest,dict(network_id=nid,truth_id=tid,noise_id=nid_noise,complete=True,records=records))
    return dict(dataset=key,complete=True)

def main():
    raw=[json.loads((HERE/f'runs/method_validation/{n}.json').read_text()) for n in range(45000,45040)]
    keys=sorted(set((d['network_id'],r['truth_id'],r['noise_id']) for d in raw for r in d['records'] if r['best']['objective']>r['teacher_objective']+.001))
    protocol=HERE/'protocols/method_fit_audit.json'
    if not protocol.exists():dump(protocol,dict(created_utc=datetime.now(timezone.utc).isoformat(),datasets=keys,
        reason='Check method effects against certified optimization failures in frozen results',
        starts='eight additional common public-prior starts; refine old best with 600-evaluation cap',
        seed=94031,scope='retrospective numerical diagnostic, not replacement of prespecified results'))
    with ProcessPoolExecutor(3) as ex:
        for f in as_completed([ex.submit(worker,k) for k in keys]):print(json.dumps(f.result()),flush=True)
    lookup={}
    for key in keys:
        nid,tid,noiseid=key;d=json.loads((HERE/f'runs/method_fit_audit/{nid}_{tid}_{noiseid}.json').read_text())
        for r in d['records']:lookup[(nid,tid,noiseid,r['policy'])]=r
    policies=['local','ensemble','prior_cov','prior_cv','random'];metrics={p:[] for p in policies};audit={p:[] for p in policies}
    for d in raw:
        for p in policies:
            rr=[lookup.get((d['network_id'],r['truth_id'],r['noise_id'],p),r) for r in d['records'] if r['policy']==p]
            metrics[p].append(float(np.mean([r['mse'] for r in rr])))
            audit[p].extend([r['best']['objective']>r['teacher_objective']+.001 for r in rr])
    comparisons={a+'_vs_'+b:bootstrap_change(metrics[a],metrics[b]) for a,b in [('prior_cv','local'),('prior_cov','local'),('ensemble','local'),('prior_cov','ensemble'),('prior_cov','random')]}
    dump(HERE/'analysis/method_fit_audit.json',dict(datasets=len(keys),metrics=metrics,comparisons=comparisons,
        certified_suboptimal_remaining={p:sum(v) for p,v in audit.items()},scope='retrospective common-start optimization sensitivity'))
    print(json.dumps(comparisons,indent=2))
if __name__=='__main__':main()
