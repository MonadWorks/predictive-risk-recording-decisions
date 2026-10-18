# Figure redesign: current design and delivery contract

Updated 2026-10-17. The design pass changes the visual encoding before final styling; frozen data, independent units, estimands and intervals are preserved. Main-figure width 180 mm and graphical-abstract width 190 mm are project choices, not certified venue requirements.

## Scientific object and final figure roles

The object is a partially observed synthetic neural network and its specified response. The current manuscript Fig. 1 is [a fixed first-network overview](data_overview/fig1_data_overview.pdf), not a conceptual robot or invented biological apparatus. It displays J5000 signed connectivity, actual noisy calibration observations at N6/N8/N11, and held-out N4 stimulus-minus-control activity. Trials reset to the same known initial state and are not connected across the display boundary. The response integral retains the original step-weighted definition. This n=1 instance is fixed by first index, not selected for a favourable effect; it establishes no method ranking or biological validation.

Fig. 2a/b display nominal MSE on a shared logarithmic horizontal scale against descriptive within-network log₂(E/N), with zero denoting equal error. Panel c separately displays the primary raw mean-MSE difference and its 97.5% paired network-cluster interval. Individual ratios are neither the primary estimand nor the ratio of aggregate means. Every network, tie and influential instance is retained.

Fig. 3a pairs two risk forecasts with the same actual prediction error. Panel b shows all 40 network score differences, including the tail; panel c displays their mean and prespecified 95% paired interval on its own labelled scale. Individual variation and uncertainty about the mean cannot share an axis merely to save space. Scores are computed per case and aggregated within J, not calculated from panel-a aggregate coordinates.

Fig. 4 retains all eight exploratory settings and pointwise intervals. The model family changes along with N; it is not an N-only scaling claim. Supplementary figures preserve complete distributions and secondary strata. The [actual graphical abstract](../submission/graphical_abstract/graphical_abstract.pdf) is a separate deterministic artifact with authors and an equal-contribution footer; it complements the manuscript without replacing its evidence.

## Workflow adoption and execution identity

Inspected canvas-design, scientific-schematics, scientific-visualization and PaperBanana materials informed hierarchy, source-backed components, planning and critique. Their aesthetic or external-runtime suggestions are not blanket manuscript requirements. No upstream PaperBanana runtime or third-party formatter CLI was installed or executed.

The science-plot-formatter workflow is adopted as a bounded finishing process: choose physical size, inspect exports, apply local style changes, and compare before/after. Its audited snapshot had 8 stars and pinned commit `750c6c1834c833c2607e5913daea76497433dc6e`; no explicit license was found. It is a skill workflow, not an executable formatter package. Provenance and limits are documented in [the closeout](../case_studies/formatter_application_closeout.md).

Encoding changes belong to the design stage. Final styling is limited to supported glyphs, mathtext, minor-tick handling, strokes and physical dimensions. Local Matplotlib code uses NullLocator/NullFormatter to suppress unwanted minor labels; a preset cannot choose statistical units or repair a misleading estimand.

## Rejected branch and retained history

Early AI-generated concept candidates were rejected and moved to workspace `work/editorial_v3/rejected_imagegen/`. Generated images do not enter this delivery; there is no continuing image-generation plan. The old `figures/fig1_study_design.*` exports and `figure_redesign/baseline/` are historical references, not the current manuscript Fig. 1. No generated data marks, traces, numbers or confidence intervals replace numerical sources.

Manuscript changes remain local. Abstract wording and counts are maintained in the submission directory rather than frozen in this design brief. This closeout does not claim scientific novelty, biological validation, venue approval or submission completion.
