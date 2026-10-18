# Fig1 / Fig5 presentation patch QA

- Original images actually inspected before editing: `fig_audit_schematic_v5.png`, `fig4_model_extension_v4.png`.
- Outputs: `fig1_audit.{pdf,svg,png}`, `fig5_extension.{pdf,svg,png}`. Reproducer: `render_schematic_extension.py`.
- Local presentation patch retains original layouts and scientific sequence. No GA function is called. Existing evidence source files remain untouched.
- Fig1 stays 180 × 98 mm; Fig5 stays 180 × 88 mm. The original figure-wide millimetre geometry and deterministic axes are retained. All text is Arial, ordinary 6–7 pt; panel letters and step numbers 8 pt. Black text on white or near-white pink panel fills. PDF font audit confirms embedded ArialMT / Arial-BoldMT; Fig1 also embeds Arial-BoldItalicMT.
- Palette: single #B73E70, shared #D99AB3, forecast #87385F, neutral #C9C5C8. Shared extension uses a square with a dark mulberry outline; single uses circles. Filled/hollow still represents whether the unchanged 95% interval excludes zero.
- Data: existing source assertions pass: identical sets 82/120 and 26/40; main response changes −3.7% and +2.7%; forecast score −0.46; 19/40 networks favour prior-averaged risk; extension 4/8 intervals exclude zero. Extension CI values read directly from frozen `n100_paired_effects.csv`. No new inference.
- Visual check: both output PNGs inspected at full rendered size. No visible text collision, clipped CI or missing characters. The Fig1 illustrative e² bar previously extended beyond its container; both illustrative bars were shortened proportionately to fit (not measured experimental quantities). Original diagram boxes retained to preserve the accepted scientific story; cosmetic pink fills remain extremely pale.
- Limit: this is standalone figure QA. Final manuscript placement, caption consistency and full-paper PDF verification belong to suite integration.

## Review revision

Fig1 keeps the original 180 × 98 mm canvas and component positions. Removed the Key insight block/black rule, large curved arrow and italic headline. Replaced round step badges with small a/b/c labels aligned to the corresponding title baselines. Changed containers to thin square rules. The lower-left replacement explicitly distinguishes identical point predictions from separate risk-forecast scoring; no forecast improvement is claimed to improve the fixed point prediction.

Final typography supersedes the earlier all-black note: Arial panel letters 8 pt Bold #27232B; short titles 7 pt Bold #27232B; categories 6.8 pt Regular; axes 7 pt Regular #49424B; ticks 6.3 pt Regular #6B626D; results 6.5 pt Regular #27232B; secondary text 6 pt Regular #776F78. Fig5 composition and all data remain unchanged. Both revised outputs were viewed again. Embedded fonts now ArialMT and Arial-BoldMT only.
