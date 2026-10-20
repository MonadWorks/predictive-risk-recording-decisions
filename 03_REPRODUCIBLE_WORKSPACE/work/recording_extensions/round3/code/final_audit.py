"""Audit finite results and envelope every known feasible response.

Raw optimisation output stays unchanged. A numerical extremum must include
other feasible fits already found. The wider-threshold check must also include
all feasible extrema from the narrower sublevel set.
"""
from common import *
import copy

def envelope(rec,extra=()):
    pr=rec['profile'];cap=rec['best']['objective']+pr['delta'];changes=[]
    candidates=[]
    for i,f in enumerate(rec.get('fits',[])):
        if f['objective']<=cap+1e-5:
            for k,q in enumerate(f['q_hat']):
                candidates.append((k,dict(z=f['z'],q=q,cost=f['objective'],success=f['success'],source='feasible_alternative_fit',fit=i)))
    candidates+=list(extra)
    for s in pr['searches']:
        old=copy.deepcopy(s['chosen'])
        choices=[old]+[c for k,c in candidates if k==s['target'] and c['cost']<=cap+1e-5]
        chosen=max(choices,key=lambda c:s['sign']*c['q'])
        if chosen['q']!=old['q']:
            changes.append(dict(target=s['target'],sign=s['sign'],old_q=old['q'],new_q=chosen['q'],
                change_fraction_of_width=abs(chosen['q']-old['q'])/max(pr['width'][s['target']],1e-15),source=chosen['source']))
            s['chosen']=copy.deepcopy(chosen)
    pr['lower']=[s['chosen']['q'] for s in pr['searches'] if s['sign']==-1]
    pr['upper']=[s['chosen']['q'] for s in pr['searches'] if s['sign']==1]
    pr['width']=(np.asarray(pr['upper'])-pr['lower']).tolist()
    return changes

def main():
    changes=[];raw_width=[];new_width=[];count=0
    for nid in range(40000,40040):
        d=json.loads((HERE/f'runs/profile_validation/{nid}.json').read_text());assert d['complete']
        for r in d['records']:
            assert np.isfinite(r['best']['objective'])
            assert np.all(np.isfinite(r['profile']['width']))
            before=np.mean(np.square(r['profile']['width']));ch=envelope(r)
            for c in ch:c.update(network_id=nid,policy=r['policy'])
            changes+=ch;raw_width.append(before);new_width.append(np.mean(np.square(r['profile']['width'])))
            count+=sum(f['objective']<=r['best']['objective']+2+1e-5 for f in r['fits'])
        dump(HERE/f'runs/profile_audited/{nid}.json',d)
    threshold=[];tc=[]
    for nid in range(40000,40008):
        source=HERE/f'runs/threshold_refined/{nid}.json'
        if not source.exists():source=HERE/f'runs/threshold_check/{nid}.json'
        d=json.loads(source.read_text())
        base=json.loads((HERE/f'runs/profile_audited/{nid}.json').read_text())
        for r in d['records']:
            b=next(x for x in base['records'] if x['policy']==r['policy']);r['fits']=b['fits']
            ch=envelope(r,[(s['target'],dict(s['chosen'],source='feasible_delta2_extreme')) for s in b['profile']['searches']])
            for c in ch:c.update(network_id=nid,policy=r['policy'])
            tc+=ch
            threshold.append(dict(network_id=nid,policy=r['policy'],delta2_width2=float(np.mean(np.square(b['profile']['width']))),
                delta5_width2=float(np.mean(np.square(r['profile']['width']))),
                chosen_success=[s['chosen']['success'] for s in r['profile']['searches']]))
        dump(HERE/f'runs/threshold_audited/{nid}.json',d)
    a=[r['delta5_width2'] for r in threshold if r['policy']=='both'];b=[r['delta5_width2'] for r in threshold if r['policy']=='neither']
    a2=[r['delta2_width2'] for r in threshold if r['policy']=='both'];b2=[r['delta2_width2'] for r in threshold if r['policy']=='neither']
    out=dict(nearoptimal_fits_checked=count,range_envelope_changes=changes,
        max_relative_width2_change=float(np.max(np.abs(np.asarray(new_width)/raw_width-1))),
        threshold_envelope_changes=tc,threshold_records=threshold,
        threshold_delta5=bootstrap_change(a,b),threshold_delta2_same_subset=bootstrap_change(a2,b2),
        explanation='Every known feasible fit is retained. Raw outputs remain unchanged; derived audited files are the analysis inputs.')
    dump(HERE/'analysis/final_range_audit.json',out)
    print(json.dumps({k:v for k,v in out.items() if k!='threshold_records'},indent=2))

if __name__=='__main__':main()
