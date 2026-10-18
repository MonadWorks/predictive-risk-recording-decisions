"""Existing local predictive-risk criteria, averaged over a common prior set.

No posterior-predictive or new-optimal-design claim. Each particle is solved
separately and then averaged. All calculations use public model/prior only.
"""
import time
import numpy as np
from models import seeded


def gram(a):return np.einsum('...ki,...kj->...ij',a,a)


def build_bank(case,cfg):
    start=time.perf_counter();m=case['model'];sd=case['sd'];mu=case['mu'];P=m.P
    draws=seeded(cfg['design_seed'],case['network_id']).normal(size=(cfg['ensemble_size'],P))
    particles=np.vstack([mu,mu+sd*draws])
    infos=[];targets=[];vectors=[];glist=[];activity=None
    for l,theta in enumerate(particles):
        _,D=m.simulate(theta,case['train'],True)
        d=D[:,::cfg['sample_stride']]
        F=d.transpose(2,0,1,3).reshape(m.N,-1,P)*sd[None,None,:]/cfg['noise_sd']
        info=gram(F)
        Q,G=m.responses(theta,case['intervention'],True)
        g=G[case['readouts']]*sd[None,:]
        infos.append(info);glist.append(g)
        targets.append(np.einsum('ki,kj->kij',g,g));vectors.append(gram(g)/len(g))
        if l==0:
            A=d.reshape(-1,P)*sd[None,:]
            activity=gram(A)/len(A)
    bank=dict(info=np.asarray(infos),goal=np.asarray(targets),vector=np.asarray(vectors),
              gradients=np.asarray(glist),activity=activity,particles=particles)
    # Independent Monte Carlo task scale shared across every design; not truth.
    mc=seeded(cfg['scale_seed'],case['network_id']).normal(size=(cfg['scale_samples'],P))
    qq=[]
    for z in mc:
        Q,_=m.responses(mu+sd*z,case['intervention'])
        qq.append(Q[case['readouts']])
    bank['prior_q_variance']=np.var(qq,axis=0,ddof=1)
    bank['prior_q_mean']=np.mean(qq,axis=0)
    bank['seconds']=time.perf_counter()-start
    assert np.isfinite(bank['info']).all() and np.isfinite(bank['goal']).all()
    return bank


def choose(info,W,pool,budget):
    """Deterministic greedy; linear solves for each prior particle/candidate."""
    L,N,P,_=info.shape;H=np.tile(np.eye(P),(L,1,1));selected=[]
    costs=[]
    for _ in range(budget):
        candidates=np.array([i for i in pool if i not in selected],dtype=np.int64)
        Hs=H[:,None,:,:]+info[:,candidates]
        C=np.linalg.solve(Hs,np.broadcast_to(np.eye(P),Hs.shape))
        risk=np.mean(np.einsum('lcij,lji->lc',C,W),axis=0)
        assert np.isfinite(risk).all()
        j=int(np.argmin(risk));node=int(candidates[j])
        selected.append(node);costs.append(float(risk[j]));H+=info[:,node]
    return selected,costs


def risks_for_set(bank,nodes):
    P=bank['info'].shape[-1]
    H=np.eye(P)[None]+np.sum(bank['info'][:,nodes],axis=1)
    C=np.linalg.solve(H,np.broadcast_to(np.eye(P),H.shape))
    g=bank['gradients'];v=np.einsum('lkp,lpq,lkq->lk',g,C,g)
    return v[0],np.mean(v[1:],axis=0)


def recording_designs(case,cfg,bank,pool_name,budget):
    m=case['model'];K=len(case['readouts'])
    excluded=set([case['stim'],*case['readouts'].tolist()])
    pool=[i for i in range(m.N) if pool_name=='all' or i not in excluded]
    if budget>len(pool):raise ValueError('recording budget exceeds common feasible pool')
    designs=[]
    for method in cfg['methods']:
        start=time.perf_counter()
        if method=='random':
            for rep in range(cfg['random_sets']):
                tick=time.perf_counter()
                # Prefixes give nested budgets; same random sets across tasks.
                perm=seeded(cfg['random_seed']+rep,case['network_id']).permutation(pool)
                nodes=perm[:budget].tolist();nom,ens=risks_for_set(bank,nodes)
                designs.append(dict(method=method,target=-1,replicate=rep,nodes=nodes,
                   risk_nominal=nom,risk_ensemble=ens,seconds=time.perf_counter()-tick))
            continue
        indices=[0] if method.startswith('local') else list(range(1,len(bank['particles'])))
        tasks=range(K) if method.endswith('scalar') else [-1]
        for target in tasks:
            tick=time.perf_counter()
            if method.endswith('scalar'):W=bank['goal'][indices,target]
            elif method.endswith('vector'):W=bank['vector'][indices]
            elif method=='local_activity':W=bank['activity'][None]
            else:raise ValueError(method)
            nodes,costs=choose(bank['info'][indices],W,pool,budget)
            nom,ens=risks_for_set(bank,nodes)
            designs.append(dict(method=method,target=target,replicate=0,nodes=nodes,
                risk_nominal=nom,risk_ensemble=ens,greedy_risk_path=costs,seconds=time.perf_counter()-tick))
    return designs
