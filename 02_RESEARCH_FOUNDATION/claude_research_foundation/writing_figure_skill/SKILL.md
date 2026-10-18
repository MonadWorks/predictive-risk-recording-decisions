---
name: research-writing-figures
description: Craft evidence-led scientific manuscripts and statistical figures from a defined study, using closely related papers, explicit citation roles and figure source data. Use for substantive research writing or figure redesign, not routine copy-editing or generating research claims from incomplete evidence.
---

Connect the scientific question, literature, estimand and evidence before polishing prose. A persuasive presentation must preserve uncertainty and the study's actual contribution.

## Build the argument

Read the current study contract and outputs. Identify the exact decision/problem, independent unit, evaluation target and claim supported by the results. Keep presentation edits separate from changes to methods, estimands or analysis.

If only a summary is available, write what it supports and mark the missing methods/provenance needed for verification. Do not invent details or block useful bounded editing merely because the whole study package is unavailable.

Use a few directly related papers to reconstruct the research lineage. Give each citation a job: problem setting, closest existing answer, adopted method, competing explanation, validation standard or limitation. Cross-field papers can inform craft but do not supply missing scientific validation. Keep writing/blog references outside the scientific bibliography unless substantively relevant.

For each paragraph, record its purpose, incoming question, supporting source/result and outgoing inference. Use this map to fix missing reasoning before changing words. See [references/argument-and-prose.md](references/argument-and-prose.md) for examples and [references/working-templates.md](references/working-templates.md) for compact planning tables. The order and number of paragraphs depend on the argument, not a universal template.

## Design figures around estimands

Decide what each panel lets the reader judge. Match the figure to the comparison and dependence structure: paired observations with pairing; mean effects with their intervals; distributions without disguising repeats as independent subjects. Use source data and already-defined statistics. A redesign does not authorize a new test, selected subgroup, changed denominator or removed outlier.

Start at final physical size and check text there. Encode experimental factors consistently rather than assigning every method an unrelated colour. Keep reference lines, intervals and full tails legible. Separate the caption from dense figure-internal prose. Read [references/figure-decisions.md](references/figure-decisions.md) before using a style recipe. `scripts/figure_style.py` offers optional Matplotlib settings; it is not a journal specification or statistics engine.

For generated code, export vector PDF/SVG plus a preview and the data used in each panel. Retain the source-data hashes and transformation definitions. Inspect the rendered output, including final-size readability. A technical preflight may check dimensions/fonts/clipping, but cannot certify visual quality or scientific validity.

## Source quality and reuse

Record access depth: full main text, selected sections, figures/legends, abstract only or search excerpt. Read high-value primary sources before claiming a literature gap. Treat blog advice as a craft heuristic with conditions, and journal instructions as venue-specific requirements. Record provenance and licence for external code/skills before adapting or installing them; a popular repository or impressive README does not establish quality.

## Deliver

Provide a readable manuscript, a separate paragraph/citation map, the figure captions and source data, and a short account of substantive changes and unresolved scientific limits. Preserve earlier scientific records. Do not call a draft publication-ready because formatting checks pass. Do not submit or contact anyone without authorization.
