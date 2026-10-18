# 06_latex/biomed - Springer Nature (Nature Portfolio style) layout

    make                 # -> paper_v4_biomed.pdf  (single column, 22 pp. with the current manuscript)
    make LINENO=1        # add line numbers (class option `lineno`) for review copies
    make REFSTYLE=sn-vancouver-num   # other numeric styles (default sn-nature = [n], order of appearance)
    make NOTES=1         # also print the bib `note` fields (hidden by default, see below)

Needs pdflatex, latexmk, bibtex, pandoc >= 3, python3 (same as `../ieee`). Content comes from
`02_paper/paper_v4.md` through `../common/md2tex.py` (nothing in `common/` or `ieee/` was changed).

## Choice and justification
Preferred option obtained: the **official Springer Nature LaTeX template** (`sn-jnl.cls`, "sn-article"
v3.1, December 2024), the class Springer Nature asks authors to use for Nature Portfolio journals
(Nature Communications, Scientific Reports, Communications Biology ...). Chosen over eLife/PLOS-like
layouts because (i) it is the publisher's own class, (ii) it directly provides the requested
elements (equal-contribution marker `\equalcont`, corresponding author `\author*`, abstract, `lineno`
option, `sn-nature` numeric bibliography style, bold run-in captions below floats), and (iii) the manuscript
is already ordered Results - Discussion - Methods, as Nature journals require.
- Source: https://resource-cms.springernature.com/springer-cms/rest/v1/content/18782940/data/v12
  (Springer Nature "LaTeX template", linked from the author pages), curl-ed 2026-10-18, zip dated 2024-12-13.
- Licence: `sn-jnl.cls` header states the LaTeX Project Public License 1.3c (may be used/modified/
  redistributed under LPPL). Files kept unmodified in `sn-template/`: `sn-jnl.cls`, `sn-nature.bst`,
  `sn-article.tex` (example), `user-manual.pdf`. (The class file has old-Mac CR line endings; TeX reads it fine.)

## What `main.tex` adds on top of the class
- Front matter via `\author*`, `\equalcont`, `\affil`; abstract, manuscript note, Key-points box (tcolorbox).
- Page block widened to 158 x 238 mm (class default 31 pc x 194 mm) so the 7 in wide figures stay legible.
- Captions beneath figures and (class default) above tables; bold run-in labels changed to `Fig. N |` / `Table N |`.
- `fix_floats.py` post-processes the neutral `build/*.tex` (not the source): `figure*`/`table*` become plain
  floats `[!tbp]` (starred floats only reach page tops in one column and left big gaps); uncaptioned data tables
  (notation, design, stage tables) are typeset in place; appendix figures use `[H]`.
- Supplementary figures: section "Supplementary figures", counter `S1..S5`, hyperref anchors `S\arabic`.
- `\Needspace` before sections/subsections to avoid orphan headings; relaxed float fractions.
- Bibliography `../../05_data_and_code/references.bib` (via `build/references.bib`), numeric `sn-nature`,
  no `[?]` (checked in log and PDF text), no missing glyphs (mdcommon.sty).

## Known remaining issues (honest list)
- 5 small Overfull hboxes (<12 pt) inside the Table 2 / Table 3 text cells produced by md2tex's column-width heuristic; not visible.
- Title page uses the class's fixed narrow front-matter block (title/abstract narrower than body); abstract is
  unspaced paragraphs as the class sets it. Key points are on page 2 (SN has no key-points element).
- The bib `note` fields contain internal audit remarks ("Suggested: Introduction I4 ...", "Manuscript entry listed
  no authors ..."). They are suppressed in the typeset list by default (renamed `xnote` in `build/references.bib`
  only); the source .bib is untouched. `make NOTES=1` shows them. They should be cleaned in the source bib before submission.
- Author-contributions section still reads "[Detailed contributions to be completed by the authors.]" (from the Markdown).
- Page 16/17 end: the reference list leaves a mostly empty page before the supplementary figures (intentional `\clearpage`).
- The manuscript Markdown changed while this was built (25 -> 39 references, Box 1/2); the PDF reflects the state at last `make`.
