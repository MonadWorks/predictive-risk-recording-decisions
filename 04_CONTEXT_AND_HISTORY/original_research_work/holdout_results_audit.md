# Frozen holdout results: independent readback audit

2026-10-16. Only completed holdout raw CSV, protocol, status and existing analysis outputs were read. No model, method, protocol or analysis code was changed. This check used independent csv/NumPy calculations without importing analyze.py.

## Verified contracts

- All 40 planned independent J, all 3 conditions × 2 pools × 2 budgets × 6 methods are present. Each cell has the exact truth × noise × target × design-repeat Cartesian product, with no duplicates.
- Row error equals q_hat−q_true and squared error equals error². All network MSE means agree with network_metrics.csv.
- Same data/node-set reuse gives the same fit diagnostics; unique fit keys reproduce status actual_optimizer_calls.
- Every network-condition-target has a common prior-MC variance across methods, budgets, truths and noise. Frozen floor is retained; invalid counts agree with summary.
- Both primary absolute differences and aggregate MSE ratios, plus 97.5% paired network bootstrap percentile intervals (10,000 resamples, seed 870231), reproduce summary.json. Independent LONO values reproduce leave_one_network_out.csv. Raw/protocol SHA256 receipts agree.

## Independently recomputed numbers

```json
{
  "independent_networks": 40,
  "raw_rows": 129600,
  "network_stratum_method_cells": 2880,
  "unique_optimizer_calls": 38610,
  "fail_rows": 0,
  "fallback_rows": 0,
  "fail_fits": 0,
  "fallback_fits": 0,
  "invalid_scale_network_condition_targets": 0,
  "invalid_scale_rows": 0,
  "invalid_scale_by_condition": {},
  "network_metrics_with_na_normalized": 0,
  "primary": [
    {
      "contrast": "ensemble_scalar - local_scalar",
      "mean_mse_a": 6.649819115986673e-05,
      "mean_mse_b": 6.908461228895778e-05,
      "effect": -2.586421129091058e-06,
      "ci975": [
        -1.471304677118912e-05,
        4.826304931626923e-06
      ],
      "relative_mse_difference": -0.03743845472089957,
      "relative_ci975": [
        -0.18483138282244313,
        0.1211614122926881
      ],
      "positive_networks": 16,
      "negative_networks": 11,
      "exact_ties": 13,
      "loo_min": -4.25933361943963e-06,
      "loo_max": 1.509013047464149e-06,
      "most_influential_omitted_network": 5029,
      "largest_abs_individual_difference": -0.00016230835401474412
    },
    {
      "contrast": "ensemble_vector - local_vector",
      "mean_mse_a": 7.333874130078236e-05,
      "mean_mse_b": 7.141511391035257e-05,
      "effect": 1.923627390429782e-06,
      "ci975": [
        -1.147970762431108e-06,
        6.8260498523981685e-06
      ],
      "relative_mse_difference": 0.026935858323275053,
      "relative_ci975": [
        -0.02952871216667454,
        0.11507999192545666
      ],
      "positive_networks": 6,
      "negative_networks": 8,
      "exact_ties": 26,
      "loo_min": 3.663558737981238e-07,
      "loo_max": 2.2693479684476865e-06,
      "most_influential_omitted_network": 5000,
      "largest_abs_individual_difference": 6.265721653906444e-05
    }
  ]
}
```

## Interpretation boundary

There is no stable ensemble gain in the prespecified primary condition. ES−LS aggregate MSE is about −3.74%, with a 97.5% interval about [−18.48%, +12.12%]; EV−LV is about +2.69%, interval [−2.95%, +11.51%]. Both intervals cross zero. These results do not establish equivalence and do not establish a new-method contribution. Differences over nested rows do not increase the independent sample size above 40.

Visual QA is recorded separately below after inspection.

## Visual QA (completed)

Inspected `holdout_analysis/primary_paired_effects.png` and `raw_risk.png` at their exported dimensions through the image viewer. Both show all network points and retain the large outliers. The primary plot contains the zero line, the correct ES−LS and EV−LV directions, and clearly labelled 97.5% intervals. Means and confidence intervals agree with the tabulated numbers; neither primary interval excludes zero. Raw-risk panels show all 12 condition × pool × budget strata, consistent method order/colours/shapes and explicitly labelled raw MSE units. Labels are readable in the full-resolution export; no clipping was observed. Vertical ranges differ between panels, so cross-panel magnitude comparisons must read numerical axes rather than visual height alone. The 12-panel overview is suitable as a complete appendix/overview figure; a manuscript can present its predeclared primary stratum separately without omitting the overview.

## Influence and interpretation

For ES−LS, the full mean MSE difference is −2.5864211291e−6. Leave-one-network-out means range from −4.2593336194e−6 to +1.5090130475e−6. Omitting J=5029 changes the sign to positive; the apparent small average gain is therefore sensitive to a single influential network, which is retained. There are 13 exact ties, 11 negative differences and 16 positive differences among 40 networks. For EV−LV there are 26 exact ties; the LONO mean remains positive, but its full paired interval crosses zero. Ties are retained as measured outcomes rather than added jitter in the statistical calculation.

No computational inconsistency was found in the requested readback. This audit supports accurate reporting of a mixed/negative primary outcome; it does not certify biological validity, causal transfer to real recordings, equivalence of methods, or a new optimal-design method.
