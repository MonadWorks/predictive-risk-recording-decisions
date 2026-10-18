# ICBR 2026 extended abstract, edition v5 (incremental)

2026-10-18. Prepared locally; **not submitted**. This edition **keeps the approved v3 title and abstract** and changes only what is demonstrably better. The earlier full rewrite (v4/v5-draft) was rejected sentence by sentence; the reasons are below. ICBR accepts an extended abstract plus a graphical abstract only (no references, no extra figures or tables); the form limit is 500 words / 5,000 characters.

## Title: unchanged from v3 (13 words)

Predictive Risk and Recording Decisions for Stimulus-Response Estimation in Partially Observed Neural Networks

Why unchanged: this title is the one you chose by merging earlier options (you wanted “Decisions” and “Partially Observed”; it adds the stimulus-response target). Each candidate I wrote afterwards was worse on a specific point:

| Candidate | Why it is not better |
|---|---|
| *Prior-Averaged Risk Often Leaves Recording Decisions Unchanged in Partially Observed Neural Networks* | States a finding as a headline. The agreement result holds for one primary condition (broad prior, endpoints excluded, 3 recordings, 12 units); agreement for 6 recordings, other pools and the 100-unit family was not tabulated (statistics referee, concern C). “Often” in a title over-generalises. It also drops “stimulus-response estimation”, the target. |
| *Does Prior-Averaged Risk Change Where to Record? Auditing Channel Selection for Neural Interfaces* | More readable, but loses “partially observed”, “stimulus response” and “predictive risk”, which name what was actually studied, and “channel selection” for “neural interfaces” is a wider claim than a 12-unit simulation supports. |
| Earlier options (`title_options.md`) | Shorter but cover only half of the design (decision experiment or forecast test), which is why the merged title was chosen. |

## Abstract: v3 text plus three edits (363 words, 2575 characters; limit 500 / 5,000)

Neural interfaces in biohybrid systems use stimulation and recording to interact with living networks. Under a limited recording budget, choosing where to record becomes part of predicting a specified stimulus response. Goal-oriented design ranks recording sets by their estimated prediction error. We test whether averaging local risk over a parameter prior improves the resulting response prediction or the accuracy of the risk estimate itself.

We compared single-response and shared three-response objectives, each using a nominal-parameter or prior-averaged risk criterion, in simulated 12-unit networks with known connectivity and uncertain neuronal gains and biases. The target was the time-integrated difference between stimulated and control activity. All methods used the same feasible recording sites, measurement budget and maximum a posteriori estimator. The primary evaluation used 40 independent networks under broad, correctly specified parameter uncertainty, with three recorded neurons and stimulation and readout sites excluded. Each network was simulated with several parameter draws, noise draws and readouts; networks were the unit of analysis.

Compared with the nominal criterion, prior averaging changed aggregate mean squared response error by -3.74% for the single-response objective (97.5% paired network-cluster confidence interval, -18.48% to 12.12%) and +2.69% for the three-response objective (-2.95% to 11.51%). Both confidence intervals included zero. The two criteria selected identical recording sets for 82 of 120 target-specific designs (three per network) and 26 of 40 shared designs. To evaluate risk estimates independently of recording selection, a separately specified study used 40 new networks with recordings, data and point predictions held fixed. The primary ensemble-minus-nominal score difference was -0.45565 (95% confidence interval, -1.15857 to 0.02367), using log(v) + e²/v, where v is the estimated mean squared error and e is the response prediction error. Nineteen of 40 networks favoured the ensemble forecast, one network supplied about 64% of the summed difference, and the nominal forecast risk was closer to the actual error in aggregate.

In an exploratory extension to eight independent 100-unit rank-two networks, four of eight settings had 95% intervals that excluded zero, all favouring prior averaging; none excluded zero in the other direction, and one setting reversed in sign. Under the shared fitting procedure, prior averaging can affect response prediction only by changing which neurons are recorded.

## Word-level change log against the approved v3 abstract (311 words)

