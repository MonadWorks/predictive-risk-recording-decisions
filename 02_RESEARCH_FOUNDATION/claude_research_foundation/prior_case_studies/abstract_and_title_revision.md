# Abstract and title: targeted revision rather than inflated claims

17 October 2026. The user identified an unspecified causal disclaimer and a generic significance paragraph. Both were removed. This pass changes the argument's precision and sentence flow, not the frozen comparisons or their interpretation.

## Primary guidance actually checked

| Source | Access depth | Applied decision |
|---|---|---|
| [Nature's annotated summary paragraph](https://www.nature.com/documents/nature-summary-paragraph.pdf), September 2019 | Complete one-page PDF, including the Eg5 example and annotation. | Establish the question before reporting results; end with an answer connected to those results. Its paragraph length and positive discovery example are not ICBR requirements. |
| [ICMJE, Preparing a Manuscript for Submission](https://www.icmje.org/recommendations/browse/manuscript-preparation/preparing-for-submission.html), abstract and statistics sections | Full public guidance; relevant sections read. | Keep effect sizes and uncertainty, distinguish planned and exploratory evidence, and match the abstract to the article. Do not import clinical structured headings, clinical significance or trial-registration obligations into this simulation abstract. |
| [Mensh and Kording, 2017](https://doi.org/10.1371/journal.pcbi.1005619), rule 5 | Open full text; abstract section checked. | Present a complete question–comparison–result–interpretation sequence. A broad final claim is optional; no compulsory innovation claim is inferred. |
| [Beiran and Litwin-Kumar, 2025](https://doi.org/10.1038/s41593-025-02080-4) | Publisher abstract and figure headings; main text paywalled in this check. | The abstract moves from an explicit physiological ambiguity to a concrete finding and its conditions. Our text uses that level of specificity, without copying its phrasing or borrowing its theoretical contribution. |
| [Lappalainen et al., 2024](https://doi.org/10.1038/s41586-024-07939-3) | Open main text, including model constraints and validation sections; full-text case notes elsewhere in this package. | State which constraints are known, which prediction is evaluated and what validation is actually available. Its living-system validation cannot stand in for ours. |
| [Nature Computational Science, 2025](https://doi.org/10.1038/s43588-025-00835-4) and [Nature Human Behaviour, 2023](https://doi.org/10.1038/s41562-023-01596-8) editorials | Publisher previews only; no full-text advice inferred. | Retained as reading leads, not treated as fully reviewed rules. |

These are craft sources, not additional scientific references in the article. The principles are independently expressed here; no source paragraphs or figures are reproduced.

## Concrete changes in this abstract

- The opening now identifies a measurement-and-prediction problem in neural interfaces, then states exactly which risk approximation is compared.
- The methods retain the crossed objectives, known/unknown quantities, common inference, independent unit and primary recording constraints. Execution safeguards and routine numerical checks remain in the article.
- The results keep both primary percentage effects and their 97.5% intervals, and the independent forecast score with its 95% interval. They neither equate the methods nor promote a secondary result.
- The risk score is defined, rather than leaving the reader with an unexplained score difference.
- A descriptive readback of the frozen recording sets supplies a specific link: 82/120 scalar target-specific sets (three per network) and 26/40 shared sets coincide. These are design counts nested in 40 networks, not 160 independent samples. Provenance and all design pairs are bundled in `source_data/`.
- The ending describes the unchanged-data/unchanged-estimator relationship and the conditional extension result. It does not claim that the cause of every between-method difference has been identified.
- The title now names stimulus-response estimation. Alternatives and trade-offs are kept in `submission/title_options.md`.

This is an improvement in specificity, not a claim that the study has become a mechanistic theory. The stronger nonlinear 'why' question remains the one documented in the article's Discussion and the separate evidence-boundary note.
