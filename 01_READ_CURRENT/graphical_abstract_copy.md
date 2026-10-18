# Graphical abstract — final copy (v4 layout)

## Title

Predictive risk and recording decisions
in partially observed neural networks

## Network and target

Known connectivity
12 simulated units · M=3
Uncertain gains and biases

- Recorded node
- Stimulated node
- Response readout (one shown)

Integrated stimulus response

q = ∫ Δr(t) dt
Δr(t) = r_stim(t) − r_control(t)

## 1 Recording agreement

40 independent networks

Single-response designs: **68%** — 82 of 120 designs; identical recording sets.
Shared three-response designs: **65%** — 26 of 40 designs; identical recording sets.
Legend: same recording set.

## 2 Response error

Common MAP fit and budget
Same 40 networks

- Single response: −3.7% [−18.5, +12.1]
- Shared three-response: +2.7% [−3.0, +11.5]

Mean-MSE change vs nominal (%)
97.5% paired network-cluster CI

## 3 Risk forecasts

Fixed data and point prediction
40 new independent networks

19 of 40 favour prior averaging; 21 favour nominal.

S(v,e) = log v + e²/v
v: MSE forecast; e: response error

One network accounts for 64% of the summed score difference.

Forecast-score difference: −0.46 [−1.16, +0.02]
Prior-averaged minus nominal
95% paired network-cluster CI

## Four-line footer

We use a **common MAP estimator**. Identical recording sets and data yield identical predictions.

Primary error and forecast-score intervals include zero.

Exploratory 100-unit rank-two family (8 independent networks): 4/8 setting-specific 95% intervals exclude zero.

All four favour prior averaging. These intervals are unadjusted; one point estimate favours nominal.


## v5 key finding

Better risk estimates do not necessarily make better recording decisions.

Exact user-selected wording; leads the lower-right explanation. Existing four explanatory lines retained.
