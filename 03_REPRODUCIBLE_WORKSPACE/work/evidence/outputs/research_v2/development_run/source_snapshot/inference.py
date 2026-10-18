"""Common Gaussian MAP estimator and nonlinear response evaluation."""
import time
import numpy as np
from scipy.optimize import least_squares


def fit_selected(case,cfg,nodes,observed):
    start=time.perf_counter();m=case['model'];sd=case['sd'];mu=case['mu'];cache={}
    nodes=np.asarray(sorted(nodes),dtype=np.int64)
    def evaluate(theta):
        key=theta.tobytes()
        if cache.get('key')!=key:
            r,d=m.simulate(theta,case['train'],True,nodes)
            pred=r[:,::cfg['sample_stride']]
            jac=d[:,::cfg['sample_stride']]
            residual=np.r_[((pred-observed)/cfg['noise_sd']).ravel(),(theta-mu)/sd]
            fulljac=np.vstack([jac.reshape(-1,m.P)/cfg['noise_sd'],np.diag(1/sd)])
            if not np.isfinite(residual).all() or not np.isfinite(fulljac).all():raise FloatingPointError('nonfinite MAP evaluation')
            cache.update(key=key,residual=residual,jac=fulljac)
        return cache
    fallback=False;error=''
    try:
        fit=least_squares(lambda x:evaluate(x)['residual'],mu,
             jac=lambda x:evaluate(x)['jac'],max_nfev=cfg['max_nfev'],
             xtol=1e-7,ftol=1e-7,gtol=1e-7)
        theta=fit.x;success=bool(fit.success);nfev=fit.nfev;cost=fit.cost
        H=np.einsum('ki,kj->ij',fit.jac,fit.jac)
        Q,G=m.responses(theta,case['intervention'],True)
        g=G[case['readouts']]
        variance=np.einsum('ki,ik->k',g,np.linalg.solve(H,g.T))
        if not np.isfinite(Q).all():raise FloatingPointError('nonfinite response')
    except (ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError) as exc:
        # Predeclared deployable fallback; never silently delete failures.
        fallback=True;error=type(exc).__name__+': '+str(exc)[:150]
        theta=mu.copy();success=False;nfev=-1;cost=float('nan')
        Q,G=m.responses(theta,case['intervention'],True)
        g=G[case['readouts']]*sd[None,:]
        variance=np.sum(g*g,axis=1)
    predicted,_=m.simulate(theta,case['test'])
    return dict(theta=theta,Q=Q[case['readouts']],variance=np.maximum(variance,0.),
                test_activity=predicted,success=success,nfev=int(nfev),cost=float(cost),
                fallback=fallback,error=error,seconds=time.perf_counter()-start)