| # | Where | v3 wording | New wording | Why it is better |
|---|---|---|---|---|
| 1 | Methods, last sentence | “Truth, noise and readout repetitions were nested within networks.” | “Each network was simulated with several parameter draws, noise draws and readouts; networks were the unit of analysis.” | “Nested” is statistical jargon for a robotics audience; the new sentence says what was repeated and names the unit of analysis explicitly. Same content, plain words. |
| 2 | Results, after the score definition | (nothing) | “Nineteen of 40 networks favoured the ensemble forecast, one network supplied about 64% of the summed difference, and the nominal forecast risk was closer to the actual error in aggregate.” | The score difference of −0.456 looks like a modest favourable effect. One network (−11.67) supplies about 64% of the sum, and in aggregate the ensemble forecast was further from the actual error. The v3 text omitted both; leaving them out lets a reader over-read the number. Verified in `fig3_networks.csv` and `forecast_summary.json`. |
| 3 | Extension, first sentence | “…the direction of the error difference varied with the response objective and recording budget.” | “…four of eight settings had 95% intervals that excluded zero, all favouring prior averaging; none excluded zero in the other direction, and one setting reversed in sign.” | “Varied” says nothing checkable and hides that the exploratory signal leans toward prior averaging. The new sentence is exact (checked against `n100_paired_effects.csv`), reports the favourable and the reversed settings together, and keeps “exploratory”. |

Everything else is **byte-identical** to v3: the opening, the problem statement, the methods, the two primary effects with intervals, the agreement counts, the score definition, and the final sentence about the shared fitting procedure (which you had deliberately chosen to replace a repeated conclusion).

## Candidates I tried and rejected

| Candidate sentence (from my full rewrite) | Why rejected |
|---|---|
| Opening: “Biohybrid robots rely on neural interfaces that can record from only a few channels…” | No citation supports “only a few channels”, and the literature pass found none. v3’s opening makes no unsupported claim. |
| Ending: “For interface designers the practical check is cheap: count how often a criterion changes the recorded channels…” | This is the generic significance sentence you removed in the earlier revision, and it generalises from one 12-unit setting. Not restored. |
| Ending: “…an improved criterion can act only in the minority of designs where the criteria differ.” | Follows by construction rather than from data, and duplicates v3’s final sentence (“can affect response prediction only by changing which neurons are recorded”). v3 is shorter and already says it. |
| Reordering Results to put agreement first | Changes the structure you had settled on (primary effects, then agreement, then the independent forecast test) without a reason strong enough to outweigh the continuity. |
| “where v is the forecast of the mean squared error” | v3’s “estimated mean squared error” is already clear; no gain. |
| Four bold headings (Objective / Methods / Results / Conclusion) | Optional per the venue, cost about 4 words and make the portal text busier; v3’s four paragraphs already follow that order. |
| Longer Results with the 5-number extension example | Gave the exploratory result more room than the primary result. |

## Checks

- All numbers: `python validate_pack.py` (agreement counts, both primary effects and intervals, forecast score and interval, 19/21, four-of-eight). The 64% and “closer in aggregate” statements are from `forecast_summary.json` (nominal risk 1.19e-4, ensemble 1.92e-4, actual MSE 1.18e-4) and `fig3_networks.csv`.
- No references, tables or figures; plain-text math.
- Counts: 363 words, 2575 characters including paragraph breaks.
- Graphical abstract: `../03_figures/graphical_abstract_v5.pdf` if the redesign is accepted, otherwise `graphical_abstract_v4.pdf`.

## What v4 pushed too far for an abstract-only venue

| v4 choice | Decision |
|---|---|
| Three full-paper layouts, one with an “Appearing in ICML 2025” footer | ICBR needs no full paper. Keep the Nature-style PDF as the reference manuscript for a later journal version; the ICML and IEEE layouts are optional and not part of this submission. |
| Key points, contents line, evidence ledger | Manuscript only; not allowed in an abstract. |
| Repeated “simulation only” | Kept once in the abstract (already in v3’s framing) and once in the graphical abstract footer. |
| New title and new abstract | Reverted, as explained above. |

## Author contributions (decided by you: equal contribution)

J.D. and S.C. contributed equally to this work, including conceptualisation, methodology, investigation, visualisation and writing. Both authors approved the final manuscript.

This matches the “† These authors contributed equally” marker already in the author block, graphical abstract and form, so nothing else needs to change. The portal still needs a presenting author (not yet chosen).
