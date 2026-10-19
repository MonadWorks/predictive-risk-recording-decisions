"""Finite-amplitude input/propagation/readout identity and parameter controls.

The secant identity is algebraic. Hybrid paths are functional decompositions,
not physical interventions. Separate gain perturbations test a proposed static
parameter-combination approximation without assuming it is sufficient.
"""
from common4 import *
from numba import njit
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse,math

@njit(cache=True)
def coeff(theta,L,R,x0,U,stim,readouts,dt,tau,substeps):
    n=len(theta);rank=L.shape[1];h=dt/substeps;g=1+theta
    length=len(U)*substeps
    aa=np.zeros((length,4,rank,rank));bb=np.zeros((length,4,rank));cc=np.zeros((length,4,len(readouts),rank))
    z=np.zeros((2,rank));v=np.row_stack((x0,x0));q=np.zeros(len(readouts));ix=0
    eh=np.exp(-h/(2*tau));ef=np.exp(-h/tau)
    for t in range(len(U)):
        us=np.zeros((2,n));us[1]=U[t]
        for sub in range(substeps):
            vh=us+(v-us)*eh;vf=us+(v-us)*ef
            ks=np.zeros((4,2,rank));rates=np.zeros((4,2,n))
            for k in range(4):
                zz=z.copy();vv=v
                if k==1:zz=z+h/2*ks[0];vv=vh
                elif k==2:zz=z+h/2*ks[1];vv=vh
                elif k==3:zz=z+h*ks[2];vv=vf
                xx=vv+zz@L.T;tt=np.tanh(xx);rates[k]=tt*g
                ks[k]=(-zz+rates[k]@R.T)/tau
                sec=np.zeros(n)
                for i in range(n):
                    dx=xx[1,i]-xx[0,i]
                    sec[i]=g[i]*(tt[1,i]-tt[0,i])/dx if abs(dx)>1e-12 else g[i]*(1-np.tanh((xx[1,i]+xx[0,i])/2)**2)
                aa[ix,k]=(R*sec)@L
                bb[ix,k]=R[:,stim]*sec[stim]*(vv[1,stim]-vv[0,stim])
                for j in range(len(readouts)):cc[ix,k,j]=sec[readouts[j]]*L[readouts[j]]
            z+=h/6*(ks[0]+2*ks[1]+2*ks[2]+ks[3]);v=vf
            for k,w in [(0,1.),(1,2.),(2,2.),(3,1.)]:
                q+=h/6*w*(rates[k,1,readouts]-rates[k,0,readouts])
            ix+=1
    return aa,bb,cc,q

@njit(cache=True)
def transfer(a,b,c,dt,tau,substeps):
    h=dt/substeps;z=np.zeros(a.shape[-1]);q=np.zeros(c.shape[-2])
    for t in range(len(a)):
        k1=(-z+a[t,0]@z+b[t,0])/tau;r1=c[t,0]@z
        z2=z+h*k1/2;k2=(-z2+a[t,1]@z2+b[t,1])/tau;r2=c[t,1]@z2
        z3=z+h*k2/2;k3=(-z3+a[t,2]@z3+b[t,2])/tau;r3=c[t,2]@z3
        z4=z+h*k3;k4=(-z4+a[t,3]@z4+b[t,3])/tau;r4=c[t,3]@z4
        z+=h/6*(k1+2*k2+2*k3+k4);q+=h/6*(r1+2*r2+2*r3+r4)
    return q

def coefficients(case,z):
    m=case['model'];theta=case['mu']+case['sd']*np.asarray(z)
    return coeff(theta,m.left,m.right,m.x0,case['intervention'][1],case['stim'],case['readouts'],m.dt,m.tau,m.substeps)

def hybrids(case,ref,alt):
    m=case['model'];qs=[]
    for mask in range(8):
        a=(alt if mask&2 else ref)[0];b=(alt if mask&1 else ref)[1];c=(alt if mask&4 else ref)[2]
        qs.append(transfer(a,b,c,m.dt,m.tau,m.substeps))
    qs=np.asarray(qs);phi=np.zeros((3,3))
    for k in range(3):
        for mask in range(8):
            if mask&(1<<k):continue
            size=mask.bit_count();weight=math.factorial(size)*math.factorial(2-size)/6
            phi[k]+=weight*(qs[mask|(1<<k)]-qs[mask])
    assert np.allclose(phi.sum(0),qs[-1]-qs[0],rtol=1e-10,atol=1e-12)
    return qs,phi

