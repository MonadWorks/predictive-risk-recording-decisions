# Figure decisions before styling

## Start with the question and the independent unit

| Reader needs to judge | Useful form | Essential condition | Common misuse |
|---|---|---|---|
| Two methods on the same systems | Paired scatter with identity line; paired differences | Point is the independent system's prescribed mean | Plot every repeated time point as a new independent subject |
| A population mean contrast | Effect estimate plus confidence interval | Defined estimand, pairing and interval level | Treat overlapping marginal error bars as the comparison test |
| Spread and tails | Individual points or ECDF | Retain all instances; state dependence | Violin density from n=8 suggests unsupported smooth structure |
| A risk forecast versus actual error | Same-unit scatter with identity line plus an appropriate predeclared score | Keep point prediction fixed if studying forecasts | Correlation or one favourable aggregate ratio is called calibration |
| A factorial method comparison | Row/column layout or redundant encodings | Each encoding has a fixed meaning | Four unrelated colours conceal two underlying factors |
| Many conditions | Ordered small multiples or supplements | Comparable scales and explicit conditions | Independent autoscaling creates apparent similarity or hides magnitude |

For this study, the primary paired scatter uses one MSE per J. Both axes share the same log range; no data values are logged before computing the scientific estimand. The primary forest reads the already-computed raw mean-MSE difference and its paired bootstrap interval, with a labelled display scale of 10⁻⁵. Relative mean-MSE changes remain in the table; those are ratios of aggregate means, not means of per-network ratios. The underlying studies and statistics remain frozen.

## An internally consistent visual grammar

The current project uses blue `#0072B2` for a single-response objective and vermilion `#D55E00` for the three-response objective. Nominal and ensemble methods have open and filled markers where each point represents one method. In a local-versus-ensemble paired scatter, a point represents both methods; its colour indicates the objective, and axes indicate the approximation. A contrast marker represents an effect, not a new method. Activity/random references are grey.

The independent forecast study holds the single-response recording policy fixed. Nominal/ensemble forecasts therefore use the same blue with open/filled markers and a shared actual-MSE coordinate. This does not turn blue into an ensemble-only label. Colour alone is never the only identifier.

Other projects may prefer approximation colours with objective shapes. Pick a scheme based on the argument; do not mechanically reuse this project's colour semantics.

## Physical size is part of the information design

Our v2 raw-risk overview was approximately 404 mm wide after export. Scaling it to 180 mm reduces a nominal 9 pt label to about 4 pt. Higher DPI cannot repair this. The revised manuscript figures are authored at 180 mm with about 8–9 pt text at that size, while the complete condition grid is split across supplementary figures. This is a project choice, not a universal journal rule.

Save the final-size PDF without automatic tight cropping that changes its media box. Use adequate margins and inspect the exported PDF. Provide PNG previews, but do not rely on a zoomed-in monitor view. Keep short panel titles inside; put the full title, conditions, n, aggregation and interval in the caption.

## Concrete references

- [Wilke, multi-panel figures](https://clauswilke.com/dataviz/multi-panel-figures.html), full chapter and examples read. The degree-trend example changes interpretation when axes are rescaled; the athlete example shows inconsistent colour/order across panels. We adopt shared scales, meaningful panel order and stable encodings, not its data or artwork.
- [Wilke, titles, captions and tables](https://clauswilke.com/dataviz/figure-titles-captions.html), full chapter read. The paired display/infographic examples distinguish article captions from integrated headline graphics. We remove long figure-internal headings, keep axis units and use restrained tables. This is craft advice; a venue's current instructions take precedence.
- [Wilke, uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html), chapter consulted for matching visual summaries to uncertainty. Point spread, uncertainty about a mean and a predictive interval describe different quantities. We retain the frozen cluster interval instead of swapping in a prettier marginal error bar.

Additional journal/editor, statistical and GitHub cases are documented in the accompanying `case_studies/figure_research.md`. Repository styles may improve defaults, but cannot choose an estimand or make a misleading chart sound.

## Preflight that is useful, and its limit

Check exported dimensions, embedded fonts, text bounds, point counts, source-data hashes, the zero/identity line, complete interval ranges, stable factor encoding and caption agreement. Inspect every figure. A script can detect changed values or text outside a page; it cannot establish that the research is worth publishing or that the design is aesthetically optimal.
