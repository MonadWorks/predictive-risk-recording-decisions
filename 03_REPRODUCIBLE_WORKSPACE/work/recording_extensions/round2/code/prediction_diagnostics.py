"""Targeted posthoc checks: task-specific prediction and exact error identity."""
import os,sys,json,argparse
from pathlib import Path
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
HERE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(HERE.parent/'code'))
import numpy as np
from threadpoolctl import threadpool_limits
from models import generate_truth
from rank2_refined import refined_case

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--validation',action='store_true');args=ap.parse_args()
    folder=HERE/('validation/runs/endpoint' if args.validation else 'runs/endpoint')
    assert len(list(folder.glob('*.done.json')))==40
    cfg=json.loads((HERE.parent/'protocols/confirmation.json').read_text());records=[]
    first=30000 if args.validation else 20000
    for nid in range(first,first+40):
        case=refined_case(nid,cfg,cfg['conditions'][0],2);m=case['model'];truths={}
        for tid in range(2):
            t=generate_truth(case,cfg,cfg['conditions'][0],tid);r,_=m.simulate(t,case['test']);truths[tid]=(t,r)
        for line in (folder/f'{nid}.jsonl').read_text().splitlines():
            r=json.loads(line);theta=np.array(r['theta']);truth,teacher=truths[r['truth_id']]
            pred,_=m.simulate(theta,case['test'])
            qtrue=np.array(r['q_true']);err=np.array(r['q_hat'])-qtrue
            gains=1+truth[case['readouts']]
            assert np.min(np.abs(gains))>1e-9
            amplitude=(theta[case['readouts']]-truth[case['readouts']])*qtrue/gains
            dynamics=err-amplitude
            row={k:r[k] for k in ['network_id','truth_id','noise_id','replicate','policy','response_mse']}
            row.update(passive_mse=float(np.mean((pred-teacher)**2)),
                       stim_gain_mse=float((theta[case['stim']]-truth[case['stim']])**2),
                       readout_gain_mse=float(np.mean((theta[case['readouts']]-truth[case['readouts']])**2)),
                       endpoint_amplitude_term_mse=float(np.mean(amplitude**2)),
                       dynamic_term_mse=float(np.mean(dynamics**2)),
                       cross_term=float(2*np.mean(amplitude*dynamics)))
            assert np.isclose(row['response_mse'],row['endpoint_amplitude_term_mse']+row['dynamic_term_mse']+row['cross_term'],atol=1e-12,rtol=1e-8)
            records.append(row)
    suffix='_validation' if args.validation else ''
    (HERE/f'analysis/prediction_diagnostics{suffix}.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps({p:{k:float(np.mean([r[k] for r in records if r['policy']==p])) for k in ['response_mse','passive_mse','endpoint_amplitude_term_mse','dynamic_term_mse','cross_term']} for p in ['neither','stim_only','readouts_only','both']},indent=2))

if __name__=='__main__':
    with threadpool_limits(limits=1):main()
