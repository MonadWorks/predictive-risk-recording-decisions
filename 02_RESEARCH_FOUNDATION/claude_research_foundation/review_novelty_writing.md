# Review: novelty, venue fit, structure, sentences (paper_v4)

## 1. Novelty and significance
**Established:** goal-oriented/Bayesian OED [10,18,24], prior-ensemble averaging of local criteria [21], greedy selection [25], proper scoring [14], connectome-constrained recording selection [5]. The paper itself says so (D2, Conclusions). **New in a modest sense:** (a) the decision-agreement layer, i.e. quantifying that ~2/3 of designs are unchanged and so cannot differ in error; (b) fixing predictions and comparing risk forecasts with log(v)+e²/v; (c) the objective x risk-criterion factorial. These are evaluation-protocol contributions, not method contributions. Significance is a calibrated negative/null result plus a reusable check ("measure how often a costlier criterion changes the design").

**Contribution list (I6):** credible but inflated. Items (iii) is a result, not a contribution; (iv) is an artefact; (v) is a plan. Honest count: two methodological (i, ii) plus one empirical finding (iii). Merge (iv) into reproducibility and drop (v) or call it a "proposed test". Placement is correct (end of Introduction), but a reader of the Abstract never sees the list; the Abstract ends on a results recap rather than the contribution.

## 2. Venue fit
A pure-simulation null result is a stretch for a biohybrid audience; the only link is [1,2] in I1, then nothing until D4/F5. Relevance is real but indirect: biohybrid interfaces have a few recording channels and must predict a response to a fixed stimulus. Suggested framing:
- **Abstract, sentence 1-2:** "Biohybrid neural interfaces typically have few recording channels, so the choice of channels shapes what can be predicted about a planned stimulus. We ask whether a more elaborate channel-selection criterion changes that choice, and whether it improves prediction, in simulated networks."
- **Introduction, end of I1:** "We study this in simulation only; the networks are generic rate models, not a model of any biohybrid platform."
- **Conclusions, last sentence:** "For interface designers, the practical result is a cheap check: count how often a costlier channel-selection criterion changes the channels before adopting it. Whether this holds for living tissue is untested."
Do not describe the result as relevant to robot control; the paper already (correctly) says neural response is not mechanical output.

## 3. Structure: missing items, ranked
1. **Algorithm box for the three-layer audit** (Results opening or Methods head): inputs, steps, outputs, with the decision rule for when each layer is skipped. Highest value; (ii) is the main contribution and currently exists only as prose.
2. **Problem statement** (end of I4/start of Results): one displayed paragraph defining design set M, target q, estimator, risk R, and the three audited quantities. Currently scattered.
3. **Notation table** (Methods): J, theta, eta, b, M, F, H, a_k, R, v, e, S, LS/ES/LV/EV. Notation first appears in Methods but is used in Results.
4. **Practitioner decision flowchart** (Discussion, "Implications"): see section 6.
5. **Related work:** adequate on OED; thin on sensor selection for neural interfaces/BMI channel selection and on biohybrid platforms (3 refs). Add 3-5 sentences in I3, not a new section.
6. **Reproducibility statement:** exists but is buried in Methods/Data availability and references file paths. Add one explicit paragraph: seeds, freeze status ("local, not external preregistration" is good), runtime, versions.
Also: the Contents line and Key points box are journal-style; fine, but Table 3 sits under a heading that does not match its content.

## 4. Ten weakest sentences and rewrites
1. Abstract: "A better risk estimate can improve the prediction only if it changes which neurons are recorded or forecasts the error more accurately." -> "A better risk estimate helps prediction only by changing which neurons are recorded or by forecasting error more accurately."
2. Abstract: "so most recording decisions did not change." -> "so in about two thirds of designs the two criteria recorded the same neurons."
3. Abstract: "The primary comparisons therefore do not establish a stable benefit, while the decision, error and forecast audit shows that an improved criterion can act only in the minority of designs where it changes the recording set." -> "Neither primary comparison showed a benefit. Because the criteria agree in most designs, any benefit can arise only in the minority where they differ."
4. I1: "A recording configuration is useful insofar as it supports the inference for which its measurements are collected." -> "A recording set should be judged by how well the data it yields support the intended prediction."
5. I4: "These distinctions call for comparisons that separate the prediction objective from its uncertainty approximation." -> "We therefore compare criteria that differ in only one of these two choices."
6. I6 (iii): "It reports what these layers show for prior-averaged local risk: usually the same recordings, no stable gain..." -> "We find that prior averaging usually selects the same recordings and shows no clear gain in error or forecast accuracy in the primary condition."
7. R3: "Implementation controls established the expected numerical behaviour before interpreting method differences." -> "Before comparing methods, we checked the code against an independent implementation and a linear-Gaussian case with a known answer."
8. R11: "With only eight independent networks, unadjusted pointwise intervals, and simultaneous changes in model family, dynamics and parameter coordinates, the extension describes conditional behaviour and motivates a confirmatory study; it is neither..." -> "Eight networks, unadjusted intervals and several simultaneous changes (model family, dynamics, parameterisation) mean this extension can only suggest a hypothesis for a confirmatory study."
9. D5: "The absence of a uniformly superior criterion does not remove the need to evaluate both risk forecasts and recording decisions for the specified task." -> "No criterion was uniformly better, so each should be tested on its own task, checking both its forecasts and the recordings it chooses."
10. Conclusions: "The contribution is an audit that separates decision, error and forecast, with numerical controls and open tables, and a specific confirmatory test; it is not a new optimal-design principle..." -> "Our contribution is a three-step audit (decision agreement, response error, forecast accuracy) with open data and a proposed confirmatory test. It is not a new design principle, and it has no biological validation."

## 5. Key points and Abstract versus body
Mostly consistent; numbers match (82/120, 26/40, -3.74%, +2.69%, -0.45565, 19/40, 4 of 8). Problems:
- Abstract omits the outlier dependence of the forecast result (one network ~64% of the sum) and that nominal forecast risk was closer to actual MSE in aggregate; Key points also omit it. This is the most important qualifier for a "forecast" claim; add one clause.
- Abstract says the audit "shows" that an improved criterion can act only in the minority; this follows by construction, not from data. Reword as above.
- Key points "rules out mean-MSE reductions larger than about 3%" is correct for the 97.5% interval but reads as stronger than the text; add "in this simulated setting".
- Abstract spends a full paragraph on the exploratory 100-unit result with five numbers; trim to one sentence to keep exploratory below primary.
- Abstract and Key points are long (Abstract roughly 400 words); Key points repeats Abstract. Cut Key points to four bullets.
- Title is a clear, honest null statement; good.

## 6. At most five additions (no new experiments)
1. **Audit algorithm box** (pseudocode: select under both criteria; compare sets; if equal, error identical; else compare MSE; fix predictions, compare forecast scores).
2. **Practitioner decision flowchart:** compute both criteria on your design pool -> fraction of identical designs? high: keep the cheap one; low: run the error and forecast checks -> report intervals as bounds.
3. **Notation table** in Methods, linked from first use in Results.
4. **One-paragraph problem statement** plus a single schematic (criterion -> recording set -> fit -> prediction -> error / forecast) showing where each audit layer sits; fits as Fig. 1 panel.
5. **Short "What this means for biohybrid interface design" paragraph** in Discussion (3-4 sentences, assumptions stated), replacing the generic last paragraph of F5.
