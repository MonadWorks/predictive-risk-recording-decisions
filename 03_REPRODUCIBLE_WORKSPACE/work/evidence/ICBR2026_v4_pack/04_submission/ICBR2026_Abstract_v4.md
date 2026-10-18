# ICBR 2026 — abstract v4 for author review

17 October 2026. Prepared locally; **not submitted.** No portal login, upload or message was made. The "all authors approved" checkbox in the submission form has not been checked and needs both authors.

## Title (12 words; limit 15)

Prior-Averaged Risk Often Leaves Recording Decisions Unchanged in Partially Observed Neural Networks

Alternative, closer to the v3 title (13 words): *Predictive Risk and Recording Decisions for Stimulus-Response Estimation in Partially Observed Neural Networks*

## Authors

Jiayi Du¹*†, Shuaizhi Cheng²†. ¹ Stiftung Louisenlund, Germany. ² Department of Computing, Harbin Institute of Technology, China. † Equal contribution. * Correspondence: jiayi.du@mail.louisenlund.de (Shuaizhi Cheng: szcheng@stu.hit.edu.cn). Names, order and institution strings unchanged from v3.

## Abstract (paste only the four paragraphs)

Biohybrid neural interfaces can have few usable recording channels, so the choice of channels shapes what can be predicted about a planned stimulus. Goal-oriented design ranks recording sets by their estimated prediction error. A better risk estimate helps the prediction only by changing which neurons are recorded or by forecasting the error more accurately; we tested both routes for averaging local risk over a parameter prior, in simulation only.

We compared single-response and shared three-response objectives, each with a nominal-parameter or prior-averaged risk criterion, in simulated 12-unit networks with known connectivity and uncertain neuronal gains and biases. The target was the time-integrated difference between stimulated and control activity. All methods used the same feasible recording sites, measurement budget and maximum a posteriori estimator. The primary evaluation used 40 independent networks under broad, correctly specified uncertainty, with three recorded neurons and stimulation and readout sites excluded. Each network was simulated with several parameter draws, noise draws and readouts; networks were the unit of analysis.

Prior averaging selected identical recording sets in 82 of 120 target-specific designs (three per network) and 26 of 40 shared designs, so in about two thirds of designs the two criteria recorded the same neurons. Relative to the nominal criterion it changed aggregate mean squared response error by −3.74% for the single-response objective (97.5% paired network-cluster interval, −18.48% to 12.12%) and by +2.69% for the three-response objective (−2.95% to 11.51%); both intervals included zero. A separately specified study on 40 new networks held recordings, data and point predictions fixed and compared risk forecasts with the score log(v) + e²/v, where v is the forecast of the mean squared error and e is the prediction error. The ensemble-minus-nominal difference was −0.45565 (95% interval, −1.15857 to 0.02367), with 19 of 40 networks favouring the ensemble; one network supplied about 64% of the summed difference, and nominal forecast risk was closer to the actual error in aggregate.

An exploratory extension to eight 100-unit networks gave intervals excluding zero in favour of prior averaging in four of eight settings and against it in none (one sign reversal). Neither primary comparison showed a benefit; because the criteria agree in most designs, any benefit can arise only in the minority where they differ. All evidence is computational, and the networks are generic rate models, not a model of any biohybrid platform.

## Short version (274 words, 1943 characters) for a 300-word limit

Biohybrid neural interfaces can have few usable recording channels, so the choice of channels shapes what can be predicted about a planned stimulus. Goal-oriented design ranks recording sets by their estimated prediction error. A better risk estimate helps the prediction only by changing which neurons are recorded or by forecasting the error more accurately; we tested both routes for prior-averaged local risk, in simulation only.

We compared single-response and shared three-response objectives, each with a nominal-parameter or prior-averaged risk criterion, in simulated 12-unit networks with known connectivity and uncertain neuronal gains and biases. The target was the time-integrated difference between stimulated and control activity. All methods used the same feasible recording sites, measurement budget and maximum a posteriori estimator. The primary evaluation used 40 independent networks under broad, correctly specified uncertainty, with three recorded neurons and stimulation and readout sites excluded. Networks were the unit of analysis.

Prior averaging selected identical recording sets in 82 of 120 target-specific and 26 of 40 shared designs. It changed aggregate mean squared response error by −3.74% (97.5% paired network-cluster interval, −18.48% to 12.12%) for the single-response objective and +2.69% (−2.95% to 11.51%) for the shared objective; both intervals included zero. In 40 new networks with recordings and point predictions held fixed, the ensemble-minus-nominal risk-forecast score difference was −0.45565 (95% interval, −1.15857 to 0.02367); one network supplied about 64% of the summed difference.

An exploratory extension to eight 100-unit networks favoured prior averaging in four of eight settings and none against. Neither primary comparison showed a benefit; because the criteria agree in most designs, any benefit can arise only in the minority where they differ. All evidence is computational.

## Checks

- Every number is in the frozen v2 records or in `05_data_and_code/source_data/`; `python validate_pack.py` re-derives 82/120, 26/40, 19/21, the 40-network primary intervals and the four-of-eight count.
- The form limits quoted in v3 (500 words, 5,000 characters, title ≤ 15 words) should be rechecked with the portal's own counter; the site text also mentions 300 words, so the v3 conflict is unresolved. Local counts for the full abstract above: 387 whitespace-delimited words and 2602 characters including spaces and paragraph breaks, below both the 500-word and 5,000-character limits but above 300 words, so a 300-word cut would be needed if the stricter figure applies.
- Keywords, subject areas, funding and conflict fields are unchanged from v3 (`submission_metadata.json`).
- Submission file: `../03_figures/graphical_abstract_v4.pdf` (single vector PDF; check size and fonts with `pdffonts`).
- **What changed after v3:** lead finding is now the decision agreement; the conditional extension result is stated completely (four of eight intervals excluded zero, none in the other direction, one sign reversal); no primary estimate, interval, estimand or test changed.
