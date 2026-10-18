# ICBR 2026 — revised abstract for author review

17 October 2026. Prepared locally; **not submitted**. The title and abstract below are the recommended working version. Other title choices are in [title_options.md](title_options.md).

## Title

Predictive Risk and Recording Decisions for Stimulus-Response Estimation in Partially Observed Neural Networks

## Authors and affiliations

Jiayi Du¹*†, Shuaizhi Cheng²†

¹ Stiftung Louisenlund, Germany  
² Department of Computing, Harbin Institute of Technology, China

† These authors contributed equally to this work.  
* Correspondence: Jiayi Du, jiayi.du@mail.louisenlund.de  
Shuaizhi Cheng: szcheng@stu.hit.edu.cn

Preserve the names, order and institution strings exactly. Footnote markers belong in the graphical abstract and author note, not in CMT name fields. The graphical abstract includes the equal-contribution designation because the supplied form does not show a dedicated field for it.

## Abstract — paste only the following four paragraphs

Neural interfaces in biohybrid systems use stimulation and recording to interact with living networks. Under a limited recording budget, choosing where to record becomes part of predicting a specified stimulus response. Goal-oriented design ranks recording sets by their estimated prediction error. We test whether averaging local risk over a parameter prior improves the resulting response prediction or the accuracy of the risk estimate itself.

We compared single-response and shared three-response objectives, each using a nominal-parameter or prior-averaged risk criterion, in simulated 12-unit networks with known connectivity and uncertain neuronal gains and biases. The target was the time-integrated difference between stimulated and control activity. All methods used the same feasible recording sites, measurement budget and maximum a posteriori estimator. The primary evaluation used 40 independent networks under broad, correctly specified parameter uncertainty, with three recorded neurons and stimulation and readout sites excluded. Truth, noise and readout repetitions were nested within networks.

Compared with the nominal criterion, prior averaging changed aggregate mean squared response error by -3.74% for the single-response objective (97.5% paired network-cluster confidence interval, -18.48% to 12.12%) and +2.69% for the three-response objective (-2.95% to 11.51%). Both confidence intervals included zero. The two criteria selected identical recording sets for 82 of 120 target-specific designs (three per network) and 26 of 40 shared designs. To evaluate risk estimates independently of recording selection, a separately specified study used 40 new networks with recordings, data and point predictions held fixed. The primary ensemble-minus-nominal score difference was -0.45565 (95% confidence interval, -1.15857 to 0.02367), using log(v) + e²/v, where v is the estimated mean squared error and e is the response prediction error.

In an exploratory extension to eight independent 100-unit rank-two networks, the direction of the error difference varied with the response objective and recording budget. Under the shared fitting procedure, prior averaging can affect response prediction only by changing which neurons are recorded.

---

## Submission fields and local checks

- Abstract: **311 whitespace-delimited words**, 337 under a conservative punctuation split; **2,260 Unicode characters** including spaces and paragraph breaks. Both are below 500 words and 5,000 characters. The actual portal counter remains the final check.
- Title: 13 whitespace-delimited words.
- Keywords: biohybrid robotics; neural interfaces; goal-oriented design; sensor selection; predictive risk
- Primary subject: c. Modeling, actuation, sensing, and control of biohybrid robots
- Secondary subject: d. Data fusion and intelligence of biohybrid robots
- Funding Information: **None**. Conflicts of Interest: **None**. Both explicitly confirmed by the user.
- Primary contact: Jiayi Du, jiayi.du@mail.louisenlund.de.
- Submission file: [graphical_abstract.pdf](graphical_abstract/graphical_abstract.pdf), a single vector PDF under 10 MB. [PNG preview](graphical_abstract/graphical_abstract.png) and editable SVG are retained locally.
- No full manuscript is required or prepared for upload.

## What changed after the writing review

The unspecified causal disclaimer and generic significance sentences were removed. The opening now states a concrete recording-and-response problem; the score is defined; and a descriptive readback of frozen recording sets explains a specific source of identical predictions. The end retains the primary uncertainty and conditional extension result without asserting a general mechanism. The primary numbers, estimands and statistical tests are unchanged.

The agreement counts come from frozen `holdout_run/designs.json`: 82/120 target-specific designs (three per network) and 26/40 shared designs, all nested within the same 40 networks. This is a descriptive count, not a new primary hypothesis, independent sample expansion or proof of the remaining nonlinear mechanisms. The full pair list and provenance are bundled in `source_data/`. The manuscript now contains the same statement.

## Remaining form action

The actual form requires confirmation that **all listed authors have reviewed and approved this submission**. That fact has not been confirmed, so the checkbox has not been checked. The pasted form does not show a separate presenting-author field; a presenter is not invented as an additional current-form requirement. Conference attendance and registration arrangements remain a later matter under the conference rules.

No portal login, author-table mutation, upload, email, registration, payment or submission has been performed by this preparation step. There is no submission ID or receipt.
