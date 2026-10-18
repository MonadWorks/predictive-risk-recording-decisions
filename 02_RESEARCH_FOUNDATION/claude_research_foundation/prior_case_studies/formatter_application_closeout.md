# Plot-formatting workflow: application closeout

2026-10-17. This note records what was adopted, implemented and left outside scope. It does not certify research quality or journal compliance.

## Source and access

Source: [preordinary/science-plot-formatter](https://github.com/preordinary/science-plot-formatter), commit `750c6c1834c833c2607e5913daea76497433dc6e` (2026-05-27). The local [source audit](science_plot_formatter_audit.md) records README, skill and agent-instruction inspection. GitHub REST snapshot at 2026-10-16 23:42:26.993 Beijing returned 8 stars; an older web cache showed 7. This small popularity count is provenance, not quality evidence. The inspected tree supplied a skill workflow, with no executable formatter CLI, Python installation package or dependency manifest. API license was null and no explicit LICENSE/COPYING was found; license remains unknown.

No third-party formatter CLI was run and no upstream skill was installed. The project independently implemented relevant finishing actions in local Matplotlib code, without redistributing the upstream text as a licensed tool.

## Applied sequence and evidence

1. **Design the comparison first.** Fig. 1 now uses fixed J5000 source arrays and actual simulated observations. Fig. 2a/b expose nominal-error scale and descriptive log₂(E/N); c retains the raw primary estimand with 97.5% intervals. Fig. 3b retains all 40 score differences; c separately resolves the mean and 95% interval. These are deliberate encoding decisions, not changes attributed to a formatter.
2. **Finish at physical size.** Main plots use the project's provisional 180 mm width; graphical abstract uses 190 mm. These dimensions are not official venue certification. Styling then addresses glyph support, mathtext, unwanted minor tick labels, stroke weight and size. Current renderer explicitly uses NullLocator/NullFormatter; it does not alter data, score definitions, confidence levels or independent n.
3. **Keep artifacts and claim checks together.** Current [paper and captions](../paper/论文研究稿_v3.md), [Fig. 1 manifest](../figure_redesign/data_overview/manifest.json), [statistical renderer](../scripts/render_figures.py), [figure manifest](../figures/figure_manifest.json), and [graphical-abstract manifest](../submission/graphical_abstract/manifest.json) provide the corresponding contracts. This document checked the current captions, source code and manifest; it does not claim a fresh pixel-by-pixel review of every export or a new statistical rerun.

The actual [graphical-abstract PDF](../submission/graphical_abstract/graphical_abstract.pdf) includes authors and the equal-contribution footer. Current abstract wording and technical counts are maintained separately and may change locally. This note therefore does not freeze their word count.

## Removed branch and remaining limits

Rejected AI image candidates are in workspace `work/editorial_v3/rejected_imagegen/`; they do not enter delivered figures. Historical concept and baseline exports remain distinguishable from the current manuscript Fig. 1. No image generation remains planned for this delivery.

The main comparisons remain uncertain, the extension exploratory, and every model simulated. Better encoding improves access to that evidence; it does not create a new method, establish biological validity, resolve approximation mechanisms or demonstrate a stable ensemble advantage. Final submission and author approvals are separate from document formatting and are not asserted here.
