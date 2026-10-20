from common import *
from profiles import extremes
from methods import select_joint

class Quadratic:
    def __init__(self):
        self.H=np.array([[2.,.3],[.3,1.]])
        self.J=np.linalg.cholesky(self.H).T
        self.G=np.array([[1.,.2],[.3,-.7],[1.,1.]])
    def evaluate(self,z):
        return dict(jac=self.J,cost=10.+.5*np.einsum('i,ij,j',z,self.H,z),grad=np.einsum('ij,j->i',self.H,z))
    def response(self,z):return dict(q=np.einsum('ij,j->i',self.G,z),g=self.G)

def main():
    toy=Quadratic();best=dict(z=[0.,0.],objective=10.)
    prof=extremes(toy,best)
    analytic=2*np.sqrt(4*np.einsum('ki,ij,kj->k',toy.G,np.linalg.inv(toy.H),toy.G))
    assert np.allclose(prof['width'],analytic,rtol=2e-5)
    cfg,case=case_for(19980);theta,y,eps,q=data_for(case,cfg);nodes,ends=allocated_nodes(case,'both')
    sigma=np.array([.2 if i in ends else .05 for i in nodes])
    p=Problem(case,cfg,nodes,y[:,:,nodes]+eps[:,:,nodes]*sigma,sigma)
    z=seeded(78,19980).normal(size=100)*.1;direction=seeded(79,19980).normal(size=100);direction/=np.linalg.norm(direction)
    e=p.evaluate(z);grad=e['grad'].copy();r=p.response(z);g=r['g'].copy();h=1e-5
    costfd=(p.evaluate(z+h*direction)['cost']-p.evaluate(z-h*direction)['cost'])/(2*h)
    qfd=(p.response(z+h*direction)['q']-p.response(z-h*direction)['q'])/(2*h)
    assert np.allclose(costfd,np.dot(grad,direction),rtol=1e-5,atol=1e-5)
    assert np.allclose(qfd,np.einsum('ki,i->k',g,direction),rtol=1e-5,atol=1e-8)
    rng=np.random.default_rng(123);L=12;Y=rng.normal(size=(L,4));Q=rng.normal(size=(L,3));V=rng.normal(size=(L,4));Qv=rng.normal(size=(L,3))
    Y-=Y.mean(0);Q-=Q.mean(0);X=Y/np.sqrt(L-1);Z=V/np.sqrt(L-1)
    K=np.einsum('lt,mt->lm',X,X);cross=np.einsum('lt,mt->lm',Z,X)
    bank=dict(K=K[None],cross=cross[None],q=Q,qv=Qv,L=L)
    _,cv=select_joint(bank,[0],1,True);_,cov=select_joint(bank,[0],1,False)
    H=np.einsum('li,lj->ij',X,X)+np.eye(4)
    W=np.linalg.solve(H,np.einsum('li,lj->ij',Y,Q)/(L-1))
    pred=np.einsum('li,ij->lj',V,W)
    directcv=float(np.mean((pred-Qv)**2)+np.sum(W*W)/3)
    directcov=float((np.sum(Q*Q)/(L-1)-np.sum(np.einsum('li,lj->ij',Y,Q)/(L-1)*W))/3)
    assert np.allclose(cv[0],directcv,rtol=1e-10)
    assert np.allclose(cov[0],directcov,rtol=1e-10)
    out=dict(profile_quadratic_relative_error=float(np.max(abs(np.array(prof['width'])/analytic-1))),
             objective_gradient_relative_error=float(abs(costfd-np.dot(grad,direction))/max(abs(costfd),1e-15)),
             response_gradient_max_error=float(np.max(abs(qfd-np.einsum('ki,i->k',g,direction)))),
             cv_dual_vs_direct_error=float(abs(cv[0]-directcv)),cov_dual_vs_direct_error=float(abs(cov[0]-directcov)),passed=True)
    dump(HERE/'analysis/checks.json',out);print(json.dumps(out))
if __name__=='__main__':main()
