from common import *
from profiles_conditioned import extremes
from fast_values import FastProblem
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse

def threshold_worker(nid):
    dest=HERE/'runs/threshold_check'/f'{nid}.json'
    if dest.exists():return dict(network_id=nid,cached=True)
    raw=json.loads((HERE/'runs/profile_validation'/f'{nid}.json').read_text())
    cfg,case=case_for(nid);theta,y,eps,trueq=data_for(case,cfg);records=[]
    for label in ['neither','both']:
        rec=next(r for r in raw['records'] if r['policy']==label);nodes=rec['nodes'];sigma=np.array(rec['sigma'])
        p=FastProblem(case,cfg,nodes,y[:,:,nodes]+sigma*eps[:,:,nodes],sigma)
        pr=extremes(p,rec['best'],5.)
        records.append(dict(policy=label,best=rec['best'],profile=pr))
    dump(dest,dict(network_id=nid,complete=True,records=records));return dict(network_id=nid,complete=True)

def integration_audit():
    checks=[];ranges=[]
    for nid in range(40000,40040):
        raw=json.loads((HERE/'runs/profile_audited'/f'{nid}.json').read_text())
        cfg,case=case_for(nid);case['model'].substeps=4
        # Keep the original observations exactly: do not regenerate data with a
        # different integrator when checking an already fitted objective.
        _,original=case_for(nid);theta,y,eps,trueq=data_for(original,cfg)
        for rec in raw['records']:
            nodes=rec['nodes'];sigma=np.asarray(rec['sigma']);p=FastProblem(case,cfg,nodes,y[:,:,nodes]+sigma*eps[:,:,nodes],sigma)
            best_fine_cost=p.cost_value(np.asarray(rec['best']['z']));fine_q=[]
            for s in rec['profile']['searches']:
                point=s['chosen'];z=np.asarray(point['z']);k=s['target'];q=p.q_value(z)[k];cost=p.cost_value(z)
                width=max(rec['profile']['width'][k],1e-12);fine_q.append((k,s['sign'],float(q)))
                checks.append(dict(network_id=nid,policy=rec['policy'],target=k,sign=s['sign'],
                    absolute_q_change=float(abs(q-point['q'])),q_change_fraction_of_width=float(abs(q-point['q'])/width),
                    objective_change=float(cost-point['cost']),fine_constraint_excess=float(cost-rec['best']['objective']-2),
                    fine_constraint_excess_centered=float(cost-best_fine_cost-2)))
            widths=[next(q for k,sign,q in fine_q if k==i and sign==1)-next(q for k,sign,q in fine_q if k==i and sign==-1) for i in range(3)]
            ranges.append(dict(network_id=nid,policy=rec['policy'],width2=float(np.mean(np.square(widths)))))
    out=dict(points=len(checks),max_q_change_fraction_of_width=max(c['q_change_fraction_of_width'] for c in checks),
             max_abs_objective_change=max(abs(c['objective_change']) for c in checks),
             max_fine_constraint_excess=max(c['fine_constraint_excess'] for c in checks),
             max_centered_fine_constraint_excess=max(c['fine_constraint_excess_centered'] for c in checks),
             fine_primary_width_effect=bootstrap_change([r['width2'] for r in ranges if r['policy']=='both'],[r['width2'] for r in ranges if r['policy']=='neither']),
             fine_ranges=ranges,records=checks)
    dump(HERE/'analysis/integration_audit.json',out)
    print(json.dumps({k:v for k,v in out.items() if k not in ['records','fine_ranges']}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['threshold','integration']);ap.add_argument('--workers',type=int,default=4);a=ap.parse_args()
    if a.phase=='integration':integration_audit()
    else:
        with ProcessPoolExecutor(a.workers) as ex:
            for f in as_completed([ex.submit(threshold_worker,n) for n in range(40000,40008)]):print(json.dumps(f.result()),flush=True)
