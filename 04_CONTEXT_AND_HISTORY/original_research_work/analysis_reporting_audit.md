# Analysis-report wording audit

2026-10-16. Only reporting text/inventory logic in analyze.py changed. No model, protocol, metric, bootstrap, method, sampling unit or primary effect definition changed. Existing run directories were read; no simulations or fits were rerun. Existing output directories were retained.

Each dataset was reanalyzed after capturing all pre-existing numerical CSV SHA256 values, primary effect objects, metric summaries and calibration diagnostics. All are unchanged. N100 now explicitly states that it has no primary comparison and all contrast intervals are exploratory 95%; its notes name only figures/source-data files present in the output directory. Development reference comparisons remain exploratory, despite retaining their protocol-specified interval levels. The completed frozen holdout retains its actual 97.5% two-comparison Bonferroni primary family.

```json
[
  {
    "dataset": "rank2_n100_refined",
    "numerical_csv_count": 6,
    "all_csv_sha256_unchanged": true,
    "primary_objects_unchanged": true,
    "metric_summaries_unchanged": true,
    "calibration_diagnostics_unchanged": true,
    "primary_interval": "not applicable: no primary comparison specified; all reported contrast intervals exploratory 95%",
    "available_figures": [
      "raw_risk",
      "normalized_risk"
    ]
  },
  {
    "dataset": "development",
    "numerical_csv_count": 9,
    "all_csv_sha256_unchanged": true,
    "primary_objects_unchanged": true,
    "metric_summaries_unchanged": true,
    "calibration_diagnostics_unchanged": true,
    "primary_interval": "reference comparisons use protocol-specified 97.5% paired cluster intervals; exploratory only, no confirmatory inference",
    "available_figures": [
      "raw_risk",
      "normalized_risk",
      "primary_paired_effects",
      "network_risk_distributions",
      "risk_vs_actual_mse"
    ]
  },
  {
    "dataset": "holdout",
    "numerical_csv_count": 9,
    "all_csv_sha256_unchanged": true,
    "primary_objects_unchanged": true,
    "metric_summaries_unchanged": true,
    "calibration_diagnostics_unchanged": true,
    "primary_interval": "97.5% paired network-cluster percentile CI; Bonferroni two-comparison family",
    "available_figures": [
      "raw_risk",
      "normalized_risk",
      "primary_paired_effects",
      "network_risk_distributions",
      "risk_vs_actual_mse"
    ]
  }
]
```

New analysis SHA256: `f7d834df47f775490b7627cd58cc9bdf955816188a13d7b5549a6878fdc764a5`. Every updated summary.json records this same hash. Frozen simulation source receipts and protocols were not rewritten.
