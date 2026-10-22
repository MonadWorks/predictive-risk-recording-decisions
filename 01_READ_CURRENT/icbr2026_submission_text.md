# ICBR 2026 extended-abstract submission text

Not submitted. Official rules (https://icbr2026.org/submission_guidelines.html, checked 22 Oct 2026): abstract of at most 500 words, title of at most 15 words, 2-5 keywords, graphical abstract required, no references, figures or tables in the abstract text. The same page also contains a stray "300-word" sentence, so confirm the field limit in CMT. Extended-abstract deadline on the CFP page: 23 Oct 2026, 23:59 PST.

## Title

Predictive Risk and Recording Decisions in Partially Observed Neural Networks

## Keywords

Biohybrid neural interfaces; Recording-site selection; Predictive uncertainty; Experimental design; Response prediction

## Abstract (490 words by whitespace count)

This text is identical to the Abstract of the current manuscript (`abstract_from_current_manuscript.txt`); if one changes, change both.

Neural interfaces in biohybrid systems use stimulation and recording to interact with living networks. Under a limited recording budget, choosing where to record becomes part of predicting a specified stimulus response. Goal-oriented design ranks recording sets by estimated prediction error. We asked whether averaging this local risk over a parameter prior improves recording decisions, and which recordings make a specified response predictable when connectivity is known but neuronal gains are uncertain.

We first compared nominal-parameter and prior-averaged risk criteria in simulated 12-unit networks with uncertain neuronal gains and biases, with the measurement budget and maximum a posteriori (MAP) estimator held fixed. Across 40 independent networks, prior averaging changed mean squared response error (MSE) by -3.74% for a single-response objective and +2.69% for a shared three-response objective; both paired network-cluster intervals included zero. The two criteria chose identical recordings in 68% and 65% of designs, and a separately specified risk-forecast study did not establish a better forecast. A benefit suggested by an exploratory 100-unit pilot was not confirmed for the shared-response objective in 40 independent 100-unit networks (+7.95%; 95% CI, -23.59% to +20.95%).

In 100-unit rank-two rate networks with all sites available, selectors under both criteria always recorded the stimulation site and included all three readouts in 30 and 38 of 40 networks; we call these four sites the endpoints. We therefore controlled which endpoints occupied five calibration slots, withholding the target stimulus response from fitting. Recording all four endpoints reduced held-out response MSE by 96.44% relative to five non-endpoint recordings in 40 networks, and by 98.13% in an independent 40-network validation (95% CI, -99.19% to -93.94%). The benefit was specific to the intended response, came with narrower numerically feasible response ranges (not calibrated intervals), and weakened at lower recording precision. In the first 40-network cohort, neither criterion showed a clear benefit over this endpoint baseline.

An exact factorization of the finite response into input, recurrent-propagation and readout terms localized the strongest error contraction to the input and readout terms. Oracle controls that revealed true gains suggested that four recurrent gain combinations carry predictive information beyond endpoint gains.

We then asked whether a fifth recording could acquire this information. In 80 further networks, adding a fifth site to the four endpoints reduced response MSE by about 30% (secondary comparisons), but a response-directed choice did not clearly differ from a random fifth site in the prespecified comparison. A site chosen for the recurrent combinations reduced their estimation MSE by 31.07% relative to a random site (secondary comparison; 95% CI, -42.35% to -19.81%) without a clear change in response MSE.

Endpoint benefits persisted under rank-six augmentation and mild connectivity or initial-state errors, with less certainty in independently generated Gaussian rank-six and positive-gain networks. Together, these simulations suggest that endpoint coverage is an informative baseline for evaluating recording criteria, and that better estimation of response-relevant parameters need not translate into better response prediction. Applicability to living networks and mechanical outputs remains to be tested.

## Compact fallback (248 words)

Use only if the CMT field enforces a 300-word limit. Every number below also appears in the full abstract and the manuscript.

Neural interfaces in biohybrid systems use stimulation and recording to interact with living networks. With a limited recording budget, choosing where to record is part of predicting a specified stimulus response. We asked whether averaging local risk over a parameter prior improves recording decisions, and which recordings make a response predictable when connectivity is known but neuronal gains are uncertain.

In simulated 12-unit networks, prior averaging did not establish lower response error than a nominal criterion across 40 independent networks (mean squared error [MSE] change -3.74% and +2.69% for single- and three-response objectives; both intervals included zero). In 100-unit rank-two networks, selectors always recorded the stimulation site and usually the three readouts. Controlling these endpoints at a fixed budget of five recordings, with the target response withheld from fitting, recording all four endpoints reduced held-out response MSE by 96.44% (40 networks) and by 98.13% in an independent 40-network validation (95% confidence interval, -99.19% to -93.94%). The benefit was specific to the intended response and accompanied by narrower numerically feasible response ranges.

An exact response factorization and oracle controls suggested that four recurrent gain combinations carry predictive information beyond endpoint gains. A fifth recording chosen for them reduced their estimation error by 31.07% relative to a random fifth site in 80 further networks (secondary comparison), but did not clearly change response MSE.

These simulations suggest endpoint coverage as an informative baseline for recording decisions, and that better parameter estimation need not give better prediction. Living networks and mechanical outputs remain untested.

## Graphical abstract

`graphical_abstract.pdf` / `.png` / `.svg` in this folder.
