# v5 figure changes (all from render_teaser_v5.py; data, counts and intervals unchanged, asserts retained)

Rationale: teaser must show problem and insight at a glance; figures as "a paper within the paper"; annotate what matters.

- fig_audit_schematic_v5 (new, 180 mm): left-to-right pipeline pool -> two criteria -> sets A/B -> common MAP fit -> q vs truth -> forecast v vs error e. Numbered ink badges mark the three audit layers (1 decision agreement, 2 response error, 3 forecast accuracy). Arrow "cannot differ if sets are identical" runs from layer 1 to layer 2. Proportional bars show 82/120 and 26/40. Colours as in STYLE.md. The set dots and v/e bars are illustrative icons, not data.
- graphical_abstract_v5 (190 x 135 mm): network drawing replaced by a compact pipeline strip on top; badges 1-3 bridge strip and the three evidence columns so columns visibly belong to the pipeline; columns widened (larger dot grid, forest plots); takeaway bar and authors block as in v4, with "three-layer audit" wording and the 64% single-network caveat in column 3 (value from the paper). Checked at 60% size.
- fig2_recording_decisions_v5: arrow from grey dots ("same recordings: error cannot differ"), arrow to the exact-zero cluster ("identical designs cannot differ: ratio exactly 1"), arrow to the single outlying network (log2 ratio +1.5, read from the data). Axis annotations moved down to avoid the x-label.
- fig3_risk_forecasts_v5: arrow on the clipped -11.7 bar with axis-break marks and "one network = 64% of the summed difference"; 19 better / 21 worse unchanged.
