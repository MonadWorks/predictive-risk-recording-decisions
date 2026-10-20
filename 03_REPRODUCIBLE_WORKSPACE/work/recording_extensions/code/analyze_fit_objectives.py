"""Use the known generating parameter as a feasible-point MAP diagnostic.

An optimizer objective above that at the teacher parameter certifies a
suboptimal returned fit. This is an oracle analysis of simulation records,
not a recording policy and not a replacement of experimental outcomes.
"""
from pathlib import Path
from collections import defaultdict
import csv,json
import numpy as np
from models import seeded

ROOT=Path(__file__).resolve().parent.parent


def main():
    rows=[]
    cfg=json.loads((ROOT/'protocols/mechanism.json').read_text())
    for p in (ROOT/'runs').glob('mechanism_shard_*/results.csv'):
        with p.open() as f:rows.extend(csv.DictReader(f))
    groups=defaultdict(list)
    for r in rows:
        groups[(int(r['network_id']),r['condition'],int(r['budget']),r['method'],int(r['truth_id']),int(r['noise_id']))].append(r)
    noise_cache={};prior_cache={};out=[]
    for key,rs in sorted(groups.items()):
        nid,condition,budget,method,truth_id,noise_id=key
        if (nid,truth_id) not in prior_cache:
            z=seeded(cfg['truth_seed'],nid,truth_id).normal(size=cfg['neurons'])
            prior_cache[nid,truth_id]=float(.5*np.dot(z,z))
        if (nid,truth_id,noise_id) not in noise_cache:
            noise_cache[nid,truth_id,noise_id]=seeded(cfg['noise_seed']+noise_id,nid,truth_id).normal(size=(2,len(range(0,cfg['steps'],cfg['sample_stride'])),cfg['neurons']))
        nodes=list(map(int,rs[0]['nodes'].split(';')))
        noise=noise_cache[nid,truth_id,noise_id][:,:,nodes]
        feasible=float(.5*np.sum(noise*noise)+prior_cache[nid,truth_id])
        objective=float(rs[0]['fit_objective'])
        out.append(dict(zip(['network_id','condition','budget','method','truth_id','noise_id'],key),
             fitted_objective=objective,teacher_feasible_objective=feasible,
             certified_suboptimal=objective>feasible+1e-6,
             objective_ratio=objective/feasible,
             response_mse=float(np.mean([float(r['squared_error']) for r in rs])),
             optimizer_success=rs[0]['optimizer_success']=='True'))
    summary=[];strata=defaultdict(list)
    for r in out:strata[r['condition'],r['budget'],r['method']].append(r)
    for key,rs in sorted(strata.items()):
        bad=[r for r in rs if r['certified_suboptimal']]
        total=sum(r['response_mse'] for r in rs)
        summary.append(dict(zip(['condition','budget','method'],key),fits=len(rs),
             certified_suboptimal_fits=len(bad),networks_with_suboptimal_fit=len(set(r['network_id'] for r in bad)),
             fraction_response_error_in_suboptimal_fits=sum(r['response_mse'] for r in bad)/total,
             overall_mse=total/len(rs)))
    for name,data in [('teacher_objective_comparison.csv',out),('teacher_objective_summary.csv',summary)]:
        with (ROOT/'analysis'/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
