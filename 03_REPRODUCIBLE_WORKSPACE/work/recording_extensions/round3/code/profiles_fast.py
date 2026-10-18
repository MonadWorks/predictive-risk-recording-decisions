"""Constrained response ranges in a MAP objective sublevel set.

These are numerical feasible ranges, not calibrated confidence intervals.
One dimensional directions of all three target responses are searched.
"""
from common import *
from fast_values import FastProblem as Problem
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
import argparse

def extremes(p,best,delta=2.,maxiter=160):
    z=np.asarray(best['z']);cost=best['objective'];e=p.evaluate(z)
    C=np.linalg.inv(np.einsum('ki,kj->ij',e['jac'],e['jac']))
    q=p.response(z)['q'].copy();G=p.response(z)['g'].copy()
    allout=[]
    for k in range(3):
        v=max(float(np.einsum('i,ij,j',G[k],C,G[k])),1e-16);scale=np.sqrt(v)
        d=np.einsum('ij,j->i',C,G[k])*np.sqrt(2*delta/v)
        for sign in [-1,1]:
            candidates=[dict(z=z.tolist(),q=float(q[k]),cost=cost,success=True,source='map')]
            attempts=[]
            for sid,x0 in enumerate([z,z+.6*sign*d]):
                f=minimize(lambda x:-sign*p.q_value(x)[k]/scale,x0,
                    jac=lambda x:-sign*p.response(x)['g'][k]/scale,method='SLSQP',
                    bounds=[(-np.sqrt(2*(cost+delta)),np.sqrt(2*(cost+delta)))]*len(z),
                    constraints=[dict(type='ineq',fun=lambda x:(cost+delta-p.cost_value(x))/delta,
                                      jac=lambda x:-p.evaluate(x)['grad']/delta)],
                    options=dict(maxiter=maxiter,ftol=1e-8))
                actual=p.evaluate(f.x)['cost'];val=float(p.response(f.x)['q'][k]);feasible=actual<=cost+delta+1e-5
                rec=dict(z=f.x.tolist(),q=val,cost=float(actual),success=bool(f.success),
                         feasible=bool(feasible),nit=int(f.nit),message=str(f.message),start=sid,source='slsqp')
                attempts.append(rec)
                if feasible and np.isfinite(val):candidates.append(rec)
            chosen=max(candidates,key=lambda c:sign*c['q'])
            allout.append(dict(target=k,sign=sign,chosen=chosen,attempts=attempts))
    lower=np.array([r['chosen']['q'] for r in allout if r['sign']==-1])
    upper=np.array([r['chosen']['q'] for r in allout if r['sign']==1])
    return dict(delta=delta,lower=lower.tolist(),upper=upper.tolist(),width=(upper-lower).tolist(),
                local_width=(2*np.sqrt(2*delta*np.einsum('ki,ij,kj->k',G,C,G))).tolist(),searches=allout)

def worker(nid,stage,policies):
    dest=HERE/'runs'/stage/f'{nid}.json';
    if dest.exists():return dict(network_id=nid,cached=True)
    cfg,case=case_for(nid);theta,clean,eps,trueq=data_for(case,cfg)
    tick=time.perf_counter();records=[]
    for policy in policies:
        nodes,ends=allocated_nodes(case,policy)
        factor=4. if policy=='both_noise4' else 16. if policy=='both_noise16' else 1.
        sigma=np.array([cfg['noise_sd']*(factor if i in ends else 1.) for i in nodes])
        obs=clean[:,:,nodes]+eps[:,:,nodes]*sigma
        p=Problem(case,cfg,nodes,obs,sigma);best,fits=p.multistart(starts_for(case))
        pr=extremes(p,best)
        # A lower objective discovered during a range search is evidence to refit,
        # not silently accepted as a globally optimal starting point.
        found=[a for s in pr['searches'] for a in s['attempts'] if a['cost']<best['objective']-.01]
        recenter=[]
        if found:
            new=p.fit(np.asarray(min(found,key=lambda a:a['cost'])['z']),600)
            recenter.append(new);fits.append(new);best=min(fits,key=lambda x:x['objective']);pr=extremes(p,best)
        rec=dict(network_id=nid,policy=policy,nodes=nodes,sigma=sigma.tolist(),q_true=trueq.tolist(),
            best=best,fits=fits,recenter=recenter,profile=pr,
            mse=float(np.mean((np.asarray(best['q_hat'])-trueq)**2)),
            teacher_objective=float(p.evaluate((theta-case['mu'])/case['sd'])['cost']))
        if stage=='profile_pilot':rec['profile_delta5']=extremes(p,best,5.)
        records.append(rec)
    out=dict(network_id=nid,complete=True,stage=stage,seconds=time.perf_counter()-tick,records=records)
    dump(dest,out)
    return dict(network_id=nid,seconds=out['seconds'],mse={r['policy']:r['mse'] for r in records},
                widths={r['policy']:float(np.mean(np.square(r['profile']['width']))) for r in records})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True);ap.add_argument('--start',type=int,required=True)
    ap.add_argument('--count',type=int,required=True);ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--policies',default='neither,both,both_noise4,both_noise16');a=ap.parse_args()
    with ProcessPoolExecutor(a.workers) as ex:
        jobs=[ex.submit(worker,n,a.stage,a.policies.split(',')) for n in range(a.start,a.start+a.count)]
        for f in as_completed(jobs):print(json.dumps(f.result()),flush=True)
if __name__=='__main__':main()
