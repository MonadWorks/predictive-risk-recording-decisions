# ICBR 2026 — reviewable abstract draft

Prepared 17 October 2026 (Asia/Shanghai). **Not submitted.** The abstract body below contains no references, figures or author metadata. Author markers and all review notes are outside the text to paste into CMT.

## Title

Predictive Risk and Recording Decisions in Partially Observed Neural Networks

## Authors and affiliations

Jiayi Du¹*†, Shuaizhi Cheng²†

¹ Stiftung Louisenlund, Germany  
² Department of Computing, Harbin Institute of Technology, China

† These authors contributed equally to this work.  
* Correspondence: Jiayi Du, jiayi.du@mail.louisenlund.de  
Shuaizhi Cheng: szcheng@stu.hit.edu.cn

Names, affiliation wording, order, equal-contribution designation, emails and countries reproduce the user-supplied information. Do not put footnote markers into CMT given/family-name fields.

## Abstract body — paste only this section

Neural interfaces in biohybrid systems motivate selecting recordings for specified stimulus responses. Known connectivity does not determine neuronal gains or biases, and limited measurements can constrain different predictions unequally. Goal-oriented experimental design addresses this problem through predictive risk. However, a more extensive approximation to risk need not change the selected observations or improve the response predicted from them. We examined these distinct outcomes in controlled computational experiments.

In simulated 12-unit neural networks with known connectivity and uncertain gains and biases, we crossed single-response and three-response objectives with local-risk criteria evaluated at a nominal parameter or averaged over a common prior ensemble. The target was the time-integrated difference between stimulated and unstimulated activity. Methods shared the available model information, feasible recording pool, measurement budget and Gaussian maximum a posteriori estimator. Recording decisions used no generating parameters or evaluation outcomes. A frozen primary evaluation included 40 independent networks, with physiological truths, measurement-noise repetitions and readouts nested within each network. Its primary condition used broad matched uncertainty, three recorded nodes and exclusion of stimulation and readout sites.

Neither prediction objective established a consistent ensemble advantage. Relative changes in aggregate mean squared response error were -3.74% for the single-response objective (97.5% paired network-cluster interval, -18.48% to 12.12%) and +2.69% for the three-response objective (-2.95% to 11.51%). These uncertain comparisons do not establish method equivalence. A separately specified follow-up used 40 new networks and held recordings, data and point predictions fixed while comparing the risk forecasts. Its primary ensemble-minus-nominal forecast-score difference was -0.45565 (95% interval, -1.15857 to 0.02367), also uncertain. An exploratory extension to eight independent 100-unit rank-two networks showed effects that varied with objective and recording budget. Linear-Gaussian controls verified risk-to-prediction agreement where analytically expected; nonlinear approximation diagnostics and selection overlap constrained interpretation without identifying a unique cause.

These results distinguish forecasting prediction error from improving the recording decision made using that forecast. More extensive prior averaging should therefore be evaluated through both its risk forecasts and the actual response estimates obtained under the same task and information budget. The study provides computational evidence about existing design criteria; translation to living neural interfaces and mechanical biohybrid outputs remains untested.

---

## Review notes — not part of the abstract

**Length checks.** Body: 355 whitespace-delimited words; 384 under a conservative punctuation-splitting check. It has 2,822 Unicode characters including spaces and LF paragraph breaks (2,828 if converted to CRLF). Title: 10 words. Keywords: 5 items, 94 characters including separators. Both word-count checks satisfy the user-provided live-form limit of 500 words; character counts are well below 5,000. CMT's own counter remains the final check.

**Keywords — semicolon separated:**

biohybrid robotics; neural interfaces; goal-oriented design; sensor selection; predictive risk

**Topic recommendation:** primary c, Modeling, actuation, sensing, and control of biohybrid robots; secondary d, Data fusion and intelligence of biohybrid robots. These are recommendations to select in the actual form, not claims that the work validates a robot.

**Sentence responsibilities:**

| Sentence(s) | Responsibility |
|---|---|
| 1–2 | Establish the interface motivation and why known connectivity does not remove uncertainty about the response. |
| 3–5 | Identify the existing risk criterion and distinguish a better approximation from a better recording decision. |
| 6–8 | Define the crossed factors, response quantity and shared inference/information conditions. |
| 9–11 | State prospective selection and the independent sampling unit, primary pool and budget. |
| 12–14 | Preserve both uncertain primary comparisons, quantitative relative effects and non-equivalence limitation. |
| 15–16 | Explain the independent forecast study and report its own uncertain primary result without replacing the first study. |
| 17–18 | Identify the exploratory larger family and numerical/approximation controls, without turning them into a general improvement claim. |
| 19–21 | Give the implication for task-matched evaluation and the boundary at living/functional validation. |

The table follows the prose's intended sentence grouping; decimal numbers in the results should not be used as sentence delimiters in an automated parser.

**CMT fields ready to review:**

- Title, abstract and semicolon-separated keywords: ready above and in separate machine-readable files.
- Author 1: given Jiayi; family Du; affiliation Stiftung Louisenlund; country Germany; email jiayi.du@mail.louisenlund.de; corresponding author.
- Author 2: given Shuaizhi; family Cheng; affiliation Department of Computing, Harbin Institute of Technology; country China; email szcheng@stu.hit.edu.cn.
- Equal contribution: both authors. The actual field for this note has not been confirmed; do not silently alter name strings to encode it.
- Funding Information: **None**, explicitly confirmed by the user; 4 characters, within 500.
- Conflicts of Interest: **None**, explicitly confirmed by the user; 4 characters, within 3,000.
- Presenting Author: **not yet specified**. Corresponding author does not automatically identify the presenter.
- Coauthor agreement checkbox: **not confirmed and not checked**. Authors should review the concrete draft before confirming.
- Graphical abstract: required; live form permits PDF/PNG/JPG/JPEG, maximum 10 MB. No GA is created or uploaded by this drafting subtask.
- Full paper: not requested.

**Evidence check.** The two primary percentage effects and intervals were verified against `holdout_paired_effects.csv`; the independent forecast score was verified against `forecast_summary.json`. The study sizes and family description agree with the manuscript. This document introduces no new analyses or results. `abstract_audit.json` retains the exact source values, counts and hashes.

**Remaining boundaries.** Submission-format compliance is separate from acceptance. The result remains simulation only, the main comparisons uncertain, the 100-unit family exploratory, and biological/mechanical validity untested. Portal preview, presenter choice, author agreement and graphical-abstract attachment remain for the authorized submission workflow. No login, email, registration, payment or submission was performed here.
