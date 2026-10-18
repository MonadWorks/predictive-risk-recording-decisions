"""Exact rank-two state reduction with RK4 and analytic known-input filter.

Inputs are zero-order held on the protocol grid. Recording times stay on that
grid; intervention responses integrate rates/sensitivities at RK4 stages.
No gain clipping, fastmath, or approximated zero rows in response gradients.
"""
import argparse,json,time
from pathlib import Path
import numpy as np
from numba import njit
from models import Model,public_case,generate_truth

@njit(cache=True)
def stage(z,S,v,L,R,g,tau,sensitivity):
    N=len(g);rank=L.shape[1];P=S.shape[1]
    r=np.zeros(N);dr=np.zeros((N,P))
    for i in range(N):
        x=v[i]
        for a in range(rank):x+=L[i,a]*z[a]
        t=np.tanh(x);s=g[i]*(1.-t*t);r[i]=g[i]*t
        if sensitivity:
            for p in range(P):
                for a in range(rank):dr[i,p]+=s*L[i,a]*S[a,p]
                if i==p:dr[i,p]+=t
    kz=-z.copy();ks=-S.copy()
    for a in range(rank):
        for i in range(N):
            kz[a]+=R[a,i]*r[i]
            if sensitivity:
                for p in range(P):ks[a,p]+=R[a,i]*dr[i,p]
    return kz/tau,ks/tau,r,dr

@njit(cache=True)
def refined_kernel(theta,L,R,U,dt,tau,x0,nodes,sensitivity,substeps,integral):
    K,T,N=U.shape;O=len(nodes);P=len(theta);rank=L.shape[1]
    result=np.zeros((K,T,O)) if not integral else np.zeros((0,0,0))
    deriv=np.zeros((K,T,O,P)) if sensitivity and not integral else np.zeros((0,0,0,0))
    Q=np.zeros((K,N));G=np.zeros((K,N,P))
    g=1.+theta;h=dt/substeps;ehalf=np.exp(-.5*h/tau);efull=np.exp(-h/tau)
    for k in range(K):
        z=np.zeros(rank);S=np.zeros((rank,P));v=x0.copy()
        for t in range(T):
            if not integral:
                _,_,r,dr=stage(z,S,v,L,R,g,tau,sensitivity)
                for o in range(O):
                    result[k,t,o]=r[nodes[o]]
                    if sensitivity:
                        for p in range(P):deriv[k,t,o,p]=dr[nodes[o],p]
            u=U[k,t]
            for _ in range(substeps):
                vh=u+(v-u)*ehalf;vf=u+(v-u)*efull
                a,as_,ar,ad=stage(z,S,v,L,R,g,tau,sensitivity)
                b,bs,br,bd=stage(z+.5*h*a,S+.5*h*as_,vh,L,R,g,tau,sensitivity)
                c,cs,cr,cd=stage(z+.5*h*b,S+.5*h*bs,vh,L,R,g,tau,sensitivity)
                d,ds,dr,dd=stage(z+h*c,S+h*cs,vf,L,R,g,tau,sensitivity)
                z+=h/6.*(a+2.*b+2.*c+d)
                S+=h/6.*(as_+2.*bs+2.*cs+ds)
                if integral:
                    Q[k]+=h/6.*(ar+2.*br+2.*cr+dr)
                    if sensitivity:G[k]+=h/6.*(ad+2.*bd+2.*cd+dd)
                v=vf
    return result,deriv,Q,G

class RefinedModel(Model):
    substeps=2
    def simulate(self,theta,U,sensitivity=False,nodes=None):
        ids=np.arange(self.N,dtype=np.int64) if nodes is None else np.asarray(nodes,dtype=np.int64)
        r,d,_,_=refined_kernel(np.asarray(theta),self.left,self.right,U,self.dt,self.tau,
                              self.x0,ids,sensitivity,self.substeps,False)
        return r,d
    def responses(self,theta,U,sensitivity=False):
        _,_,q,g=refined_kernel(np.asarray(theta),self.left,self.right,U,self.dt,self.tau,
                              self.x0,np.arange(self.N,dtype=np.int64),sensitivity,self.substeps,True)
        return q[1]-q[0],g[1]-g[0] if sensitivity else None

def refined_case(network_id,cfg,condition,substeps=2):
    case=public_case(network_id,cfg,condition);m=case['model']
    if m.kind!=1 or not np.array_equal(m.active,np.arange(m.N)):
        raise ValueError('refined backend requires full signed raw-gain rank-two model')
    m=RefinedModel(m.J,m.left,m.right,m.x0,m.active,m.kind,m.dt,m.tau)
    m.substeps=substeps;case['model']=m;return case

