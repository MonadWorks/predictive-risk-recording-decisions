# Literature gap plan (refs 26-39), 2026-10-18

Verification: all 14 DOIs were resolved against the Crossref REST API (title, authors, journal, volume/issue/pages, date). Publisher full texts were not read; "what it supports" is based on titles, abstracts and general knowledge of each paper, and is flagged where weaker. Bib entries: `05_data_and_code/references_extra.bib` (keys ref26-ref39). `paper_v4.md` and `references.bib` are unchanged. Numbers continue the paper's list (1-25).

Two search results are honest negatives: no landmark paper on model-based (Fisher-information or risk-based) recording-neuron selection in BMIs was found beyond Beiran and Litwin-Kumar [5] and Krause et al. [25]; ref30 is EEG data-driven channel selection and ref31 is hardware. The paper should not claim that this literature is covered.

## Entries

### [26] Ricotti et al. 2017
Ricotti L, Trimmer B, Feinberg AW, Raman R, Parker KK, Bashir R, Sitti M, Martel S, Dario P, Menciassi A. Biohybrid actuators for robotics: A review of devices actuated by living cells. Sci Robot 2(12):eaaq0495 (2017). doi:10.1126/scirobotics.aaq0495
- Supports: biohybrid actuation is an established field with reviews.
- Location: I1, after "[1,2]".
- Sentence: "Biohybrid robots translate optical inputs into motion through directly stimulated muscle or an intervening neuromuscular interface [1,2] (reviewed in [26])."

### [27] Aydin et al. 2019
Aydin O, Zhang X, Nuethong S, Pagan-Diaz GJ, Bashir R, Gazzola M, Saif MTA. Neuromuscular actuation of biohybrid motile bots. PNAS 116(40):19841-19847 (2019). doi:10.1073/pnas.1907051116
- Supports: a neuron-muscle coupling as a route to actuation, earlier than [2].
- Location: I1 (same sentence) and D4 (last sentence).
- Sentence (I1): "Earlier neuromuscular biohybrid bots coupled cultured neurons to muscle tissue [27]."  
- Sentence (D4): "...would require a further neuromuscular validation layer, as illustrated by current biohybrid crawlers [2,27]."

### [28] DeMarse et al. 2001
DeMarse TB, Wagenaar DA, Blau AW, Potter SM. The neurally controlled animat: biological brains acting with simulated bodies. Auton Robots 11(3):305-310 (2001). doi:10.1023/A:1012407611130
- Supports: cultured networks recorded and stimulated through a limited electrode array in closed loop with a (simulated) body.
- Location: I1, after "patterned electrical inputs [3]".
- Sentence: "Closed-loop use of cultured networks through a small set of electrodes has a longer history [28]."

### [29] Gutenkunst et al. 2007
Gutenkunst RN, Waterfall JJ, Casey FP, Brown KS, Myers CR, Sethna JP. Universally sloppy parameter sensitivities in systems biology models. PLoS Comput Biol 3(10):e189 (2007). doi:10.1371/journal.pcbi.0030189
- Supports: parameters of biological models are often poorly constrained individually while some predictions remain constrained; ties to [4] and [13].
- Location: I2, after "Different circuit parameters can produce similar activity [4]"; also D4 next to [13].
- Sentence (I2): "Models in systems biology show a related pattern, in which many parameter combinations are weakly constrained by data although some predictions remain well constrained [29]."
- Sentence (D4, after [13]): "...can expose model discrepancy [13], and weakly constrained parameter directions are common in biological models [29];"

### [30] Lal et al. 2004
Lal TN, Schroder M, Hinterberger T, Weston J, Bogdan M, Birbaumer N, Scholkopf B. Support vector channel selection in BCI. IEEE Trans Biomed Eng 51(6):1003-1010 (2004). doi:10.1109/TBME.2004.827827
- Supports: channel selection is an established BCI problem, typically solved with data-driven classifiers (EEG, not intracortical).
- Location: I3, start of the paragraph's sensor-selection sentence.
- Sentence: "Channel selection is an established problem in brain-computer interfaces, usually posed as choosing channels that maximise decoding performance on recorded data [30], whereas here the choice is made before recording from a model."

### [31] Jun et al. 2017
Jun JJ, Steinmetz NA, Siegle JH, Denman DJ, ... Harris TD. Fully integrated silicon probes for high-density recording of neural activity. Nature 551(7679):232-236 (2017). doi:10.1038/nature24636
- Supports: modern probes offer many recording sites but only a subset of channels is recorded at a time, so site selection remains a practical decision. Channel/site numbers are from general knowledge, not re-read.
- Location: I1 or I3 (practical motivation for "few recording channels").
- Sentence: "Even high-density probes expose many more sites than can be read out at once, so a choice of recorded sites is still required [31]; biohybrid preparations may be more restricted."
- Note: hedge the last clause; no evidence collected for biohybrid channel counts.

### [32] Lewi, Butera, Paninski 2009
Lewi J, Butera R, Paninski L. Sequential optimal design of neurophysiology experiments. Neural Comput 21(3):619-687 (2009). doi:10.1162/neco.2008.08-07-594
- Supports: information-theoretic stimulus design for neural system identification.
- Location: I3, last sentence, next to [9].
- Sentence: "...which has its own experimental-design literature [9,32]."

