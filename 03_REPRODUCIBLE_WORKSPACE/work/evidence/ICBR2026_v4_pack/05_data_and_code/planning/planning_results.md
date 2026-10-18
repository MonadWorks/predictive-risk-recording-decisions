# Planning analysis for a possible new confirmatory study

**PLANNING ONLY, not inference.** No hypothesis tests were run on the existing data and no frozen estimate was changed. The 40 existing network-level differences are used only as a rough guide to variability. Script: `planning.py` (numpy only, seed 20261017); machine-readable output: `planning_results.json`.

## (a) Spread of the paired network differences (n = 40 each)

| Quantity | ES-LS (q^2) | EV-LV (q^2) | Forecast score diff |
|---|---:|---:|---:|
| Mean | -2.59e-06 | 1.92e-06 | -0.456 |
| SD | 2.78e-05 | 1.19e-05 | 1.99 |
| Median | 0 | 0 | 0.0265 |
| Robust SD (1.4826 x MAD) | 3.35e-09 | 0 | 0.482 |
| Max single-network share of sum of absolute differences | 0.656 | 0.46 | 0.346 |
| Top network's signed share of the summed difference | 1.57 | 0.814 | 0.64 |
| SD without most influential network | 1.02e-05 | 6.72e-06 | 0.83 |
| Networks with exactly zero difference (of 40) | 13 | 26 | 0 |

SD far above the robust SD and a large top-network share indicate heavy tails. The signed share can exceed 1 when positive and negative differences cancel in the sum. A robust SD near zero reflects many networks where the two designs choose the same recording set (difference exactly 0), so it is not a usable planning SD. The bootstrap grid starts at n = 40, so a minimum of 40 only means the target is met at the smallest n examined.

## (b) Planning sample sizes for a NEW study

Target: expected half-width of the paired interval at most 10%, 5%, 2.5% of the nominal mean MSE (97.5% interval, primary comparisons). Forecast: 95% interval; MSE-relative targets do not apply, so absolute half-widths of 0.4, 0.2, 0.1 score units are used (an assumption). Networks needed by the normal approximation, then the bootstrap half-width by n.

### ensemble_scalar - local_scalar

Nominal (local_scalar) mean MSE = 6.91e-05 q^2.

| Scenario | Method | h<=10% (6.91e-06) | h<=5% (3.45e-06) | h<=2.5% (1.73e-06) |
|---|---|---:|---:|---:|
| observed SD (SD 2.78e-05) | Normal: n required | 82 | 326 | 1301 |
| observed SD | Bootstrap: smallest grid n | 80 | 320 | >640 |
| top network excluded (SD 1.02e-05) | Normal: n required | 11 | 44 | 176 |
| top network excluded | Bootstrap: smallest grid n | 40 | 40 | 320 |

| n | obs normal | obs boot | excl normal | excl boot |
|---:|---:|---:|---:|---:|
| 40 | 9.85e-06 | 9.72e-06 | 3.62e-06 | 3.36e-06 |
| 80 | 6.96e-06 | 6.69e-06 | 2.56e-06 | 2.32e-06 |
| 160 | 4.92e-06 | 4.73e-06 | 1.81e-06 | 1.82e-06 |
| 320 | 3.48e-06 | 3.42e-06 | 1.28e-06 | 1.19e-06 |
| 640 | 2.46e-06 | 2.42e-06 | 9.05e-07 | 8.71e-07 |

Half-widths in q^2 (raw response MSE).

### ensemble_vector - local_vector

Nominal (local_vector) mean MSE = 7.14e-05 q^2.

| Scenario | Method | h<=10% (7.14e-06) | h<=5% (3.57e-06) | h<=2.5% (1.79e-06) |
|---|---|---:|---:|---:|
| observed SD (SD 1.19e-05) | Normal: n required | 14 | 56 | 223 |
| observed SD | Bootstrap: smallest grid n | 40 | 80 | 320 |
| top network excluded (SD 6.72e-06) | Normal: n required | 5 | 18 | 72 |
| top network excluded | Bootstrap: smallest grid n | 40 | 40 | 80 |

