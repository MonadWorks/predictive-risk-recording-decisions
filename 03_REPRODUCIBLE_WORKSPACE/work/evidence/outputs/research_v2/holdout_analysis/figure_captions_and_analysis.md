# Analysis and figure notes

Phase: `frozen_holdout`. Status: `complete`. Independent connection matrices: 40 of 40 planned.

Each plotted point is one connection matrix J, after equal averaging of the balanced 3 truth draws, 3 noise draws, 3 prespecified targets and (for random designs) 5 design draws. These nested rows are not independent experimental units. All finite predictions, optimizer failures and fallback predictions are retained. Failure rates are evaluation-weighted summaries, not counts of independent optimizer calls.

Primary inference: 97.5% paired network-cluster percentile CI; Bonferroni two-comparison family. Other contrast intervals are exploratory pointwise 95%. Bootstrap resamples 10000 whole networks with replacement (seed 870231); methods share resample indices within each stratum. Development, scale diagnostics, smoke checks and partial runs cannot supply confirmation claims. No p-values, equivalence conclusions or post-hoc sample expansion are computed.

Figures actually available in this directory: `raw_risk`, `normalized_risk`, `primary_paired_effects`, `network_risk_distributions`, `risk_vs_actual_mse`.


`raw_risk`: response MSE in raw q units squared, all strata. Black marks are means and pointwise 95% network-cluster percentile intervals; colored points retain all network means and outliers. Panel y ranges differ; compare numerical axes rather than visual heights across panels.

`normalized_risk`: per-case squared error divided by the common independent nonlinear prior-MC variance. The variance floor remains 1e-16. A network metric is NA if any target is invalid; no valid-target substitution or floor change is made. A full-stratum standardized mean and interval are NA if any network is NA. Axis labels give missing-network counts. `task_scales.csv` lists all scale flags; 0 network-condition-target scales are invalid. Panel y ranges differ.

`primary_paired_effects`: one paired MSE difference per network in the predeclared primary stratum; negative favors the first method. 97.5% paired network-cluster percentile CI; Bonferroni two-comparison family. This figure does not upgrade development or partial results to confirmation.

`network_risk_distributions`: complete raw-risk ECDFs in the specified reference stratum, including tails. Standardized ECDFs show finite network metrics only, with retained/total counts in the legend. This conditional display does not replace a full-stratum estimate and is exploratory.

`risk_vs_actual_mse`: nominal-point and ensemble-averaged local predictive variances against nonlinear actual MSE, aggregated within J; dashed y=x is a calibration reference. Correlations and risk bins are descriptive, not row-level significance tests.

`network_metrics.csv` supplies independent-unit metric summaries and risk-plot coordinates. `primary_paired_plot_data.csv` contains the paired-dot coordinates. `risk_calibration_bins.csv` documents exploratory calibration summaries. `risk_calibration_network_summary.csv` documents exploratory calibration summaries. RMSE is sqrt(mean network MSE); bootstrap recomputes this transformation. Relative MSE differences are ratios of aggregate mean MSEs minus one, not averages of per-network ratios. `leave_one_network_out.csv` reports influence without dropping influential networks. All designs use the same MAP fitting procedure. Coverage refers to a model-internal local Gaussian interval for a noiseless response, not a certified biological or clinical confidence interval. Figures are 300-dpi PNG plus vector PDF with embedded TrueType fonts, fixed method order/colors and shape coding.

Reproduce: `python analyze.py --run work/research_v2/holdout_run --out work/research_v2/holdout_analysis`.
