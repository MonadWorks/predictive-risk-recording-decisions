# Development-only mechanism diagnostics

Only development_run is read. Its frozen model snapshot, protocol, model receipts, designs and Q truths are hash-verified or cross-checked. No holdout data, model optimization or protocol changes are involved. All conditions, networks, truths and three readouts remain in raw tables; no error-based filtering is performed.

The signed Q Taylor remainder is q(true)-q(mu)-grad q(mu)^T(true-mu). It is recorded in raw integrated-rate units and divided by the same archived independent prior-MC sigma used in the experiment. The original variance floor is retained. Invalid scales are empty CSV fields and null JSON, not zero. Their counts are reported; normalized summaries use available scaled targets, so cannot silently represent all targets.

The calibration diagnostic is the norm of the sampled-rate first-order prediction remainder divided by the norm of the actual parameter-induced change. This uses noiseless teacher signals, the same calibrated trials and sample stride, and the nominal model gradient. It is not fitted error or measurement noise. A zero change denominator is NA.

Jaccard compares recording sets from local versus ensemble criteria within the same scalar/vector objective, pool, budget, and scalar target. Direct target inclusion is evaluated in the all pool: scalar refers to its own readout; vector reports the fraction of the three readouts included. Nested target/truth/budget repeats are averaged within J before network-level summaries; networks, not repetitions, are the independent unit. SD/SEM do not certify an effect.

These are descriptive tests of nonlinear approximation and recording-set stability, not causal mechanism attribution, biological validation or method innovation. Raw data and missingness must accompany any interpretation. All source and input hashes are in report.json. Runtime and figure versions are recorded by the outputs. Figure has been generated as both PNG and vector PDF.

Run from workspace root:
```sh
work/research-v2-env/bin/python work/research_v2/mechanism.py
```
No packages are installed. Python bytecode writes are disabled and Numba/plot/font caches are redirected under this result directory; the frozen experiment is unchanged.
