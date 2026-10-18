"""Network-paired summaries; every policy and every network is retained."""
import argparse, csv, json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(HERE.parent/'code'))
from models import seeded

def rows(phase,complete=True):
    paths=sorted((HERE/'runs'/phase).glob('*.jsonl'))
    done=sorted((HERE/'runs'/phase).glob('*.done.json'))
    if complete:assert len(done)==40,(phase,len(done))
    output=[]
    for p in paths:
        if not p.with_suffix('.done.json').exists():continue
        output += [json.loads(line) for line in p.read_text().splitlines()]
    return output

def paired(a,b):
    a=np.asarray(a);b=np.asarray(b);n=len(a)
    assert n==40 and np.isfinite(a).all() and np.isfinite(b).all()
    ix=seeded(20261018,0).integers(n,size=(10000,n))
    effect=100*(a.mean()/b.mean()-1)
    boot=100*(a[ix].mean(1)/b[ix].mean(1)-1)
    diff=a-b
    loo=[100*(np.delete(a,i).mean()/np.delete(b,i).mean()-1) for i in range(n)]
    return dict(mean_a=float(a.mean()),mean_b=float(b.mean()),relative_change_percent=float(effect),
        ci95_percent=np.quantile(boot,[.025,.975]).tolist(),wins=int(np.sum(diff < -1e-15)),ties=int(np.sum(np.abs(diff)<=1e-15)),
        leave_one_out_range_percent=[min(loo),max(loo)],largest_absolute_difference_fraction=float(np.max(np.abs(diff))/max(np.sum(np.abs(diff)),1e-300)),
        most_influential_network=20000+int(np.argmax(np.abs(diff))))

def means(data,key='response_mse'):
    grouped=defaultdict(list)
    for r in data:grouped[r['policy'],r['network_id']].append(float(r[key]))
    policies=sorted({r['policy'] for r in data})
    return {p:[float(np.mean(grouped[p,n])) for n in range(20000,20040)] for p in policies}

def write_csv(path,rr):
    keys=list(dict.fromkeys(k for r in rr for k in r))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rr)

def endpoint():
    rr=rows('endpoint');assert len(rr)==1920
    for r in rr:
        true=.9*seeded(211,r['network_id'],r['truth_id']).normal(size=100)
        err=(np.asarray(r['theta'])-true)**2
        ends={r['stim'],*r['readouts']}
        r['stim_gain_mse']=float(err[r['stim']])
        r['readout_gain_mse']=float(err[r['readouts']].mean())
        r['other_gain_mse']=float(err[[i for i in range(100) if i not in ends]].mean())
        r['provably_suboptimal']=r['objective']>r['teacher_objective']+1e-6
    network=means(rr)
    old=[]
    for p in (HERE.parent/'runs').glob('confirmation_shard_*/results.csv'):
        with p.open() as f:old.extend(csv.DictReader(f))
    for p in ['local_vector','ensemble_vector','local_activity','random']:
        network[p]=[float(np.mean([float(r['squared_error']) for r in old if int(r['network_id'])==n and r['method']==p and r['pool']=='all' and int(r['budget'])==5])) for n in range(20000,20040)]
    contrasts=[('both','neither'),('both','stim_only'),('both','readouts_only'),('stim_only','neither'),('readouts_only','neither'),('local_vector','both'),('ensemble_vector','both'),('both','random'),('both','local_activity')]
    summary=dict(scope='retrospective controlled recording allocation, original common estimator, 40 previously used networks',comparisons={f'{a}_vs_{b}':paired(network[a],network[b]) for a,b in contrasts},network_means=network,fit_diagnostics={})
    for p in ['neither','stim_only','readouts_only','both']:
        data=[r for r in rr if r['policy']==p];bad=[r for r in data if r['provably_suboptimal']]
        summary['fit_diagnostics'][p]=dict(calls=len(data),success=sum(r['success'] for r in data),suboptimal=len(bad),error_share_suboptimal=sum(r['response_mse'] for r in bad)/sum(r['response_mse'] for r in data))
    summary['gain_errors']={k:means(rr,k) for k in ['stim_gain_mse','readout_gain_mse','other_gain_mse']}
    summary['gain_comparisons']={k:{f'{a}_vs_{b}':paired(v[a],v[b]) for a,b in [('both','neither'),('stim_only','neither'),('readouts_only','neither'),('both','stim_only'),('both','readouts_only')]} for k,v in summary['gain_errors'].items()}
    (HERE/'analysis/endpoint_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    write_csv(HERE/'analysis/endpoint_fit_summary.csv',[{k:v for k,v in r.items() if not isinstance(v,list)} for r in rr])
    return summary

def fitting():
    rr=rows('fit_primary');assert len(rr)==1600
    grouped=defaultdict(list)
    for r in rr:grouped[r['network_id'],r['truth_id'],r['noise_id'],r['policy']].append(r)
    nominal=[];best=[];diagnostics=[]
    for key,data in grouped.items():
        n=next(r for r in data if r['start']=='nominal')
        b=min(data,key=lambda r:r['objective'])
        nominal.append(n);best.append(b)
        diagnostics.append(dict(network_id=key[0],truth_id=key[1],noise_id=key[2],policy=key[3],
            nominal_objective=n['objective'],best_objective=b['objective'],best_start=b['start'],
            nominal_mse=n['response_mse'],best_mse=b['response_mse'],teacher_objective=b['teacher_objective'],
            best_suboptimal=b['objective']>b['teacher_objective']+1e-6,
            substantial_objective_improvement=b['objective']<n['objective']-max(1e-5,1e-4*abs(n['objective']))))
    nv=means(nominal);bv=means(best)
    summary=dict(scope='retrospective same recorded data, common five-start MAP selected by objective only',
        original=paired(nv['ensemble_vector'],nv['local_vector']),best_of_five=paired(bv['ensemble_vector'],bv['local_vector']),
        within_method={p:paired(bv[p],nv[p]) for p in nv},network_means_nominal=nv,network_means_best=bv,
        diagnostics={})
    for p in nv:
        data=[r for r in diagnostics if r['policy']==p]
        summary['diagnostics'][p]=dict(fits=len(data),substantial_improvements=sum(r['substantial_objective_improvement'] for r in data),
            original_suboptimal=sum(r['nominal_objective']>r['teacher_objective']+1e-6 for r in data),
            best_suboptimal=sum(r['best_suboptimal'] for r in data),
            best_suboptimal_error_fraction=sum(r['best_mse'] for r in data if r['best_suboptimal'])/sum(r['best_mse'] for r in data))
    summary['optimizer_success']=sum(r['success'] for r in rr)
    (HERE/'analysis/fitting_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    write_csv(HERE/'analysis/fitting_trials.csv',diagnostics)
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['endpoint','fit_primary','both'],default='both');a=ap.parse_args()
    if a.phase in ['endpoint','both']: print(json.dumps({'endpoint':endpoint()['comparisons']},indent=2))
    if a.phase in ['fit_primary','both']: print(json.dumps({'fitting':fitting()},indent=2))