| n | obs normal | obs boot | excl normal | excl boot |
|---:|---:|---:|---:|---:|
| 40 | 4.21e-06 | 4e-06 | 2.38e-06 | 2.34e-06 |
| 80 | 2.98e-06 | 2.9e-06 | 1.68e-06 | 1.63e-06 |
| 160 | 2.1e-06 | 2e-06 | 1.19e-06 | 1.16e-06 |
| 320 | 1.49e-06 | 1.48e-06 | 8.42e-07 | 7.98e-07 |
| 640 | 1.05e-06 | 1.04e-06 | 5.95e-07 | 5.77e-07 |

Half-widths in q^2 (raw response MSE).

### forecast score difference (ensemble - nominal, LS, broad, excl. endpoints, M=3)

| Scenario | Method | h<=0.4 (0.4) | h<=0.2 (0.2) | h<=0.1 (0.1) |
|---|---|---:|---:|---:|
| observed SD (SD 1.99) | Normal: n required | 96 | 383 | 1529 |
| observed SD | Bootstrap: smallest grid n | 160 | 640 | >640 |
| top network excluded (SD 0.83) | Normal: n required | 17 | 67 | 265 |
| top network excluded | Bootstrap: smallest grid n | 40 | 80 | 320 |

| n | obs normal | obs boot | excl normal | excl boot |
|---:|---:|---:|---:|---:|
| 40 | 0.618 | 0.592 | 0.257 | 0.254 |
| 80 | 0.437 | 0.422 | 0.182 | 0.182 |
| 160 | 0.309 | 0.311 | 0.129 | 0.129 |
| 320 | 0.219 | 0.215 | 0.0909 | 0.091 |
| 640 | 0.155 | 0.148 | 0.0643 | 0.0648 |

Half-widths in score units (log-score; unitless).

**Caution.** Heavy tails: a handful of networks carry much of the summed difference, so SDs from 40 networks are unstable, the normal approximation is optimistic, and the bootstrap cannot generate tail behaviour that was not among the 40 observed networks (also optimistic). Excluding the top network is a sensitivity range, not an estimate. Treat these n values as lower-bound, order-of-magnitude guides. Normal approx: n = ceil((z*SD/h)^2), z=2.2414 (97.5%) or 1.96 (95%). Bootstrap: resample n networks with replacement from the 40 (or 39) observed differences, take the mean, repeat 2000 times; half-width = half the central percentile interval (1.25-98.75% or 2.5-97.5%) of those means. It is a plug-in sampling-distribution width, not a nested bootstrap CI.

## (c) Computational scaling (from Table 2 study accounting)

| Stage | Setting | J | Records | MAP calls | Runtime (s) | s/record | s/network | s/MAP call |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Development | 12-unit | 8 | 19,200 | 5,696 | 25.4 | 1.32e-03 | 3.17 | 4.46e-03 |
| Frozen recording evaluation | 12-unit | 40 | 129,600 | 38,610 | 356.0 | 2.75e-03 | 8.9 | 9.22e-03 |
| Independent forecast study | 12-unit | 40 | 6,480 | 3,006 | 17.5 | 2.70e-03 | 0.438 | 5.82e-03 |
| Exploratory 100-unit family | 100-unit | 8 | 3,072 | 1,436 | 693.1 | 2.26e-01 | 86.6 | 4.83e-01 |

**Extrapolation (not measured):** EXTRAPOLATION, not measurement: wall time = n * (stage seconds per network), i.e. linear in networks with the stage's own per-network design (truths x noises x readouts, conditions, methods). Ignores parallelism, memory, solver-difficulty changes and different designs; the 100-unit stage has only 8 networks and a different model family.

| Stage | Setting | 160 networks | 640 networks |
|---|---|---:|---:|
| Development | 12-unit | 508 s | 33.9 min |
| Frozen recording evaluation | 12-unit | 23.7 min | 94.9 min |
| Independent forecast study | 12-unit | 70 s | 280 s |
| Exploratory 100-unit family | 100-unit | 3.85 h | 15.40 h |
