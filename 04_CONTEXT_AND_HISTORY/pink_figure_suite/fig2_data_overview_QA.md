# Fig. 2 local revision QA

2026-10-18. Rendered and visually inspected `fig2_data_overview.png`; subsequently corrected mathematical-font configuration and positive colourbar sign, then rendered again. No graphical abstract files modified.

- Historical basis: `03_figures/render_supp_v4.py`, function `fig1()`; preserved its three-panel arrangement, signed weight matrix, 180 calibration observations, 120 held-out samples, source values, time axes, row orientation and q calculation.
- Source assertions pass: network 5000; recorded nodes [6,8,11]; stimulus 0; readout 4; 144 matrix entries; max absolute weight rounds to 0.42; both weight signs present; 0.05 time step; q=2.43518 × 10^-4 at displayed precision.
- Pink hierarchy: calibration/recordings #B73E70; readout ring #D99AB3; stimulus/response #87385F. Signed connectivity explicitly uses #413A43 → white → #B73E70, with negative, zero and positive numeric colourbar ticks. These are signed values, not categorical objective colours.
- Retained layout and axes positions; shortened panel headings, standardized panel labels to 8 pt and body text to 6.5–7 pt (stimulus tick labels 6.8 pt). Node identifiers share one page-coordinate left edge rather than varying with tick-label widths.
- Moved integration result to an aligned footer beneath the time axis; removed redundant large in-plot “area=q” and explanatory paragraph, preserving the statement that shading integrates to q in the panel subtitle.
- Strict text test passes: no off-page text or pairwise text overlaps detected. It does not prove absence of all possible text-data intersections; visual inspection checks the illustrated result.
- `pdffonts`: ArialMT and Arial-BoldMT, both embedded TrueType; no DejaVu fallback in final PDF. SVG preserves text. White canvas 180 × 122 mm.

Caption addition: “The signed connectivity map uses grey-purple for negative weights, white for zero and rose for positive weights. Rings and filled markers identify the stimulated, unrecorded readout and recorded nodes; their roles are given by the node key. Shading under the held-out stimulated-minus-control response integrates to q.”

Colour-accessibility correction: the first grey-purple candidate #66546E was rejected after the parent palette check found poor separation from rose under protanopia simulation. Final negative endpoint is darker #413A43. TwoSlopeNorm fixes zero exactly at the white midpoint. Rose denotes the positive numerical sign of the supplied weight, without asserting biological excitatory identity.
