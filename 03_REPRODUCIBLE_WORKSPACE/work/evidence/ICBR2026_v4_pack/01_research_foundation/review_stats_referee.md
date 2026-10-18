# Referee report: paper_v4 (statistical/methods)

## 1. Summary
In simulated 12-unit networks, prior-averaged local risk picks the same 3-node recording set as the nominal criterion in 82/120 single-response and 26/40 shared designs. Aggregate MSE changes are -3.74% [-18.48, 12.12] and +2.69% [-2.95, 11.51] (97.5% intervals). The forecast-score difference is -0.45565 [-1.15857, 0.02367]. A 100-unit exploratory family (n=8) has 4/8 intervals favouring the ensemble. The paper proposes an audit framework and a confirmatory test.

## 2. Major concerns
**A. Bound language.** "a large benefit of prior averaging is not compatible with these data" (D1b); "rules out mean-MSE reductions larger than about 3%" (Key points). 26/40 differences are exactly zero and the rest are heavy-tailed, so a percentile bootstrap of a ratio of means is not a sharp bound. Fix: say "the interval's lower limit is -2.95%, sensitive to the heavy tail"; drop "not compatible".

**B. Confirmatory hypothesis.** "the number of independent networks from the planning calculation" (F3); "sample-size-planned" (Contribution v). The planning is 12-unit and precision-based. Nothing covers the 100-unit shared objective, and the two settings were chosen after seeing the results (winner's curse). Fix: say the planning gives only an order of magnitude for the 12-unit comparisons. Say the 100-unit size needs a pilot SD. Replace "sample-size-planned" with "candidate hypothesis".

**C. Generality.** The title and Conclusions ("in the simulated networks studied here") rest on one condition: broad, endpoints excluded, M=3, N=12. Agreement for M=6, other pools and the 100-unit family is unreported. Fix: qualify "in the primary condition", or tabulate agreement from existing records.

**D. "Independent" follow-up.** The freeze is local, with the same authors and code. Fix: use "separately specified" throughout.

**E. Non-replication.** The first study's ratios (1.103 ensemble vs 1.615 nominal) favoured the ensemble. The follow-up reverses this (forecast_summary.json: nominal risk 1.19e-4 and ensemble 1.92e-4 against MSE 1.18e-4). Fix: say explicitly that the calibration hint did not replicate.

**F. Numbering.** The evidence ledger is Table 3 and precedes Table 2 (Methods). Renumber.

## 3. Planning numbers (F1/F2)
All match planning_results.md: 82/326/1301, 14/56/223, 11/44/176, bootstrap 80/320/>640 and 40/80/320, forecast 160/640/>640, share 66% (0.656), 0.48 s per call, 3.85 h and 15.4 h.

One correction: "about 40" for the shared comparison is the bootstrap grid minimum, since the normal value is 14. Add "(grid minimum)". The shared 40-network half-width is already about 7%, so the 10% target is trivially met. The per-network timings compare different record counts (27 vs 12).

## 4. Contributions paragraph
- (iii) "interval bounds that rule out large benefits": overclaims (see A).
- (v) "sample-size-planned": overclaims (see B).
- (i) "keeps task specialisation apart": only partly true. The interaction contrast is NaN in n100_paired_effects.csv, and the scalar and vector objectives also differ in target count.
- (iv) "needed to repeat the audit on other criteria": untested. Say "intended to be reusable".
- (ii) is fair.

## 5. "Identical by construction"
This is justified, but the conditions are scattered across Methods. The MAP objective uses only the fitted data. The initial point is the prior mean. Subsets come from one common noise field per (network, truth, noise). Solver settings are identical. Add one sentence listing these and stating that the solver is deterministic. Methods also say identical data "may reuse" a fit, so some identity is by caching; say so. The 39/80 exact-zero cells (13+26) agree with the design counts.

## 6. Verified numbers
- Identical designs 82/120 and 26/40 (holdout_design_agreement.csv).
- Mean differences -2.586e-6 and +1.924e-6; exact zeros 13 and 26 (holdout_primary_paired.csv).
- Single-response max share 1.623e-4/2.474e-4 = 0.656.
- Table 1 RMSE² gives -3.74% and +2.69%.
- Forecast: the mean of the other 39 networks is -0.17.
- N=100 intervals for ES excl M5, EV excl M10 and ES excl M10 match the CSV.
- Not verifiable: the first-study 1.615 and 1.103 ratios (files absent).

The 100-unit percentage intervals (for example [-98.81, -8.92]) come from 8-network bootstraps and are unstable; say so.

## 7. Verdict
The descriptive conclusions follow: usually the same recordings, and no established gain or equivalence. The hedged "conditional benefit" language is acceptable. The "rules out large benefits" and "sample-size-planned" framings do not follow from the evidence. Minor revision is required.