def dense_reference(theta,J,U,dt,tau,x0,substeps):
    """Independent full-state NumPy RK4, including full-state sensitivities."""
    K,T,N=U.shape;rs=np.zeros((K,T,N));ds=np.zeros((K,T,N,N));qq=np.zeros((K,N));gg=np.zeros((K,N,N))
    eye=np.eye(N);gain=1+theta;h=dt/substeps
    def f(x,S,u):
        tt=np.tanh(x);r=gain*tt;dr=gain[:,None]*(1-tt*tt)[:,None]*S+eye*tt[:,None]
        return (-x+J@r+u)/tau,(-S+J@dr)/tau,r,dr
    for k in range(K):
        x=x0.copy();S=np.zeros((N,N))
        for t in range(T):
            _,_,rs[k,t],ds[k,t]=f(x,S,U[k,t])
            for _ in range(substeps):
                a,aa,ar,ad=f(x,S,U[k,t]);b,bb,br,bd=f(x+h*a/2,S+h*aa/2,U[k,t])
                c,cc,cr,cd=f(x+h*b/2,S+h*bb/2,U[k,t]);d,dd,dr,dg=f(x+h*c,S+h*cc,U[k,t])
                x+=h/6*(a+2*b+2*c+d);S+=h/6*(aa+2*bb+2*cc+dd)
                qq[k]+=h/6*(ar+2*br+2*cr+dr);gg[k]+=h/6*(ad+2*bd+2*cd+dg)
    return rs,ds,qq[1]-qq[0],gg[1]-gg[0]

def checks():
    root=Path(__file__).parent;cfg=json.loads((root/'rank2_n100.json').read_text());cond=cfg['conditions'][0]
    report=dict(scope='independent numerical-only development seeds; ZOH inputs at protocol grid',cases=[])
    start=time.perf_counter()
    def rel(a,b):return float(np.linalg.norm(a-b)/max(np.linalg.norm(b),1e-15))
    for network_id in [1880,1881]:
        outputs=[];times=[]
        for sub in [1,2,4,8]:
            c=refined_case(network_id,cfg,cond,sub);m=c['model'];theta=generate_truth(c,cfg,cond,0)
            tick=time.perf_counter();r,d=m.simulate(theta,c['train'],True);q,g=m.responses(theta,c['intervention'],True)
            times.append(time.perf_counter()-tick);outputs.append((r,d,q,g))
        ref=outputs[-1];entry=dict(network_id=network_id,negative_gains=int(np.sum(1+theta<0)),
            gains_min=float(np.min(1+theta)),readouts=c['readouts'].tolist(),substeps=[])
        for sub,out,seconds in zip([1,2,4,8],outputs,times):
            entry['substeps'].append(dict(substeps=sub,seconds_including_possible_jit=seconds,
                observation_relative_error=rel(out[0],ref[0]),observation_gradient_relative_error=rel(out[1],ref[1]),
                q_relative_error=rel(out[2],ref[2]),G_relative_error=rel(out[3],ref[3]),
                target_q_relative_error=rel(out[2][c['readouts']],ref[2][c['readouts']]),
                target_G_relative_error=rel(out[3][c['readouts']],ref[3][c['readouts']])))
        # Directional finite differences include integrated Q gradients at all N rows.
        rng=np.random.default_rng(123);v=rng.normal(size=m.P);v/=np.linalg.norm(v);eps=1e-5
        qp,_=m.responses(theta+eps*v,c['intervention']);qn,_=m.responses(theta-eps*v,c['intervention'])
        entry['integrated_Q_directional_gradient_relative_error']=rel((qp-qn)/(2*eps),g@v)
        assert entry['integrated_Q_directional_gradient_relative_error']<1e-5
        rn,dn=m.simulate(theta,c['train'],True,[9,2,7])
        entry['selected_observation_max_error']=float(np.max(np.abs(rn-r[:,:,[9,2,7]])))
        entry['selected_gradient_max_error']=float(np.max(np.abs(dn-d[:,:,[9,2,7]])))
        assert entry['selected_observation_max_error']<1e-12
        report['cases'].append(entry)
    small=dict(cfg,neurons=8,targets=3,steps=40)
    sc=refined_case(1880,small,cond,8);sm=sc['model'];st=generate_truth(sc,small,cond,0)
    rr,dd=sm.simulate(st,sc['train'],True);q,g=sm.responses(st,sc['intervention'],True)
    dense=dense_reference(st,sm.J,sc['train'],sm.dt,sm.tau,sm.x0,16)
    intdense=dense_reference(st,sm.J,sc['intervention'],sm.dt,sm.tau,sm.x0,16)
    report['independent_dense_RK4_small']=dict(neurons=8,reduced_substeps=8,dense_substeps=16,
      observation_relative_error=rel(rr,dense[0]),gradient_relative_error=rel(dd,dense[1]),
      q_relative_error=rel(q,intdense[2]),G_relative_error=rel(g,intdense[3]))
    assert max(report['independent_dense_RK4_small'][k] for k in ['observation_relative_error','gradient_relative_error','q_relative_error','G_relative_error'])<1e-5
    report['elapsed_seconds']=time.perf_counter()-start
    (root/'rank2_refined_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':checks()
