"""Independent dimensionless rate-model implementations; no upstream code.

Softplus family motivated by Beiran & Litwin-Kumar (2025). Rank-two tanh
family follows their Fig.3 equations/distribution with explicit protocol
adaptations (inputs, known initial state, measurement noise, fitting).
"""
from dataclasses import dataclass
import math
import numpy as np
try:
    from numba import njit
except ImportError:
    def njit(*args, **kwargs):
        return lambda f: f


@njit(cache=True)
def kernel(theta, J, left, right, U, dt, tau, x0, active, kind, nodes, sensitivity):
    K,T,N=U.shape; P=len(theta); O=len(nodes)
    gain=np.ones(N); bias=np.zeros(N)
    for p in range(P):
        ix=active[p]
        if ix<N:
            gain[ix]=math.exp(theta[p]) if kind==0 else 1.+theta[p]
        else:
            bias[ix-N]=theta[p]
    R=np.zeros((K,T,O))
    D=np.zeros((K,T,O,P)) if sensitivity else np.zeros((0,0,0,0))
    for k in range(K):
        x=x0.copy();S=np.zeros((N,P));r=np.zeros(N);slope=np.zeros(N)
        for t in range(T):
            for i in range(N):
                z=x[i]+bias[i]
                if kind==0:
                    sp=z+math.log1p(math.exp(-z)) if z>0. else math.log1p(math.exp(z))
                    sig=1./(1.+math.exp(-z)) if z>=0. else math.exp(z)/(1.+math.exp(z))
                    r[i]=gain[i]*sp;slope[i]=gain[i]*sig
                else:
                    h=math.tanh(z);r[i]=gain[i]*h;slope[i]=gain[i]*(1.-h*h)
            dr=np.zeros((N,P))
            if sensitivity:
                for i in range(N):
                    for p in range(P):
                        v=slope[i]*S[i,p]
                        if active[p]==i:
                            v+=r[i] if kind==0 else math.tanh(x[i]+bias[i])
                        elif active[p]==N+i:
                            v+=slope[i]
                        dr[i,p]=v
            for o in range(O):
                i=nodes[o];R[k,t,o]=r[i]
                if sensitivity:
                    for p in range(P):D[k,t,o,p]=dr[i,p]
            drive=np.zeros(N);dS=np.zeros((N,P))
            if left.shape[1]>0:
                rank=left.shape[1];rr=np.zeros(rank);ss=np.zeros((rank,P))
                for a in range(rank):
                    for j in range(N):
                        rr[a]+=right[a,j]*r[j]
                        if sensitivity:
                            for p in range(P):ss[a,p]+=right[a,j]*dr[j,p]
                for i in range(N):
                    for a in range(rank):
                        drive[i]+=left[i,a]*rr[a]
                        if sensitivity:
                            for p in range(P):dS[i,p]+=left[i,a]*ss[a,p]
            else:
                for i in range(N):
                    for j in range(N):
                        drive[i]+=J[i,j]*r[j]
                        if sensitivity:
                            for p in range(P):dS[i,p]+=J[i,j]*dr[j,p]
            for i in range(N):
                x[i]+=dt/tau*(-x[i]+drive[i]+U[k,t,i])
                if sensitivity:
                    for p in range(P):S[i,p]+=dt/tau*(-S[i,p]+dS[i,p])
    return R,D


@dataclass
class Model:
    J:np.ndarray
    left:np.ndarray
    right:np.ndarray
    x0:np.ndarray
    active:np.ndarray
    kind:int=0
    dt:float=.05
    tau:float=1.

    @property
    def N(self):return len(self.J)
    @property
    def P(self):return len(self.active)

    def simulate(self,theta,U,sensitivity=False,nodes=None):
        ids=np.arange(self.N,dtype=np.int64) if nodes is None else np.asarray(nodes,dtype=np.int64)
        return kernel(np.asarray(theta),self.J,self.left,self.right,U,self.dt,self.tau,self.x0,self.active,self.kind,ids,sensitivity)

    def responses(self,theta,U,sensitivity=False):
        r,d=self.simulate(theta,U,sensitivity)
        Q=self.dt*np.sum(r[1]-r[0],axis=0)
        G=self.dt*np.sum(d[1]-d[0],axis=0) if sensitivity else None
        return Q,G


