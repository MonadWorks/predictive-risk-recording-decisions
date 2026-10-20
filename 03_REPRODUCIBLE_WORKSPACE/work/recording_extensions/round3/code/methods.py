"""Prospective test of existing covariance design and a held-out-prior variant.

All design particles are public-prior simulations. No realized observation or
teacher is available to the selector. Both remain methodological candidates,
not claims of a newly invented general experimental-design principle.
"""
from common import *
from design import build_bank,choose
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse

def joint_bank(case,cfg):
    m=case['model'];nid=case['network_id'];P=m.P;L=cfg['ensemble_size']
    train=seeded(cfg['design_seed'],nid).normal(size=(L,P))
    valid=seeded(93713,nid).normal(size=(L,P))
    yy=[];qq=[];tick=time.perf_counter()
    for z in np.vstack([train,valid]):
        theta=case['mu']+case['sd']*z
        y,_=m.simulate(theta,case['train']);q,_=m.responses(theta,case['intervention'])
        yy.append(y[:,::cfg['sample_stride']].transpose(2,0,1).reshape(m.N,-1))
        qq.append(q[case['readouts']])
    yy=np.asarray(yy)/cfg['noise_sd'];qq=np.asarray(qq)
    mean=yy[:L].mean(0);qm=qq[:L].mean(0)
    X=(yy[:L]-mean).transpose(1,0,2)/np.sqrt(L-1)
    V=(yy[L:]-mean).transpose(1,0,2)/np.sqrt(L-1)
    K=np.einsum('nlt,nmt->nlm',X,X);cross=np.einsum('nlt,nmt->nlm',V,X)
    return dict(K=K,cross=cross,q=qq[:L]-qm,qv=qq[L:]-qm,L=L,seconds=time.perf_counter()-tick)

def select_joint(bank,pool,budget,crossvalidate):
    L=bank['L'];K=np.zeros((L,L));cross=np.zeros((L,L));selected=[];path=[]
    for step in range(budget):
        ids=np.array([n for n in pool if n not in selected]);Ks=K[None]+bank['K'][ids]
        A=np.linalg.solve(Ks+np.eye(L)[None],np.broadcast_to(bank['q'],(len(ids),L,3)))
        if crossvalidate:
            pred=np.einsum('nlm,nmk->nlk',cross[None]+bank['cross'][ids],A)
            bias=np.mean((pred-bank['qv'][None])**2,axis=(1,2))
            noise=np.einsum('nli,nlm,nmi->n',A,Ks,A)/(3*(L-1))
            score=bias+noise
        else:
            score=np.einsum('li,nli->n',bank['q'],A)/(3*(L-1))
        ix=int(np.argmin(score));node=int(ids[ix]);selected.append(node)
        path.append(float(score[ix]));K+=bank['K'][node];cross+=bank['cross'][node]
    return selected,path

def make_designs(case,cfg):
    ends={case['stim'],*case['readouts']};pool=[i for i in range(case['model'].N) if i not in ends]
    d=[];bank=build_bank(case,cfg)
    for label,indices in [('local',slice(0,1)),('ensemble',slice(1,None))]:
        tick=time.perf_counter();nodes,path=choose(bank['info'][indices],bank['vector'][indices],pool,5)
        d.append(dict(policy=label,nodes=sorted(nodes),path=path,selection_seconds=time.perf_counter()-tick,
                      shared_bank_seconds=bank['seconds']))
    del bank
    bank=joint_bank(case,cfg)
    for label,cv in [('prior_cov',False),('prior_cv',True)]:
        tick=time.perf_counter();nodes,path=select_joint(bank,pool,5,cv)
        d.append(dict(policy=label,nodes=sorted(nodes),path=path,selection_seconds=time.perf_counter()-tick,
                      shared_bank_seconds=bank['seconds']))
    d.append(dict(policy='random',nodes=sorted(seeded(cfg['random_seed'],case['network_id']).permutation(pool)[:5].tolist()),
                  selection_seconds=0.,shared_bank_seconds=0.))
    return d

def worker(nid,stage):
    dest=HERE/'runs'/stage/f'{nid}.json'
    if dest.exists():return dict(network_id=nid,cached=True)
    tick=time.perf_counter();cfg,case=case_for(nid);designs=make_designs(case,cfg)
    records=[];starts=starts_for(case)
    for tid in range(2):
        for noiseid in range(2):
            theta,clean,eps,trueq=data_for(case,cfg,tid,noiseid);cache={}
            for d in designs:
                nodes=d['nodes'];key=tuple(nodes)
                if key not in cache:
                    p=Problem(case,cfg,nodes,clean[:,:,nodes]+cfg['noise_sd']*eps[:,:,nodes],cfg['noise_sd'])
                    best,fits=p.multistart(starts)
                    teacher=float(p.evaluate((theta-case['mu'])/case['sd'])['cost'])
                    cache[key]=(best,fits,teacher)
                best,fits,teacher=cache[key]
                records.append(dict(network_id=nid,truth_id=tid,noise_id=noiseid,q_true=trueq.tolist(),
                    **d,best=best,fits=fits,teacher_objective=teacher,
                    mse=float(np.mean((np.asarray(best['q_hat'])-trueq)**2))))
    out=dict(network_id=nid,stage=stage,complete=True,seconds=time.perf_counter()-tick,designs=designs,records=records)
    dump(dest,out)
    return dict(network_id=nid,seconds=out['seconds'],mse={d['policy']:float(np.mean([r['mse'] for r in records if r['policy']==d['policy']])) for d in designs})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True);ap.add_argument('--start',type=int,required=True)
    ap.add_argument('--count',type=int,required=True);ap.add_argument('--workers',type=int,default=4);a=ap.parse_args()
    with ProcessPoolExecutor(a.workers) as ex:
        jobs=[ex.submit(worker,n,a.stage) for n in range(a.start,a.start+a.count)]
        for f in as_completed(jobs):print(json.dumps(f.result()),flush=True)
if __name__=='__main__':main()
