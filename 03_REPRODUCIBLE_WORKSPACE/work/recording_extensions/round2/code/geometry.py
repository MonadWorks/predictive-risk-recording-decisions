"""Local, public-model explanation of endpoint allocation, no fit outcomes."""
import os,sys,json
from pathlib import Path
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
HERE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(HERE.parent/'code'))
import numpy as np
from threadpoolctl import threadpool_limits
from rank2_refined import refined_case
from models import seeded

def main():
    cfg=json.loads((HERE.parent/'protocols/confirmation.json').read_text());records=[]
    for nid in range(20000,20040):
        case=refined_case(nid,cfg,cfg['conditions'][0],2);m=case['model']
        q,g=m.responses(case['mu'],case['intervention'],True);g=g[case['readouts']]*case['sd']
        _,d=m.simulate(case['mu'],case['train'],True)
        f=d[:,::cfg['sample_stride']].transpose(2,0,1,3).reshape(100,-1,100)*case['sd']/cfg['noise_sd']
        info=np.einsum('nki,nkj->nij',f,f)
        ends={case['stim'],*map(int,case['readouts'])};other=[i for i in range(100) if i not in ends]
        total=float(np.sum(g*g))
        record=dict(network_id=nid,stim=case['stim'],readouts=case['readouts'].tolist(),
          prior_risk=float(total/3),stim_gradient_fraction=float(np.sum(g[:,case['stim']]**2)/total),
          readout_gradient_fraction=float(np.sum(g[:,case['readouts']]**2)/total),
          other_gradient_fraction=float(np.sum(g[:,other]**2)/total),policies={})
        for label,fixed in [('neither',[]),('stim_only',[case['stim']]),('readouts_only',list(case['readouts'])),('both',[case['stim'],*case['readouts']])]:
            rr=[]
            for rep in range(3):
                perm=seeded(1601+rep,nid).permutation(other).tolist()
                nodes=sorted(map(int,[*fixed,*perm[:5-len(fixed)]]))
                c=np.linalg.inv(np.eye(100)+info[nodes].sum(0))
                risk=float(np.einsum('ki,ij,kj->',g,c,g)/3)
                reductions={}
                for group,known in [('stim',[case['stim']]),('readouts',list(case['readouts'])),('both',sorted(ends))]:
                    gc=g@c[:,known]
                    reduction=float(np.einsum('ki,ik->',gc,np.linalg.solve(c[np.ix_(known,known)],gc.T))/3)
                    reductions[f'fraction_removed_if_{group}_gains_known']=reduction/risk
                rr.append(dict(risk=risk,**reductions,
                    stim_variance_fraction=float(c[case['stim'],case['stim']]),
                    readout_variance_fraction=float(np.diag(c)[case['readouts']].mean())))
            record['policies'][label]={k:float(np.mean([r[k] for r in rr])) for k in rr[0]}
        records.append(record)
    (HERE/'analysis/geometry.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps({k:float(np.mean([r[k] for r in records])) for k in ['stim_gradient_fraction','readout_gradient_fraction','other_gradient_fraction']},indent=2))

if __name__=='__main__':
    with threadpool_limits(limits=1):main()