def seeded(stream,network_id,index=0):
    return np.random.default_rng(np.random.SeedSequence([int(stream),int(network_id),int(index)]))


def public_case(network_id,cfg,condition):
    """Public model/prior/task only; no truth or measurement fields."""
    rng=seeded(cfg['model_seed'],network_id);N=cfg['neurons'];T=cfg['steps']
    if cfg['family']=='softplus':
        signs=np.ones(N);signs[-max(1,N//5):]=-1
        J=np.abs(rng.normal(size=(N,N)))*(rng.random((N,N))<.3)
        np.fill_diagonal(J,0.);J*=signs[None,:]
        J*=cfg['connectivity_norm']/max(np.linalg.norm(J,2),1e-15)
        left=np.zeros((N,0));right=np.zeros((0,N));x0=np.zeros(N);kind=0;tau=1.
        mode=condition.get('mode','both')
        active=np.arange(2*N) if mode=='both' else np.arange(N) if mode=='gain' else np.arange(N,2*N)
    else:
        # Fig.3 covariance recipe: reproduce the reported PSD inflation,
        # including one final inflation on the first nonnegative iteration.
        cov=np.eye(4)
        cov[0,2]=cov[2,0]=1.5;cov[0,3]=cov[3,0]=3.
        cov[1,2]=cov[2,1]=-3.;cov[1,3]=cov[3,1]=1.5
        for _ in range(100):
            eig=np.linalg.eigvalsh(cov)
            cov[2,2]*=1.1;cov[3,3]*=1.1
            if eig.min()>=0.:break
        v=rng.multivariate_normal(np.zeros(4),cov,size=N)
        left=v[:,:2]/N;right=v[:,2:].T.copy()
        J=np.einsum('ia,aj->ij',left,right)
        x0=.1*rng.normal(size=N);kind=1;tau=.5;active=np.arange(N)
    model=Model(J,left,right,x0,active.astype(np.int64),kind,cfg['dt'],tau)
    tt=np.arange(T)*model.dt
    train=np.zeros((2,T,N));test=np.zeros_like(train)
    channels=rng.choice(N,3,replace=False)
    for k in range(2):
        for j,node in enumerate(channels):
            train[k,:,node]=.4*np.sin((.6+.3*j)*tt+k*.7)
            test[k,:,node]=.4*np.sin((.9+.2*j)*tt+k*.4+1.3)
    # Choose reachable targets using J alone, before generating physiology.
    reach=np.abs(J)>0
    for _ in range(N):
        updated=reach | ((reach.astype(np.int64)@reach.astype(np.int64))>0)
        if np.array_equal(updated,reach):break
        reach=updated
    eligible=[i for i in range(N) if np.sum(reach[:,i])-int(reach[i,i])>=cfg['targets']]
    if not eligible:raise ValueError('no stimulation site with required reachable targets')
    stim=int(rng.choice(eligible));pool=np.array([i for i in range(N) if i!=stim and reach[i,stim]])
    readouts=rng.choice(pool,cfg['targets'],replace=False).astype(np.int64)
    intervention=np.zeros((2,T,N));intervention[1,(tt>=1.)&(tt<2.),stim]=.6
    sd=np.full(model.P,condition['prior_sd']);mu=np.zeros(model.P)
    return dict(model=model,train=train,test=test,intervention=intervention,stim=stim,
                readouts=readouts,sd=sd,mu=mu,network_id=network_id)


def generate_truth(case,cfg,condition,truth_id):
    m=case['model']
    full=seeded(cfg['truth_seed'],case['network_id'],truth_id).normal(size=2*m.N if m.kind==0 else m.N)
    z=full[m.active]
    theta=case['mu']+case['sd']*z
    shift=condition.get('true_bias_shift',0.)
    theta=theta+shift*(case['model'].active>=case['model'].N)
    return theta


def source_receipt(case):
    m=case['model']
    return dict(neurons=m.N,parameters=m.P,stim=case['stim'],readouts=case['readouts'].tolist(),
                tau=m.tau,dt=m.dt,model_kind='softplus' if m.kind==0 else 'rank2_tanh',
                connectivity_norm=float(np.linalg.norm(m.J,2)),connectivity_rank=int(np.linalg.matrix_rank(m.J)))
