"""Independent extension of the frozen inference and simulation code."""
import os,sys,json,time,copy,hashlib
from pathlib import Path
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[key]='1'
HERE=Path(__file__).resolve().parent.parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'round3/code'))
from common import Problem,case_for,data_for,seeded,dump,bootstrap_change
import numpy as np
from rank2_refined import RefinedModel

CONDITIONS=['matched_rank2','augmented_rank6','random_rank6','connectivity_error','initial_state_error','positive_gain']

class PositiveModel(RefinedModel):
    """Unit-mean lognormal gains with the same Gaussian latent prior."""
    def raw(self,theta):return np.exp(np.asarray(theta)-.9**2/2)-1
    def simulate(self,theta,U,sensitivity=False,nodes=None):
        raw=self.raw(theta);r,d=super().simulate(raw,U,sensitivity,nodes)
        if sensitivity:d=d*(1+raw)[None,None,None,:]
        return r,d
    def responses(self,theta,U,sensitivity=False):
        raw=self.raw(theta);q,g=super().responses(raw,U,sensitivity)
        if sensitivity:g=g*(1+raw)[None,:]
        return q,g

def with_factors(model,left,right,positive=False):
    cls=PositiveModel if positive else RefinedModel
    m=cls(left@right,left.copy(),right.copy(),model.x0.copy(),model.active.copy(),1,model.dt,model.tau)
    m.substeps=model.substeps
    return m

def residual_factors(base,nid,rank,strength,normalize=False):
    rng=seeded(95101,nid,rank);n=base.N
    l=rng.normal(size=(n,rank))/np.sqrt(n);r=rng.normal(size=(rank,n))/np.sqrt(n)
    l*=strength*np.linalg.norm(base.J)/np.linalg.norm(l@r)
    left=np.column_stack([base.left,l]);right=np.row_stack([base.right,r])
    if normalize:left*=np.linalg.norm(base.J)/np.linalg.norm(left@right)
    return left,right

def make_case(nid,condition):
    cfg,base=case_for(nid);cfg['max_nfev']=400
    student=copy.deepcopy(base);teacher=copy.deepcopy(base);m=base['model']
    if condition=='augmented_rank6':
        l,r=residual_factors(m,nid,4,.5,True)
        student['model']=with_factors(m,l,r);teacher=copy.deepcopy(student)
    elif condition=='random_rank6':
        rng=seeded(95103,nid);l=rng.normal(size=(m.N,6))/np.sqrt(m.N);r=rng.normal(size=(6,m.N))/np.sqrt(m.N)
        l*=np.linalg.norm(m.J)/np.linalg.norm(l@r)
        student['model']=with_factors(m,l,r);teacher=copy.deepcopy(student)
    elif condition=='connectivity_error':
        l,r=residual_factors(m,nid,4,.1)
        teacher['model']=with_factors(m,l,r)
    elif condition=='initial_state_error':
        teacher['model'].x0+=.03*seeded(95107,nid).normal(size=m.N)
    elif condition=='positive_gain':
        student['model']=with_factors(m,m.left,m.right,True);teacher=copy.deepcopy(student)
    elif condition!='matched_rank2':raise ValueError(condition)
    theta,clean,eps,q=data_for(teacher,cfg)
    return cfg,student,teacher,theta,clean,eps,q

def starts(nid,p=100):
    rng=seeded(95111,nid)
    return [np.zeros(p),*.25*rng.normal(size=(2,p)),*rng.normal(size=(6,p))]

def fit_record(case,cfg,nodes,clean,eps,sigma,trueq,start_list):
    nodes=sorted(map(int,nodes));sig=np.asarray(sigma)[nodes]
    p=Problem(case,cfg,nodes,clean[:,:,nodes]+eps[:,:,nodes]*sig,sig)
    best,fits=p.multistart(start_list)
    return p,dict(nodes=nodes,sigma=sig.tolist(),best=best,fits=fits,q_true=trueq.tolist(),
                  mse=float(np.mean((np.asarray(best['q_hat'])-trueq)**2)))

def paired_allocations(case):
    ends=[int(case['stim']),*map(int,case['readouts'])]
    perm=seeded(1601,case['network_id']).permutation([i for i in range(case['model'].N) if i not in ends]).tolist()
    return dict(neither=sorted(perm[:5]),both=sorted(ends+[perm[0]]))

def model_receipt(student,teacher):
    a=student['model'];b=teacher['model']
    return dict(student_rank=int(np.linalg.matrix_rank(a.J)),teacher_rank=int(np.linalg.matrix_rank(b.J)),
                connectivity_relative_error=float(np.linalg.norm(a.J-b.J)/np.linalg.norm(a.J)),
                initial_state_error_norm=float(np.linalg.norm(a.x0-b.x0)),
                student_connectivity_norm=float(np.linalg.norm(a.J)),positive_gains=isinstance(a,PositiveModel))
