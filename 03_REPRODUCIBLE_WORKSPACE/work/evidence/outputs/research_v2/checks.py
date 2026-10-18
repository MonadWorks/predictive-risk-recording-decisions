"""Meaningful scientific/numerical checks before result evaluation."""
import importlib.util,itertools,json,time
from pathlib import Path
import numpy as np
from models import public_case,generate_truth,Model
from design import build_bank,recording_designs,choose
from inference import fit_selected


def run_checks(cfg):
 start=time.perf_counter();report={}
 c=public_case(1899,cfg,cfg['conditions'][0]);m=c['model'];th=generate_truth(c,cfg,cfg['conditions'][0],0)
 R,D=m.simulate(th,c['train'],True)
 rng=np.random.default_rng(983);direction=rng.normal(size=m.P);direction/=np.linalg.norm(direction);h=1e-5
 plus,_=m.simulate(th+h*direction,c['train']);minus,_=m.simulate(th-h*direction,c['train'])
 fd=(plus-minus)/(2*h);an=np.einsum('ktnp,p->ktn',D,direction)
 err=float(np.linalg.norm(fd-an)/np.linalg.norm(fd));assert err<1e-6
 report['trajectory_derivative_relative_error']=err
 Q,G=m.responses(th,c['intervention'],True)
 plus,_=m.responses(th+h*direction,c['intervention']);minus,_=m.responses(th-h*direction,c['intervention'])
 fdq=(plus-minus)/(2*h);aq=G@direction
 errq=float(np.linalg.norm(fdq-aq)/max(np.linalg.norm(fdq),1e-15));assert errq<1e-6
 report['response_derivative_relative_error']=errq
 nodes=[9,2,7];rs,ds=m.simulate(th,c['train'],True,nodes)
 assert np.max(np.abs(rs-R[:,:,nodes]))<1e-12
 assert np.max(np.abs(ds-D[:,:,nodes]))<1e-12
 report['nonordered_observation_axis_match']=True
 # Independent previous NumPy implementation, same state and parameter meaning.
 spec=importlib.util.spec_from_file_location('oldpilot',Path(__file__).parents[1]/'pilot/pilot.py')
 old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
 r0,d0=old.simulate(th,m.J,c['train'],m.dt,True)
 report['independent_numpy_rate_max_error']=float(np.max(np.abs(R-r0)))
 report['independent_numpy_sensitivity_max_error']=float(np.max(np.abs(D-d0)))
 assert report['independent_numpy_sensitivity_max_error']<1e-10
 # Prior-particle aggregation must collapse to nominal when repeated identically.
 P=m.P;info=np.array([np.eye(P)[None].repeat(m.N,axis=0)])
 w=rng.normal(size=(P,P));w=np.einsum('ki,kj->ij',w,w)
 one,_=choose(info,w[None],list(range(m.N)),3)
 repeated,_=choose(np.repeat(info,4,axis=0),np.repeat(w[None],4,axis=0),list(range(m.N)),3)
 assert one==repeated;report['identical_particle_design_equivalence']=True
 bank=build_bank(c,cfg);d1=recording_designs(c,cfg,bank,'exclude_endpoints',3)
 # Changing theta true is impossible through this API: no true fields supplied.
 assert 'truth' not in c
 excluded=set([c['stim'],*c['readouts']])
 assert all(not excluded.intersection(d['nodes']) for d in d1)
 report['common_endpoint_pool_and_public_design_api']=True
 # Known linear paired-bias null, using independent existing implementation.
 qs=[];grads=[]
 for _ in range(5):
  b=rng.normal(0,.3,m.N);rr,dd=old.simulate(b,m.J,c['intervention'],m.dt,True,linear=True)
  qs.append(m.dt*np.sum(rr[1,:,c['readouts'][0]]-rr[0,:,c['readouts'][0]]))
  grads.append(m.dt*np.sum(dd[1,:,c['readouts'][0]]-dd[0,:,c['readouts'][0]],axis=0))
 report['linear_bias_null_range']=float(np.ptp(qs));report['linear_bias_null_gradient']=float(np.max(np.abs(grads)))
 assert np.ptp(qs)<1e-10 and np.max(np.abs(grads))<1e-10
 # Nontrivial exact subset audit; report greedy regret rather than assume zero.
 small=dict(cfg,neurons=6,targets=2,ensemble_size=4,scale_samples=16)
 sc=public_case(1898,small,cfg['conditions'][0]);sb=build_bank(sc,small)
 inf=sb['info'][[0]];W=sb['goal'][[0],0]
 greedy,_=choose(inf,W,list(range(6)),2)
 risks=[];subsets=list(itertools.combinations(range(6),2))
 for subset in subsets:
  H=np.eye(sc['model'].P)+inf[0,list(subset)].sum(axis=0)
  risks.append(float(np.trace(np.linalg.solve(H,W[0]))))
 best=min(risks);greedy_risk=risks[subsets.index(tuple(sorted(greedy)))]
 report['exact_subset_audit']=dict(subsets=15,exact_min_risk=best,greedy_risk=greedy_risk,
       relative_regret=(greedy_risk-best)/max(best,1e-30),nonzero_target=bool(np.linalg.norm(W)>1e-16))
 # Rank-two factorisation, signed raw gains, finite-difference derivative.
 r2cfg=dict(cfg,family='rank2_tanh',neurons=100)
 cond=dict(name='published_gain',prior_sd=.9,mode='gain');rc=public_case(1897,r2cfg,cond);rm=rc['model']
 rt=generate_truth(rc,r2cfg,cond,0);rr,dd=rm.simulate(rt,rc['train'],True)
 direct=Model(rm.J,np.zeros((100,0)),np.zeros((0,100)),rm.x0,rm.active,rm.kind,rm.dt,rm.tau)
 rd,_=direct.simulate(rt,rc['train'])
 report['rank2_dense_factor_max_error']=float(np.max(np.abs(rd-rr)))
 assert report['rank2_dense_factor_max_error']<1e-10
 v=rng.normal(size=100);v/=np.linalg.norm(v)
 rp,_=rm.simulate(rt+h*v,rc['train']);rn,_=rm.simulate(rt-h*v,rc['train'])
 fd=(rp-rn)/(2*h);an=np.einsum('ktnp,p->ktn',dd,v)
 report['rank2_derivative_relative_error']=float(np.linalg.norm(fd-an)/np.linalg.norm(fd))
 assert report['rank2_derivative_relative_error']<1e-5
 report['elapsed_seconds']=time.perf_counter()-start
 return report


if __name__=='__main__':
 cfg=json.loads((Path(__file__).parent/'smoke.json').read_text())
 r=run_checks(cfg);(Path(__file__).parent/'checks.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
