"""Write explicit planned protocols before any corresponding outcome run."""
import json
from pathlib import Path

base=dict(family='softplus',neurons=12,dt=.05,steps=120,sample_stride=4,noise_sd=.05,
 connectivity_norm=.65,targets=3,ensemble_size=16,scale_samples=64,scale_floor=1e-16,
 random_sets=5,max_nfev=80,threads=2,pools=['all','exclude_endpoints'],budgets=[3,6],
 methods=['local_scalar','ensemble_scalar','local_vector','ensemble_vector','local_activity','random'],
 model_seed=101,truth_seed=211,noise_seed=307,design_seed=401,scale_seed=503,random_seed=601,
 design='prior-averaged local delta-method predictive variance; same available information',
 vector_target='same three prespecified readouts; equal raw-response weights',
 primary_metric='mean squared raw q error aggregated within J over truth/noise/target/design repeats',
 secondary_metric='mean error^2 divided by common independent nonlinear prior-MC q variance',
 independent_unit='connection matrix J; other repeats nested',
 failure_policy='retain all; on nonfinite optimizer failure predict from nominal prior mean and flag fallback',
 source_scope='independent synthetic simulations; no biological validation or new-method claim',
 bootstrap_replicates=10000,
 primary_stratum=dict(condition='broad',pool='exclude_endpoints',budget=3),
 primary_comparisons=[['ensemble_scalar','local_scalar'],['ensemble_vector','local_vector']],
 primary_interval='97.5% paired network-cluster percentile intervals per comparison; Bonferroni 2-comparison family',
 secondary_comparisons='all other strata and 2x2 interaction exploratory 95% network-cluster intervals')
conditions=[dict(name='matched',prior_sd=.18,mode='both'),
            dict(name='broad',prior_sd=.35,mode='both'),
            dict(name='bias_shift',prior_sd=.18,mode='both',true_bias_shift=.5)]
root=Path(__file__).parent
dev=dict(base,phase='development',network_ids=list(range(2000,2008)),truth_repeats=2,noise_repeats=2,
         conditions=conditions+[dict(name='gain_only',prior_sd=.35,mode='gain'),dict(name='bias_only',prior_sd=.35,mode='bias')],wall_limit_seconds=1200)
main=dict(base,phase='frozen_holdout',network_ids=list(range(5000,5040)),truth_repeats=3,noise_repeats=3,
          conditions=conditions,wall_limit_seconds=3600)
bridge=dict(base,phase='published_model_family_scale_check',family='rank2_tanh',neurons=100,
            network_ids=list(range(8000,8006)),truth_repeats=2,noise_repeats=2,
            conditions=[dict(name='published_gain',prior_sd=.9,mode='gain')],
            ensemble_size=8,scale_samples=32,budgets=[5,10],random_sets=3,wall_limit_seconds=1800,
            adaptations='published rank2 covariance, tau=.5 and signed raw N(1,.9^2) gain; own known random x0, calibration/target inputs, measurement noise and MAP; not figure reproduction')
smoke=dict(dev,phase='implementation_smoke',network_ids=[1900],truth_repeats=1,noise_repeats=1,
           conditions=[conditions[0]],budgets=[3],pools=['all'],random_sets=1,wall_limit_seconds=120)
for name,cfg in [('development',dev),('holdout',main),('rank2_n100',bridge),('smoke',smoke)]:
 p=root/(name+'.json')
 if p.exists():raise RuntimeError('refuse to replace a protocol')
 p.write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n')