def combination_controls(case,z,nid):
    m=case['model'];ends=[case['stim'],*case['readouts']];eye=np.eye(m.P)
    E=eye[ends];A=np.einsum('ai,ib->abi',m.right,m.left).reshape(-1,m.P)*case['sd'][None,:]
    B=np.row_stack((E,A));random=seeded(95201,nid).normal(size=B.shape)
    _,G=m.responses(case['mu']+case['sd']*z,case['intervention'],True);G=G[case['readouts']]*case['sd']
    bases={'endpoint':E,'endpoint_recurrence':B,'random8':random}
    directions=seeded(95203,nid).normal(size=(8,m.P));out={};q0,_=m.responses(case['mu']+case['sd']*z,case['intervention'])
    for label,rows in bases.items():
        _,s,v=np.linalg.svd(rows,full_matrices=False);v=v[s>s[0]*1e-10]
        proj=v.T@v;null=directions-directions@proj
        null/=np.linalg.norm(null,axis=1)[:,None]
        entry=dict(constraint_rank=len(v),gradient_fraction=float(np.sum((G@proj)**2)/np.sum(G**2)),perturbations={})
        for rms in [.1,.3]:
            vals=[];invariant=[]
            for direction in null:
                for sign in [-1,1]:
                    dz=sign*rms*np.sqrt(m.P)*direction;theta=case['mu']+case['sd']*(z+dz)
                    q,_=m.responses(theta,case['intervention']);vals.append(float(np.mean((q[case['readouts']]-q0[case['readouts']])**2)))
                    invariant.append(float(np.linalg.norm(rows@dz)))
            entry['perturbations'][str(rms)]=dict(mean_squared_change=float(np.mean(vals)),changes=vals,max_constraint_error=max(invariant))
        out[label]=entry
    return out

def worker(nid,stage):
    path=HERE/'runs'/stage/f'{nid}.json'
    if path.exists():return dict(network_id=nid,cached=True)
    tick=time.perf_counter();cfg,c=case_for(nid)
    raw=json.loads((ROOT/'round3/runs/profile_validation'/f'{nid}.json').read_text());records=[];max_error=0.
    for r in raw['records']:
        if r['policy'] not in ['neither','both']:continue
        z=np.asarray(r['best']['z']);ref=coefficients(c,z)
        max_error=max(max_error,float(np.max(abs(ref[3]-np.asarray(r['best']['q_hat'])))))
        entries=[]
        for s in r['profile']['searches']:
            alt=coefficients(c,s['chosen']['z']);qs,phi=hybrids(c,ref,alt)
            max_error=max(max_error,float(np.max(abs(qs[0]-ref[3]))),float(np.max(abs(qs[-1]-alt[3]))))
            entries.append(dict(target=s['target'],sign=s['sign'],q_reference=ref[3].tolist(),q_alternative=alt[3].tolist(),
                                hybrid_q=qs.tolist(),component_changes=phi.tolist()))
        records.append(dict(policy=r['policy'],decomposition=entries,combinations=combination_controls(c,z,nid)))
    assert max_error<1e-9,max_error
    out=dict(network_id=nid,complete=True,max_identity_error=max_error,seconds=time.perf_counter()-tick,records=records)
    dump(path,out);return dict(network_id=nid,seconds=out['seconds'],identity_error=max_error)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=40000);ap.add_argument('--count',type=int,default=40)
    ap.add_argument('--workers',type=int,default=2);ap.add_argument('--stage',default='mechanism');a=ap.parse_args()
    with ProcessPoolExecutor(a.workers) as ex:
        for f in as_completed([ex.submit(worker,n,a.stage) for n in range(a.start,a.start+a.count)]):print(json.dumps(f.result()),flush=True)
