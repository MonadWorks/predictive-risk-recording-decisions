"""Analytic input--propagation--readout factorization of the first variation.

The first variation is an established sensitivity equation. This diagnostic
checks how accurately it describes the particular finite stimulus in this paper.
"""
from common import *
from numba import njit
import argparse

@njit(cache=True)
def stage(z,dz,v,dv,L,R,g,tau):
    x=v+np.dot(L,z);slope=g*(1-np.tanh(x)**2)
    r=g*np.tanh(x);dr=slope*(dv+np.dot(L,dz))
    return (-z+np.dot(R,r))/tau,(-dz+np.dot(R,dr))/tau,dr

@njit(cache=True)
def linear_response(theta,L,R,x0,stim_input,dt,tau,substeps=2):
    z=np.zeros(L.shape[1]);dz=np.zeros_like(z);v=x0.copy();dv=np.zeros(len(x0));q=np.zeros(len(x0))
    h=dt/substeps;eh=np.exp(-h/(2*tau));ef=np.exp(-h/tau);g=1+theta
    for t in range(len(stim_input)):
        u=stim_input[t]
        for _ in range(substeps):
            vh=v*eh;vf=v*ef;dvh=u+(dv-u)*eh;dvf=u+(dv-u)*ef
            a,ad,ar=stage(z,dz,v,dv,L,R,g,tau)
            b,bd,br=stage(z+h*a/2,dz+h*ad/2,vh,dvh,L,R,g,tau)
            c,cd,cr=stage(z+h*b/2,dz+h*bd/2,vh,dvh,L,R,g,tau)
            d,dd,dr=stage(z+h*c,dz+h*cd,vf,dvf,L,R,g,tau)
            z+=h/6*(a+2*b+2*c+d);dz+=h/6*(ad+2*bd+2*cd+dd)
            q+=h/6*(ar+2*br+2*cr+dr);v=vf;dv=dvf
    return q

def response(case,theta):
    m=case['model']
    return linear_response(np.asarray(theta),m.left,m.right,m.x0,case['intervention'][1],m.dt,m.tau)[case['readouts']]

def check():
    cfg,c=case_for(19984);theta=generate_truth(c,cfg,cfg['conditions'][0],0)
    lin=response(c,theta);u=c['intervention'].copy();eps=1e-4
    qp,_=c['model'].responses(theta,u*eps);qn,_=c['model'].responses(theta,-u*eps)
    fd=(qp-qn)[c['readouts']]/(2*eps)
    error=float(np.linalg.norm(fd-lin)/max(np.linalg.norm(lin),1e-15))
    assert error<1e-5
    dump(HERE/'analysis/response_structure_check.json',dict(relative_error=error,passed=True));print(error)

def analyze():
    records=[]
    for nid in range(40000,40040):
        cfg,c=case_for(nid);theta,y,eps,trueq=data_for(c,cfg)
        raw=json.loads((HERE/'runs/profile_validation'/f'{nid}.json').read_text())
        for label,th,q in [('truth',theta,trueq)]+[(r['policy'],c['mu']+c['sd']*np.array(r['best']['z']),np.array(r['best']['q_hat'])) for r in raw['records']]:
            qlin=response(c,th)
            records.append(dict(network_id=nid,policy=label,q_linear=qlin.tolist(),q_nonlinear=np.asarray(q).tolist(),
                                approximation_mse=float(np.mean((qlin-q)**2)),signal_square=float(np.mean(np.asarray(q)**2))))
    out={}
    for label in ['truth','neither','both','both_noise4','both_noise16']:
        rr=[r for r in records if r['policy']==label]
        out[label]=dict(aggregate_relative_rmse=float(np.sqrt(np.mean([r['approximation_mse'] for r in rr])/np.mean([r['signal_square'] for r in rr]))),
            median_relative_rmse=float(np.median([np.sqrt(r['approximation_mse']/max(r['signal_square'],1e-16)) for r in rr])))
    dump(HERE/'analysis/response_structure.json',dict(summary=out,records=records));print(json.dumps(out,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['check','analyze']);a=ap.parse_args()
    check() if a.phase=='check' else analyze()
