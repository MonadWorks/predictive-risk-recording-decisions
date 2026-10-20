"""Reevaluate held-out predictions at twice the integration resolution."""
from common4 import *
from analyze4 import read_stage,contrast
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse

def worker(nid):
    path=HERE/'runs/integration'/f'{nid}.json'
    if path.exists():return dict(network_id=nid,cached=True)
    records=[];oracle_records=[];matrix_error=0.
    apath=HERE/'runs/oracle_data_fit_audit'/f'{nid}.json'
    audited={r['policy']:r for r in json.loads(apath.read_text())['records']} if apath.exists() else {}
    for condition in CONDITIONS:
        raw=json.loads((HERE/'runs/robustness'/f'{nid}_{condition}.json').read_text())
        cfg,c,t,theta,y,eps,q=make_case(nid,condition)
        for m in [c['model'],t['model']]:
            independent=np.einsum('ia,aj->ij',m.left,m.right)
            err=float(np.linalg.norm(independent-m.J)/max(np.linalg.norm(m.J),1e-15));matrix_error=max(matrix_error,err)
            assert np.isfinite(independent).all() and err<1e-12
            m.substeps=4
        trueq,_=t['model'].responses(theta,t['intervention']);trueq=trueq[t['readouts']]
        if condition=='matched_rank2':
            for stage in ['oracle_combinations','oracle_matched_control']:
                for r in json.loads((HERE/'runs'/stage/f'{nid}.json').read_text())['records']:
                    r=audited.get(r['policy'],r)
                    pred,_=c['model'].responses(c['mu']+c['sd']*np.asarray(r['best']['z']),c['intervention']);pred=pred[c['readouts']]
                    oracle_records.append(dict(policy=r['policy'],original_mse=r['mse'],refined_mse=float(np.mean((pred-trueq)**2)),q_difference_norm=float(np.linalg.norm(pred-r['best']['q_hat']))))
        for r in raw['records']:
            pred,_=c['model'].responses(c['mu']+c['sd']*np.asarray(r['best']['z']),c['intervention']);pred=pred[c['readouts']]
            records.append(dict(condition=condition,policy=r['policy'],original_mse=r['mse'],
                refined_mse=float(np.mean((pred-trueq)**2)),q_difference_norm=float(np.linalg.norm(pred-r['best']['q_hat'])),
                true_q_difference_norm=float(np.linalg.norm(trueq-r['q_true']))))
    dump(path,dict(network_id=nid,complete=True,matrix_product_relative_error=matrix_error,records=records,oracle_records=oracle_records));return dict(network_id=nid)

def summary():
    data=read_stage('integration',range(50000,50040));out={}
    for c in CONDITIONS:
        vals={p:[next(r['refined_mse'] for r in d['records'] if r['condition']==c and r['policy']==p) for d in data] for p in ['neither','both']}
        out[c]=contrast(vals['both'],vals['neither'])
    oracle={}
    for a,b in [('endpoints_recurrence8','ordinary8'),('endpoints_recurrence8','endpoints4'),('endpoints_recurrence8','endpoint_ordinary8')]:
        vals={p:[next(r['refined_mse'] for r in d['oracle_records'] if r['policy']==p) for d in data] for p in [a,b]}
        oracle[a+'_vs_'+b]=contrast(vals[a],vals[b])
    dump(HERE/'analysis/integration_summary.json',dict(contrasts=out,oracle_contrasts=oracle,matrix_product_max_relative_error=max(d['matrix_product_relative_error'] for d in data)))
    print(json.dumps(out,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=2);ap.add_argument('--summary',action='store_true');a=ap.parse_args()
    if a.summary:summary()
    else:
        with ProcessPoolExecutor(a.workers) as ex:
            for f in as_completed([ex.submit(worker,n) for n in range(50000,50040)]):print(json.dumps(f.result()),flush=True)
        summary()
