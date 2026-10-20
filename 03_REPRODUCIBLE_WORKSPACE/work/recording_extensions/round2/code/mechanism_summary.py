"""Exploratory functional diagnostics kept distinct from policy validation."""
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from analyze import paired
HERE=Path(__file__).resolve().parent.parent
A=HERE/'analysis'

def main():
    result={}
    for suffix,label,first in [('', 'first_cohort',20000),('_validation','validation_cohort',30000)]:
        rows=json.loads((A/f'prediction_diagnostics{suffix}.json').read_text())
        groups=defaultdict(list)
        for r in rows:groups[r['policy'],r['network_id']].append(r)
        metrics=['response_mse','passive_mse','endpoint_amplitude_term_mse','dynamic_term_mse','cross_term']
        values={metric:{p:[float(np.mean([r[metric] for r in groups[p,n]])) for n in range(first,first+40)] for p in ['neither','stim_only','readouts_only','both']} for metric in metrics}
        diag=dict(network_metrics=values,means={k:{p:float(np.mean(v)) for p,v in data.items()} for k,data in values.items()},comparisons={},cancellation={})
        for k in ['response_mse','passive_mse']:
            diag['comparisons'][k]=paired(values[k]['both'],values[k]['neither'])
            diag['comparisons'][k]['most_influential_network']+=first-20000
        for p in ['neither','stim_only','readouts_only','both']:
            aa=np.mean(values['endpoint_amplitude_term_mse'][p]);bb=np.mean(values['dynamic_term_mse'][p]);cc=np.mean(values['cross_term'][p])
            diag['cancellation'][p]=float(-cc/(aa+bb))
        r=values['response_mse'];delta=np.array(r['both'])-r['stim_only']-np.array(r['readouts_only'])+r['neither']
        ix=np.random.default_rng(20261018).integers(40,size=(10000,40))
        diag['allocation_interaction']=dict(mean_difference=float(delta.mean()),ci95=np.quantile(delta[ix].mean(1),[.025,.975]).tolist(),definition='R_both - R_stim_only - R_readouts_only + R_neither; exploratory, fixed total budget')
        result[label]=diag
    oracle=json.loads((A/'oracle_endpoint_correction.json').read_text())
    net={k:[float(np.mean([r[k] for r in oracle if r['network_id']==n])) for n in range(20000,20040)] for k in ['response_mse','stim_corrected_mse','readouts_corrected_mse','both_corrected_mse']}
    result['oracle_correction']={k:paired(v,net['response_mse']) for k,v in net.items() if k!='response_mse'}
    result['interpretation']='Exact error decomposition is descriptive and includes fitted-parameter compensation. Oracle replacement is diagnostic only. Neither establishes a unique biological mechanism.'
    (A/'mechanism_summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:{'comparisons':v['comparisons'],'cancellation':v['cancellation'],'interaction':v['allocation_interaction']} for k,v in result.items() if k.endswith('cohort')},indent=2))

if __name__=='__main__':main()
