# Provenance and revision log — paper_v4_pastel

Frozen source of truth: `../../work/evidence/ICBR2026_v4_pack` (never overwritten).
Previous deliverable: `../pink_figure_suite` (kept for reference, unchanged).

## Revision 2026-10-18b (this pass)

Requested by the author after the first pastel PDF read-through.

1. **Page layout.** sn-jnl defaults to `twoside` plus `bindingoffset`, so odd and
   even pages carried mirrored margins. The build now passes `oneside`
   (`06_latex/biomed/Makefile`, `CLSOPT`); with `bindingoffset=0mm` in
   `main.tex` the text block is centred identically on every page.
2. **Manuscript note removed from the title page.** The sentence below was
   typeset with `\noindent{\footnotesize\textit{\PaperManuscriptNote}}` right
   after `\maketitle`; it is recorded here instead of in the paper.
   > Research manuscript v4, 17 October 2026. All data are simulated. v4 changes
   > the organisation, framing and figures; every number is a frozen v2 estimate
   > or a count taken from the frozen records.

   (`\PaperManuscriptNote` is still generated from the manuscript front matter
   in `build/meta.tex`; only its printed line in `main.tex` was dropped.)

## Figure palette revision (same pass)

Amber used for forecast/realised/error encodings was brightened to a sunflower
petal tone. The family is now:

| role | value | use |
| --- | --- | --- |
| `FORECAST` | `#EDAF26` | filled areas: bars, markers, stimulus bands, rings |
| `FORECAST_LINE` | `#DB9A1D` | thin strokes: stimulus step, response curve, thin outlines |
| `VECTOR5` | `#E8A13C` | fig 5 three-response series (single warm hue family, no pink/amber mixing) |

Per-figure adjustments:

- **fig 4 panel a** — nominal risk markers now open grey (`MUTED #7D7280`) and
  ensemble markers filled bright amber, replacing the two-amber pairing.
- **fig 4 panels b/c** — mean-score annotations moved up under panel b; panel c
  heading given more clearance from its value line; `Ensemble $-$ nominal score`
  uses the typeset minus so the spacing reads correctly.
- **fig 5** — panel letters share the same gutter as the titles; the footnote is
  left-aligned to the canvas margin; the three-response series is monochrome
  orange (no amber edge on pink markers); right-hand interval values are set in
  JuliaMono.
- **fig 2 panel c** — brighter stimulus step/band and response curve.


## Formal manuscript cleanup — 2026-10-18

Removed the internal Research manuscript v4/version-freeze front-matter paragraph from the formal Markdown source (previously hidden only in the biomed PDF). Removed 31 invisible paragraph-number comments and the unconfirmed final-author-approval sentence. Scientific simulation and frozen-protocol descriptions remain in Abstract and Methods. The converter now leaves PaperManuscriptNote empty, and the IEEE wrapper no longer prints it. This prevents internal revision notes from reappearing in another template. Historical originals remain unchanged.
