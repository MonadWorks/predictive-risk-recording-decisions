"""Prespecified independent endpoint contrast; other contrasts secondary."""
import json,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from analyze import paired,write_csv
HERE=Path(__file__).resolve().parent.parent

def main():
    folder=HERE/'validation/runs/endpoint'
    assert len(list(folder.glob('*.done.json')))==40
    rows=[]
    for p in sorted(folder.glob('*.jsonl')):rows += [json.loads(s) for s in p.read_text().splitlines()]
    assert len(rows)==1920
    g=defaultdict(list)
    for r in rows:g[r['policy'],r['network_id']].append(r['response_mse'])
    values={p:[float(np.mean(g[p,n])) for n in range(30000,30040)] for p in ['neither','stim_only','readouts_only','both']}
    comparisons={}
    for a,b in [('both','neither'),('both','stim_only'),('both','readouts_only'),('stim_only','neither'),('readouts_only','neither')]:
        x=paired(values[a],values[b]);x['most_influential_network']+=10000
        x['status']='primary' if (a,b)==('both','neither') else 'secondary'
        comparisons[f'{a}_vs_{b}']=x
    result=dict(scope='40 new independent networks, prospective local freeze',comparisons=comparisons,network_means=values,fit_diagnostics={})
    for p in values:
        rr=[r for r in rows if r['policy']==p]
        bad=[r for r in rr if r['objective']>r['teacher_objective']+1e-6]
        result['fit_diagnostics'][p]=dict(fits=len(rr),success=sum(r['success'] for r in rr),suboptimal=len(bad),error_share_suboptimal=sum(r['response_mse'] for r in bad)/sum(r['response_mse'] for r in rr))
    (HERE/'analysis/validation_summary.json').write_text(json.dumps(result,indent=2)+'\n')
    write_csv(HERE/'analysis/validation_networks.csv',[dict(network_id=30000+i,policy=p,response_mse=v) for p,values_ in values.items() for i,v in enumerate(values_)])
    print(json.dumps(result['comparisons'],indent=2))

if __name__=='__main__':main()
