# 06_latex/common - template-independent Markdown -> LaTeX conversion

`md2tex.py` (+ `filter.lua`, `mdcommon.sty`) turns `02_paper/paper_v4.md` into
neutral LaTeX fragments. A template folder (`ieee/`, later `biomed/`, `conf/`)
only needs a `main.tex` that `\input`s them, and a Makefile that calls:

    python3 ../common/md2tex.py --md ../../02_paper/paper_v4.md --outdir build \
        --workdir . --lua ../common/filter.lua --bib-real ../../05_data_and_code/references.bib
    # LaTeX must run with TEXINPUTS=../common:  so \usepackage{mdcommon} resolves

`--workdir` = directory LaTeX runs in (image paths are written relative to it).
Needs pandoc >= 3 and python3.

## Output (in `--outdir`)
| file | content |
|---|---|
| `meta.tex` | macros `\PaperTitle \PaperAuthors \PaperAffiliations \PaperAuthorNotes \PaperManuscriptNote` and flags `\ifpaperabstract \ifpaperkeypoints \ifpaperkeywords \ifpaperappendix` |
| `abstract.tex`, `keypoints.tex`, `keywords.tex` | content of `## Abstract`, `## Key points`, `## Keywords` (empty if absent) |
| `body.tex` | all other `##` sections; `##`->`\section`, `###`->`\subsection`; manual numbers stripped |
| `appendix.tex` | `## Supplementary...` section (figures with `\caption`); template resets the figure counter to `S\arabic{figure}` |
| `references.bib` | copy of `--bib-real` if it exists, else a placeholder generated from the Markdown `## References` list. Keys `ref01..refNN` |

`## Contents` and `## References` are dropped from the body; HTML comments are removed.
Template must call `\bibliography{build/references}` and `\cite` keys come from `[n]`, `[n,m]`, `[n-m]`.

## Markdown conventions handled
- `![alt](path)` followed by `**Fig. N | Title.** text` -> `figure`/`figure*` (width > 4.2 in at 300 dpi -> `figure*`, class `.wide`).
  Path rewritten to `X_v4` / `X_v4/` variants if present, and to a same-stem `.pdf` if not older than the PNG.
- `**Table N | Title.** note` before a pipe table -> `table`/`table*` with `\caption{Title}`, booktabs, note under table; widths picked from cell text length (natural, stretched, or `p{}` columns using `\tblw`). Uncaptioned pipe tables are typeset too.
- Float numbers follow the Markdown labels (`\setcounter`), a warning is printed if they are out of order.
- `\[ ... \]` -> numbered `equation` (`aligned` if it contains `\\`).
- Unicode superscript/subscript runs (`10⁻⁵`, `₂`) -> `\textsuperscript`/`\textsubscript`; other glyphs via `mdcommon.sty` (`newunicodechar`, pdflatex). Add new glyphs there.
- Literal `~`/`^` are escaped; `$...$` inline math works.

A template must load `mdcommon` after its font package, and provide `figure*`/`table*` floats. Fonts/packages that clash with amssymb (newtxmath) are handled.
