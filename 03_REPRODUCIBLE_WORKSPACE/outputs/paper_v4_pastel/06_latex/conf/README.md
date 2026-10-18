# 06_latex/conf - ICML-2025-style conference layout

Build: `make` -> `paper_v4_conf.pdf` (needs pdflatex, latexmk, bibtex, pandoc >= 3, python3).
Content comes from `02_paper/paper_v4.md` via `../common/md2tex.py`; `common/` and `ieee/` are untouched.

**This is a layout choice only.** ICBR itself accepts abstracts only; the conference-paper
layout (ICML/ICLR-style, two columns, appendix after references) is an alternative presentation of the same manuscript.

Template: official ICML 2025 style package (https://media.icml.cc/Conferences/ICML2025/Styles/icml2025.zip):
`icml2025.sty`, `icml2025.bst`, `fancyhdr.sty`, `algorithm.sty`, `algorithmic.sty`, `example_paper.tex`
(the zip contains no separate licence/readme file; the licence terms are the headers inside `icml2025.sty`).

Settings in `main.tex`:
- `\usepackage[accepted]{icml2025}`: the non-anonymous "accepted" mode (real author names and affiliations,
  "Appearing in ... ICML 2025" footer). The ICML footer text (Vancouver, PMLR 267) is the template default and does NOT
  mean the paper was accepted at ICML; switch to `\usepackage{icml2025}` for anonymous "under review" mode.
- Authors, affiliations, equal-contribution and corresponding-author macros are hard-coded in `main.tex`
  (`\icmlauthor`, `\icmlaffiliation`, `\icmlcorrespondingauthor`); update there if the Markdown byline changes.
  Title, abstract, key points, body, appendix and bibliography are generated.
- Key points: breakable shaded box after the abstract. Wide tables/figures use `table*`/`figure*`.
- References: `icml2025.bst` (author-year) from `05_data_and_code/references.bib`.
- Supplementary figures (S1-S5): appendix after the references, one column, floats forced to the page bottom so the heading precedes them.

Known remaining issues (source, not layout): some bib entries carry "Suggested: ..." audit notes and the Author
contributions section contains a placeholder "[Detailed contributions ...]"; one Methods table (design list) has no caption in the Markdown;
section 3.2 "Implications" contains only the floated Table 2; the first-page ICML footer wording (see above).
