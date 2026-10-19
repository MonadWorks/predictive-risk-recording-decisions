"""Numerical checks on development seeds, separate from evaluation networks."""
from common4 import *
from rank2_refined import dense_reference

def main():
    out={}
    for condition in CONDITIONS:
        cfg,c,t,theta,y,eps,q=make_case(49980,condition);m=t['model']
        d=seeded(95121,49980).normal(size=m.P);d/=np.linalg.norm(d);h=1e-5
        r,g=m.simulate(theta,c['train'],True,[3,19,7])
        rp,_=m.simulate(theta+h*d,c['train'],False,[3,19,7]);rm,_=m.simulate(theta-h*d,c['train'],False,[3,19,7])
        qq,G=m.responses(theta,c['intervention'],True);qp,_=m.responses(theta+h*d,c['intervention']);qm,_=m.responses(theta-h*d,c['intervention'])
        ge=np.linalg.norm((rp-rm)/(2*h)-np.einsum('ktnp,p->ktn',g,d))/max(np.linalg.norm((rp-rm)/(2*h)),1e-14)
        qe=np.linalg.norm((qp-qm)/(2*h)-G@d)/max(np.linalg.norm((qp-qm)/(2*h)),1e-14)
        assert ge<1e-5 and qe<1e-5,(condition,ge,qe)
        m.substeps=4;qfine,_=m.responses(theta,c['intervention']);m.substeps=2
        err=np.linalg.norm(qfine-qq)/max(np.linalg.norm(qfine),1e-14)
        assert err<.002,(condition,err)
        out[condition]=dict(gradient_relative_error=float(ge),response_gradient_relative_error=float(qe),
                            refinement_relative_error=float(err),**model_receipt(c,t))
    dump(HERE/'analysis/numerical_checks.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
