"""Value-only SLSQP line searches; gradients still use the verified sensitivities."""
from common import *

class FastProblem(Problem):
    def cost_value(self,z):
        if self.cache.get('key')==z.tobytes():return self.cache['cost']
        if getattr(self,'vcache',{}).get('key')!=z.tobytes():
            theta=self.case['mu']+self.case['sd']*z
            r,_=self.m.simulate(theta,self.case['train'],False,self.nodes)
            e=((r[:,::self.cfg['sample_stride']]-self.y)/self.sigma).ravel()
            self.vcache=dict(key=z.tobytes(),cost=.5*float(np.dot(e,e)+np.dot(z,z)))
        return self.vcache['cost']
    def q_value(self,z):
        if self.qcache.get('key')==z.tobytes():return self.qcache['q']
        if getattr(self,'qvcache',{}).get('key')!=z.tobytes():
            theta=self.case['mu']+self.case['sd']*z
            q,_=self.m.responses(theta,self.case['intervention'],False)
            self.qvcache=dict(key=z.tobytes(),q=q[self.case['readouts']])
        return self.qvcache['q']
