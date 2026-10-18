# Nondegenerate linear-Gaussian positive control

This is a scientific positive control of the exact predictive-risk-to-MAP-MSE relation. It is a known identity, not new data, an empirical discovery, or an algorithm. Unlike the paired-stimulation additive-bias cancellation null, these linear targets have strictly positive uncertainty and nonzero MAP error.

There are 12 fixed-seed random observation systems, each with 24 parameters, 12 candidate recording nodes, five observations per node, budget three, and three linear targets. Prior and whitened noise are independent standard Gaussians. Three scalar-target and one vector-target selection are run through the unchanged main design.choose function. F/G are constant across parameters, so nominal and 16-particle ensemble designs have identical mathematical objectives; selected IDs must match. Final fixed-set E−N risk and paired actual MSE must be exactly zero. Any machine-precision difference in the numerical greedy cost paths is recorded separately, rather than called an effect.

For each system, a separate stream supplies 8,192 complete parameter truths and full candidate-node noise arrays. These are shared across selection objectives for paired comparison and never used for selection. MAP is independently implemented as (I+F_S.T F_S)^-1 F_S.T y. For each target a, analytic error is a.T C a; independent truth/noise Monte Carlo error is computed from actual MAP predictions. The exact standard error of its Monte Carlo mean squared error is sqrt(2/8192) times the analytic risk. Every cell must fall within the predeclared 5.5-SE bound; no cells are filtered or tuned. The parameter-error covariance identity C²+C F_S.T F_S C=C is also checked.

No formal experimental results or held-out data are read. No packages are installed, no algorithms or existing files are changed. Products use einsum, avoiding platform matmul warning behavior. All outputs must be finite. CSVs contain all 144 target/system/design evaluations. JSON contains protocol, IDs, source hashes, greedy paths, numerical residuals and runtime. PNG and vector PDF show risk/MSE agreement and exactly zero ensemble-minus-nominal fixed-set risk.

Run from workspace root:
```sh
work/research-v2-env/bin/python work/research_v2/linear_risk_control.py
```
