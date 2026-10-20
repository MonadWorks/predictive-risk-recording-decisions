"""Oracle diagnostic only: replace fitted endpoint gains, without refitting.

This identifies where prediction error resides within each fitted model. It
does not define a deployable estimator or isolate mediation by gain error.
"""
import os,sys,json,time
from pathlib import Path
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
HERE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(HERE.parent/'code'))
import numpy as np
from threadpoolctl import threadpool_limits
from models import seeded
from rank2_refined import refined_case

def main():
    while len(list((HERE/'runs/endpoint').glob('*.done.json')))<40:time.sleep(5)
    cfg=json.loads((HERE.parent/'protocols/confirmation.json').read_text());records=[]
    for nid in range(20000,20040):
        case=refined_case(nid,cfg,cfg['conditions'][0],2);m=case['model']
        for line in (HERE/f'runs/endpoint/{nid}.jsonl').read_text().splitlines():
            r=json.loads(line)
            if r['policy']!='neither':continue
            truth=.9*seeded(211,nid,r['truth_id']).normal(size=100)
            row={k:r[k] for k in ['network_id','truth_id','noise_id','replicate','response_mse']}
            for label,ids in [('stim',[case['stim']]),('readouts',list(case['readouts'])),('both',[case['stim'],*case['readouts']])]:
                corrected=np.array(r['theta']);corrected[ids]=truth[ids]
                q,_=m.responses(corrected,case['intervention'])
                row[f'{label}_corrected_mse']=float(np.mean((q[case['readouts']]-r['q_true'])**2))
            records.append(row)
    assert len(records)==480
    (HERE/'analysis/oracle_endpoint_correction.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps({k:float(np.mean([r[k] for r in records])) for k in ['response_mse','stim_corrected_mse','readouts_corrected_mse','both_corrected_mse']},indent=2))

if __name__=='__main__':
    with threadpool_limits(limits=1):main()