### [33] Gneiting and Katzfuss 2014; [34] Gneiting, Balabdaoui, Raftery 2007; [35] Dawid 1982
Gneiting T, Katzfuss M. Probabilistic forecasting. Annu Rev Stat Appl 1:125-151 (2014). doi:10.1146/annurev-statistics-062713-085831
Gneiting T, Balabdaoui F, Raftery AE. Probabilistic forecasts, calibration and sharpness. J R Stat Soc B 69(2):243-268 (2007). doi:10.1111/j.1467-9868.2007.00587.x
Dawid AP. The well-calibrated Bayesian. J Am Stat Assoc 77(379):605-610 (1982). doi:10.1080/01621459.1982.10477856
- Support: forecasts are judged by proper scores and by calibration; forecasting evaluation is separate from point prediction.
- Locations and sentences:
  - I4 or I6 (where Box 1 and the score are first mentioned): "Forecast quality is assessed with proper scoring rules and by calibration [14,33,34]; calibration of forecasts has long been treated separately from the accuracy of the point prediction [35]."
  - Methods, "Separately specified risk-forecast follow-up", after "This is a use of established scoring principles [14]": "...established scoring principles [14], and the forecast-evaluation literature [33,34] distinguishes calibration from sharpness; the nominal-versus-ensemble comparison here mixes both and does not test calibration separately."
  - Table 2, hidden-bias row (the sentence "the score gain may reflect larger forecast variance rather than calibration") could cite [34] for the calibration/sharpness distinction.
- Caveat: the paper's score is for a mean-squared-error forecast (a scalar mean functional), not a full predictive distribution; [33,34] discuss distributional forecasts. State this when citing.

### [36] Amrhein, Greenland, McShane 2019; [37] Altman and Bland 1995
Amrhein V, Greenland S, McShane B. Scientists rise up against statistical significance. Nature 567(7748):305-307 (2019). doi:10.1038/d41586-019-00857-9 (Comment article)
Altman DG, Bland JM. Statistics notes: absence of evidence is not evidence of absence. BMJ 311(7003):485 (1995). doi:10.1136/bmj.311.7003.485
- Support: do not infer "no effect" from p>0.05 or an interval containing zero; read intervals as the range of compatible effects.
- Location: D1b, first sentence; and Methods "Estimands and uncertainty", last sentence.
- Sentence (D1b): "A non-significant interval is more informative when read as an approximate bound than as a verdict [36,37]."
- Sentence (Methods): "We do not infer equivalence from an interval crossing zero [36,37]."

### [38] Efron 1979; [39] Field and Welsh 2007
Efron B. Bootstrap methods: another look at the jackknife. Ann Stat 7(1):1-26 (1979). doi:10.1214/aos/1176344552
Field CA, Welsh AH. Bootstrapping clustered data. J R Stat Soc B 69(3):369-390 (2007). doi:10.1111/j.1467-9868.2007.00593.x
- Support: the bootstrap and cluster resampling for clustered data.
- Location: Methods "Estimands and uncertainty", sentence on the paired network-cluster percentile bootstrap; D1b for the caveat on heavy tails.
- Sentence (Methods): "Paired network-cluster percentile bootstrap [38,39] uses 10,000 resamples, resampling whole networks so repeated targets and noises do not count as independent."
- Note: [39] studies cluster bootstrap properties; the paired difference version here is an application, not a result from that paper.

## Remaining uncited claims

| Quoted claim (location) | Found support? |
|---|---|
| "Under a limited recording budget, these tasks can assign different values to the same observation." (I1) | Partly: [10,18,24] on goal-oriented design are conceptually relevant; no direct neural source found. Could cite [10]. |
| "Biohybrid neural interfaces typically have few recording channels" (Abstract, first sentence) | No reference found; [3,28] use multi-electrode arrays but do not establish "few". Rephrase as "can have" or cite a specific platform. |
| "greedy selection with guarantees for suitable objectives [25]" (I3) | Supported by [25] (submodularity). Applicability to the paper's risk objective is not shown; hedge. |
| "averaging local criteria over a parameter ensemble accounts for variation in sensitivities [21]" (I4) | [21] is a related method, not a demonstration for this claim; hedge as "in related designs". |
| "heavy-tailed data ... percentile bootstrap intervals are not sharp" (D1b) | General bootstrap theory; [38,39] give only background. No source found for the specific small-sample-with-zeros claim. |
| "the winner's curse" (F3: observed effects likely overestimated) | Not searched; well known (e.g. Ioannidis 2008 Epidemiology) but not verified, not added. |
| "13 and 26 of the 40 ... exactly zero" and all numerical results | Own data; no citation needed. |
| "a design specialised for one known readout can outperform a shared design through task specialisation alone" (I4) | No source found; is an expectation tested by the study. Hedge. |

Considered and not added: Marder and Taylor 2011 (Nat Neurosci 14:133, doi:10.1038/nn.2735, exists in Crossref) and Transtrum et al. 2015 (J Chem Phys 143:010901) for the sloppiness theme; cap of 14 reached.
