# Submission graphical abstract — prepared, not submitted

Use `graphical_abstract.pdf` as the vector page, `graphical_abstract.png` as preview, or `graphical_abstract.svg` for editing. The design is 190 × 135 mm with Arial 8–10 pt text; every export is below 10 MB. The evidence body retains its original 115-mm physical geometry, with a 20-mm author footer added. The PDF embeds subsetted Arial regular, bold and italic fonts; `pdf_fonts.txt` records the actual pdffonts check. SVG text remains editable and there are no embedded raster images.

The three effect estimates and confidence intervals are read directly from the frozen main-study and independent follow-up summaries, retained without new statistical analysis in `source_effects.csv`. Panel A contains two 97.5% network-cluster intervals for recording-decision effects on raw response MSE (q² units, displayed ×10⁻⁵). Scalar is manuscript blue (#0072B2), vector is manuscript vermilion (#D55E00). Panel B is a different endpoint: one 95% interval for the risk-score effect with identical data and point predictions, rendered in dark ink. Each test has 40 independent networks; nested repetitions are not independent n. All three intervals cross zero.

The stand-alone graphic identifies the broad matched-uncertainty setting, M=3 and endpoint exclusion. Here “matched” describes agreement of the broad prior with generated physiology; it is not the distinct protocol condition named “matched”. The graphic also supplies the MSE-forecast score formula and states that negative differences favor the ensemble in both panels. The exact clipped formula and floor remain in the caption; no evaluated risk reached the floor.

The footer preserves the user-supplied author names, full affiliations, equal-contribution note and correspondence: Jiayi Du¹*† and Shuaizhi Cheng²†; ¹ Stiftung Louisenlund, Germany; ² Department of Computing, Harbin Institute of Technology, China; † Equal contribution. * Correspondence: jiayi.du@mail.louisenlund.de. These details are user-provided, not inferred from the simulation files.

No image-generation service, new experiment, MAP refit or biological validation was used. This is a new data-based composition, not a screenshot montage of manuscript figures. `caption.md` supplies the scientific description, including the score and display transformation. `manifest.json` records source hashes, exact effects, export dimensions, font checks and output hashes.

Reproduce from the project root:

```bash
MPLCONFIGDIR=/tmp/icbr-ga-mpl-cache XDG_CACHE_HOME=/tmp/icbr-ga-xdg-cache PYTHONDONTWRITEBYTECODE=1 work/research-v2-env/bin/python outputs/research_craft_v3/submission/graphical_abstract/make_graphical_abstract.py
```

The files are prepared for review and upload. No submission or external contact has occurred. Physical dimensions are project design choices; acceptance under any specific submission portal remains to be checked against its current requirements.
