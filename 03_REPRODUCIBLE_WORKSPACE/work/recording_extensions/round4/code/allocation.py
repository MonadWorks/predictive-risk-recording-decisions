"""Endpoint-pair lookahead under limited budgets and unequal precision.

Uses an established ensemble local-risk objective. The candidate procedure
adds endpoint-pair starts to ordinary greedy selection; it is tested against
exact endpoint-subset enumeration and the same common nonlinear estimator.
"""
from common4 import *
from design import build_bank,choose
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse

class Risk:
    def __init__(self,info,g):self.info=info;self.g=g
    def scores(self,sets):
        out=[];P=self.info.shape[-1]
        for start in range(0,len(sets),12):
            batch=sets[start:start+12]
            h=np.array([np.eye(P)[None]+self.info[:,s].sum(1) for s in batch])
            rhs=np.broadcast_to(self.g.transpose(0,2,1)[None],(*h.shape[:2],P,3))
            solution=np.linalg.solve(h,rhs)
            out.extend(np.mean(np.einsum('lkp,blpk->bl',self.g,solution)/3,axis=1).tolist())
        return np.asarray(out)
    def greedy(self,pool,budget,prefix=()):
        selected=list(prefix);path=[]
        while len(selected)<budget:
            candidates=[s for s in pool if s not in selected]
            values=self.scores([selected+[s] for s in candidates]);i=int(np.argmin(values))
            selected.append(candidates[i]);path.append(float(values[i]))
        return selected,path

def design_family(case,cfg,bank,sigma):
    info=bank['info']*(cfg['noise_sd']/sigma)[None,:,None,None]**2
    ens=Risk(info[1:],bank['gradients'][1:]);nom=Risk(info[:1],bank['gradients'][:1])
    pool=list(range(case['model'].N));ends=[int(case['stim']),*map(int,case['readouts'])]
    tick=time.perf_counter();greedy,gpath=ens.greedy(pool,3);greedy_seconds=time.perf_counter()-tick
    tick=time.perf_counter();local,lpath=nom.greedy(pool,3);local_seconds=time.perf_counter()-tick
    random=seeded(95221,case['network_id']).permutation(pool).tolist()
    perm=seeded(95223,case['network_id']).permutation(case['readouts']).tolist()
    result=[]
    for budget in [2,3]:
        tick=time.perf_counter();candidates=[list(s) for s in combinations(ends,budget)]
        scores=ens.scores(candidates);e=candidates[int(np.argmin(scores))];exact_seconds=time.perf_counter()-tick
        tick=time.perf_counter();pairs=[list(s) for s in combinations(ends,2)]
        enriched=[greedy[:budget]]
        for pair in pairs:
            proposal=pair if budget==2 else ens.greedy(pool,budget,pair)[0]
            enriched.append(proposal)
        values=ens.scores(enriched);nodes=enriched[int(np.argmin(values))];pair_seconds=time.perf_counter()-tick
        assert values.min()<=values[0]+1e-12
        for policy,selected,seconds in [('endpoint_pair',nodes,greedy_seconds+pair_seconds),
            ('endpoint_joint',e,exact_seconds),('ensemble_greedy',greedy[:budget],greedy_seconds),
            ('nominal_greedy',local[:budget],local_seconds),('stimulus_first',[case['stim'],*perm[:budget-1]],0.),
            ('random_all',random[:budget],0.)]:
            result.append(dict(policy=policy,budget=budget,nodes=sorted(map(int,selected)),
                               selection_seconds=seconds,ensemble_risk=float(ens.scores([selected])[0])))
    return result

def worker(nid,stage):
    path=HERE/'runs'/stage/f'{nid}.json'
    if path.exists():return dict(network_id=nid,cached=True)
    tick=time.perf_counter();cfg,c,t,theta,y,eps,q=make_case(nid,'matched_rank2')
    bank=build_bank(c,cfg);records=[];all_designs=[];start_list=starts(nid)
    for precision in ['uniform','stimulus_noisy','readouts_noisy']:
        sigma=np.full(c['model'].N,.05)
        if precision=='stimulus_noisy':sigma[c['stim']]*=4
        elif precision=='readouts_noisy':sigma[c['readouts']]*=4
        designs=design_family(c,cfg,bank,sigma);cache={}
        for d in designs:
            key=tuple(d['nodes'])
            if key not in cache:
                p,r=fit_record(c,cfg,d['nodes'],y,eps,sigma,q,start_list)
                r['generating_latent_objective']=float(p.evaluate((theta-c['mu'])/c['sd'])['cost'])
                cache[key]=r
            records.append(dict(**cache[key],policy=d['policy'],budget=d['budget'],precision=precision))
            all_designs.append(dict(**d,precision=precision))
    out=dict(network_id=nid,complete=True,seconds=time.perf_counter()-tick,bank_seconds=bank['seconds'],
             stim=int(c['stim']),readouts=c['readouts'].tolist(),designs=all_designs,records=records)
    dump(path,out);return dict(network_id=nid,seconds=out['seconds'],unique_fits=len({(r['precision'],tuple(r['nodes'])) for r in records}))

def check():
    cfg,c,t,th,y,eps,q=make_case(49981,'matched_rank2');bank=build_bank(c,cfg)
    r=Risk(bank['info'][1:4],bank['gradients'][1:4]);pool=list(range(10))
    a,p=r.greedy(pool,2);b,q=choose(bank['info'][1:4],bank['vector'][1:4],pool,2)
    assert a==b and np.allclose(p,q,rtol=1e-10),(a,b,p,q)
    d=design_family(c,cfg,bank,np.full(c['model'].N,.05))
    for budget in [2,3]:
        p={x['policy']:x for x in d if x['budget']==budget}
        assert p['endpoint_pair']['ensemble_risk']<=p['ensemble_greedy']['ensemble_risk']+1e-12
        assert p['endpoint_pair']['ensemble_risk']<=p['endpoint_joint']['ensemble_risk']+1e-12
    out=dict(passed=True,selection=a,original_formula_relative_error=float(np.max(abs(np.asarray(r.greedy(pool,2)[1])/np.asarray(q)-1))))
    dump(HERE/'analysis/allocation_checks.json',out);print(json.dumps(out))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--start',type=int,default=55000)
    ap.add_argument('--count',type=int,default=40);ap.add_argument('--workers',type=int,default=2);ap.add_argument('--stage',default='allocation');a=ap.parse_args()
    if a.check:check()
    else:
        with ProcessPoolExecutor(a.workers) as ex:
            for f in as_completed([ex.submit(worker,n,a.stage) for n in range(a.start,a.start+a.count)]):print(json.dumps(f.result()),flush=True)
