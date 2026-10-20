"""Resolve failed or non-nested wider-threshold searches, preserving raw output."""
from common import *
from fast_values import FastProblem
from scipy.linalg import solve_triangular
from final_audit import envelope

def main():
    logs=[]
    for nid in range(40000,40008):
        source=HERE/f'runs/threshold_check/{nid}.json';dest=HERE/f'runs/threshold_refined/{nid}.json'
        if dest.exists():continue
        d=json.loads(source.read_text());base=json.loads((HERE/f'runs/profile_validation/{nid}.json').read_text())
        cfg,case=case_for(nid);theta,y,eps,trueq=data_for(case,cfg)
        for r in d['records']:
            b=next(x for x in base['records'] if x['policy']==r['policy']);envelope(b)
            sigma=np.array(b['sigma']);nodes=b['nodes'];p=FastProblem(case,cfg,nodes,y[:,:,nodes]+sigma*eps[:,:,nodes],sigma)
            z=np.array(r['best']['z']);cost=r['best']['objective'];delta=r['profile']['delta'];j=p.evaluate(z)['jac']
            H=np.einsum('ki,kj->ij',j,j);B=solve_triangular(np.linalg.cholesky(H).T,np.eye(len(z)),lower=False)
            for s,small in zip(r['profile']['searches'],b['profile']['searches']):
                old=s['chosen'];k=s['target'];sign=s['sign'];more=sign*small['chosen']['q']>sign*old['q']+1e-9
                if old['success'] and not more:continue
                start=small['chosen'] if more else old;v0=np.linalg.solve(B,np.array(start['z'])-z)
                def full(v):return z+np.einsum('ij,j->i',B,v)
                g=np.einsum('i,ij->j',p.response(z)['g'][k],B);scale=max(np.linalg.norm(g),1e-8)
                f=minimize(lambda v:-sign*p.q_value(full(v))[k]/scale,v0,
                    jac=lambda v:-sign*np.einsum('i,ij->j',p.response(full(v))['g'][k],B)/scale,
                    method='SLSQP',constraints=[dict(type='ineq',fun=lambda v:(cost+delta-p.cost_value(full(v)))/delta,
                    jac=lambda v:-np.einsum('i,ij->j',p.evaluate(full(v))['grad'],B)/delta)],
                    options=dict(maxiter=300,ftol=1e-9))
                new=dict(z=full(f.x).tolist(),q=float(p.q_value(full(f.x))[k]),cost=float(p.cost_value(full(f.x))),
                    success=bool(f.success),feasible=bool(p.cost_value(full(f.x))<=cost+delta+1e-5),nit=int(f.nit),
                    message=str(f.message),source='refined_slsqp',start='known feasible delta2 extreme' if more else 'original failed extreme')
                s['attempts'].append(new)
                if new['feasible'] and sign*new['q']>=sign*old['q']-1e-8:s['chosen']=new
                logs.append(dict(network_id=nid,policy=r['policy'],target=k,sign=sign,success=new['success'],feasible=new['feasible'],old_q=old['q'],new_q=new['q'],iterations=new['nit']))
                print(json.dumps(logs[-1]),flush=True)
            r['profile']['lower']=[s['chosen']['q'] for s in r['profile']['searches'] if s['sign']==-1]
            r['profile']['upper']=[s['chosen']['q'] for s in r['profile']['searches'] if s['sign']==1]
            r['profile']['width']=(np.array(r['profile']['upper'])-r['profile']['lower']).tolist()
        dump(dest,d)
    dump(HERE/'analysis/threshold_refinement.json',dict(reason='Optimizer failure or failure to include a known feasible narrower-threshold point',records=logs))
if __name__=='__main__':main()
