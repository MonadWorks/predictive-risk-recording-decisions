# From evidence to a readable scientific argument

These are conditional craft decisions, distilled for computational/biomedical research. They do not establish the merit of a new scientific claim.

## A citation has a specific role before it enters a sentence

For the present neural-recording study, three lines meet at one testable question. This is a project-specific worked example, not a mandatory citation list for other studies:

| Line | Closest anchor | What it supplies | What remains to evaluate here |
|---|---|---|---|
| Connectome-constrained inference | Beiran & Litwin-Kumar 2025, doi:10.1038/s41593-025-02080-4 | Known J, uncertain neuronal properties, partial recordings and existing recording selection | How two risk approximations perform for a specified response under a common information contract |
| Purpose-matched model validation | Sourmpis et al. 2026, doi:10.7554/eLife.106827.3; Lappalainen et al. 2024, doi:10.1038/s41586-024-07939-3 | Predictions must be evaluated for their intended use; structural constraints and biological comparisons have distinct roles | Test simulated stimulus responses separately from calibration activity; biological evidence is still absent |
| Goal-oriented experimental design | Attia et al. 2018, doi:10.1088/1361-6420/aad210; Zhong et al. 2026, doi:10.1137/24M1649344 | Existing goal-dependent criteria and nonlinear alternatives | Separate task specialisation, local-risk approximation, forecast accuracy and changed recording decisions |

The last column is a study question, not a verified claim of an unprecedented gap. Avoid turning “we have not found it” into “no previous work has done it”.

## Paragraphs should change what the reader knows

A useful paragraph usually has a question, evidence and an inference. The inference should make the next question feel necessary. Sometimes this fits three sentences; a complicated result may need two paragraphs. Forced transition words do not repair missing logic.

In a Results paragraph, favour the sequence **why this comparison → what was held fixed → effect and interval → what follows**. Move solver minutiae to Methods unless they are the result under discussion. Treat a follow-up as a new question with its own evidence, not as the inevitable confirmation of an exploratory pattern.

In a Discussion paragraph, connect an interpretation to its actual support and strongest alternative. State a limitation where it changes inference; avoid repeating a disclaimer after every result. A careful paper can speak directly without repeatedly announcing that it is careful.

### Examples from our earlier draft

Earlier: “We inherit that evaluation principle rather than claim it as a discovery.”

Better for the manuscript: “We therefore evaluate the stimulus response independently of the activity used for fitting.” The citation should explain the evaluation lineage in the preceding sentence. Novelty accounting belongs in positioning, not repetitive self-commentary.

Earlier: “Neither incomplete recordings nor the selection of informative neurons is an unexplored idea.”

Better: “Beiran and Litwin-Kumar showed how partial recordings and recording-site selection constrain activity predictions when connectivity is fixed.” This states the prior answer precisely and leaves room to state our different evaluation question.

Earlier: “Their final numerical summaries are inserted only after complete execution and analysis.”

For a completed study, report the result and its uncertainty. Workflow status belongs in project records, not Results. A working manuscript should read as an argument, not an execution diary.

## Craft references and transfer limits

- [Mensh & Kording, 2017, PLOS Computational Biology](https://doi.org/10.1371/journal.pcbi.1005619), full editorial read: plan the chain of conclusions and give each paragraph an argumentative function. Useful for outline and Results order; not proof that every paper needs identical sections.
- [Simon Peyton Jones, researcher-hosted writing talk](https://simon.peytonjones.org/great-research-paper/), official 48-slide [PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2015/02/simon-peyton-jones_paper.pdf) read: replace a generic field opening with a concrete problem; make contributions answerable by evidence. His preferred placement of Related Work and one-page introduction comes from CS conference writing and is not imposed on biomedical articles.
- [Gopen & Swan, author index of the 1990 article](https://georgegopen.com/scientific-writing-articles/), author description and university-hosted reproduction consulted: place familiar context where readers can use it and make the action legible in the verb. These are editing heuristics; do not mechanically move every result to the last word or ban passive voice.
- [Altman & Bland, BMJ 1995](https://doi.org/10.1136/bmj.311.7003.485), abstract/index consulted: uncertainty crossing a no-effect value does not establish equivalence. Our actual interval widths should guide the wording; the phrase “negative result” alone is insufficient.

The cross-field primary-paper cases are stored separately in `case_studies/` of the accompanying project package. They teach evidence organisation and calibrated expression; they are not extra biological evidence for the neural simulation.
