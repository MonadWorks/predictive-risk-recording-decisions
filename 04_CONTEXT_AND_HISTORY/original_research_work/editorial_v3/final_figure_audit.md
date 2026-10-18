# v3 figures: final independent numeric/readability audit

2026-10-16. Read-only audit of Fig.2/3/4, source tables, renderer and captions. No plots, source data, renderer, protocol, or inference were changed. PDF pages were temporarily rendered with Poppler outside the project, then inspected. This audit is a numerical and readability baseline; it does not declare aesthetic success or a target-journal compliance pass.

## Actionable issues, prioritized

1. **Fig.3b: the important positive side of the 95% CI is visually almost invisible.** Its actual upper bound is +0.0236687, so the interval crosses zero. On the current shared score axis [−12.5,2], this extends only 0.0852 mm, 1.01 pixels at 300dpi to the right of zero, less than the CI stroke width. The zero line and interval line can visually swallow this positive extent. The printed numeric CI is correct, but the chart can be misread as ending exactly at zero. Preserve the entire network distribution, including J6015, on its full-range axis; put the aggregate effect and full CI on a separately labelled tighter effect-only forest axis. This separates different statistical objects, rather than clipping any network or modifying the CI.
2. **Fig.2a/b: pairing is truthful but near-identity clouds dominate the argument.** Both panels span nine decades and most points sit near y=x. They reveal wide differences in task difficulty more readily than design differences. The raw-difference forest correctly supplies the primary inference, but the large scatter area and substantial whitespace still make the page feel weakly prioritized. Keep paired data available; choose panel area according to the argument, and coordinate the scatter with complete paired-difference distributions/influence diagnostics rather than implying that proximity to the diagonal proves equivalence. No axis truncation or point exclusion is recommended.
3. **Fig.3 is still two different readings with little visual hierarchy.** The left panel is a descriptive comparison of mean risks with the same actual MSE; the right is a score-functional test averaged at the case level. Those values cannot be recomputed by scoring the plotted aggregates. The current caption states this correctly, but a reader scanning the panels can miss it. The redesigned architecture should make the shared point prediction and the difference between descriptive coordinates and primary score explicit, while reducing repeated prose.
4. **Fig.4 displays uncertainty clearly but not the eight-network outcome distribution.** There are eight aggregate contrast markers/intervals, each based on eight J; these are not the eight raw network outcomes. This is not a point-count error. The caption correctly states the sampling unit. If individual-network influence is substantively discussed, supply a complete paired network distribution in the supplement; do not make the enormous vector M=10 uncertainty prettier by dropping its full interval.
5. **Minor semantic consistency:** Fig.2 scatter axes say MSE without q² while its forest and Fig.3 include q². Adding units consistently would reduce reliance on captions. Colours consistently represent objectives; open/filled forecast encoding is meaningful only when individual nominal/ensemble forecasts are plotted, not for paired scatter or effect markers. Current captions make this distinction; keep it during skill-based redesign.

## Independent numerical and artifact checks

```json
{
  "numerical_status": "PASS: no altered estimands, points, intervals or source tables detected",
  "source_data_copies_sha256_verified": [
    "holdout_network_metrics.csv",
    "holdout_paired_effects.csv",
    "holdout_primary_paired.csv",
    "holdout_summary.json",
    "forecast_network_metrics.csv",
    "forecast_summary.json",
    "n100_network_metrics.csv",
    "n100_paired_effects.csv",
    "n100_summary.json"
  ],
  "fig2_points_per_objective": 40,
  "fig2_raw_mse_display_multiplier": 100000,
  "fig2_ci_level": 0.975,
  "fig3_risk_points": 80,
  "fig3_score_points": 40,
  "fig3_ci_level": 0.95,
  "fig4_independent_networks": 8,
  "fig4_aggregate_effect_markers": 8,
  "fig4_ci_level": 0.95,
  "all_primary_points_inside_limits": true,
  "all_intervals_inside_limits": true,
  "actual_svg_interval_endpoints_independently_verified": true,
  "fig3_positive_ci_extent_mm": 0.08520723774243816,
  "fig3_positive_ci_extent_at_300dpi_px": 1.0063846977453326,
  "artifact_checks": [
    {
      "figure": "fig2_recording_decisions",
      "pdf_size_mm": [
        179.9999222222222,
        137.99996388888886
      ],
      "png_size_px": [
        2125,
        1629
      ],
      "png_width_mm": 179.9170265007197,
      "svg_scatter_use_counts": [
        40,
        40
      ],
      "pdf_fonts": "name                                 type              encoding         emb sub uni object ID\n------------------------------------ ----------------- ---------------- --- --- --- ---------\nGOFYPY+Arial-BoldMT                  CID TrueType      Identity-H       yes yes yes     17  0\nGOFYPY+ArialMT                       CID TrueType      Identity-H       yes yes yes     24  0\nBMQQDV+DejaVuSans                    CID TrueType      Identity-H       yes yes yes     31  0\n"
    },
    {
      "figure": "fig3_risk_forecasts",
      "pdf_size_mm": [
        179.9999222222222,
        100.00015277777776
      ],
      "png_size_px": [
        2125,
        1181
      ],
      "png_width_mm": 179.9170265007197,
      "svg_scatter_use_counts": [
        40,
        40,
        1,
        1,
        40
      ],
      "pdf_fonts": "name                                 type              encoding         emb sub uni object ID\n------------------------------------ ----------------- ---------------- --- --- --- ---------\nGOFYPY+Arial-BoldMT                  CID TrueType      Identity-H       yes yes yes     18  0\nGOFYPY+ArialMT                       CID TrueType      Identity-H       yes yes yes     25  0\n"
    },
    {
      "figure": "fig4_model_extension",
      "pdf_size_mm": [
        179.9999222222222,
        111.99988888888889
      ],
      "png_size_px": [
        2125,
        1322
      ],
      "png_width_mm": 179.9170265007197,
      "svg_scatter_use_counts": [],
      "pdf_fonts": "name                                 type              encoding         emb sub uni object ID\n------------------------------------ ----------------- ---------------- --- --- --- ---------\nGOFYPY+Arial-BoldMT                  CID TrueType      Identity-H       yes yes yes     15  0\nGOFYPY+ArialMT                       CID TrueType      Identity-H       yes yes yes     22  0\n"
    }
  ]
}
```

## What was verified

- Bundled numerical source tables are byte-identical to the corresponding v2 analysis outputs. Input and output hashes match figure_manifest.json.
- Fig.2: each objective has all 40 planned networks, no duplicate/missing IDs; x/y exactly reproduce the paired method MSEs. Every point is strictly positive and inside the shared log bounds. Both raw differences and 97.5% limits are unchanged; multiplication by 1e5 is only the stated display unit. Actual SVG line coordinates invert back to the complete original interval endpoints. The displayed rounded values −0.259 [−1.471,+0.483] and +0.192 [−0.115,+0.683] agree with source values in units of 1e−5 q².
- Fig.3: all 40 new networks appear; the SVG contains 40 nominal and 40 ensemble risk markers plus 40 score-difference points (two additional single-symbol collections belong to the legend). No risk point or extreme score difference is outside the stated axes. The mean and 95% CI are identical to the frozen follow-up summary; SVG CI endpoints are numerically correct, despite the visibility issue above. Actual MSE is shared across the two forecasts.
- Fig.4: all eight planned networks are present in source data. All eight objective/pool/budget contrasts are shown, with their entire pointwise 95% intervals. Ratio-of-aggregate-means effects and intervals were independently recomputed from the eight J-level MSEs with the original bootstrap seed/resamples; they match. Actual SVG interval endpoints match the source table after percentage scaling. These comparisons remain exploratory.
- PDFs are exactly 180mm wide within metadata rounding, with intended heights 138/100/112mm; PNG physical widths agree. Arial/Arial Bold/DejaVu TrueType fonts are embedded. Temporary PDF renders showed no page-edge clipping, text overlap, missing glyphs or obvious tick collisions. Labels are readable at the intended width; this does not imply successful overall figure design.

## Limits and handoff

The review checked rendered PDFs, PNG metadata, SVG point/interval geometry, source-table identity, captions and renderer semantics. It did not certify accessibility, simulate every colour-vision condition, retest the scientific model, verify a journal-specific production specification, or approve aesthetic quality. Exact overplotting can make fewer than 40 distinct dots perceptually separable even when all 40 SVG markers exist; retain source IDs and explain ties. The source-level confidence intervals remain the authority while new figure skills/layouts are evaluated. No new test or inferential claim should be introduced as part of that redesign.

## Optional skill-combination leads, actually checked (not installed)

The user requested real high-star skill sources, so an additional read-only check verified these concrete SKILL.md files. Star counts belong to their **whole repositories**, not individual figure skills, and were approximate live GitHub displays on 2026-10-16.

- [anthropics/skills](https://github.com/anthropics/skills), approximately 181.5k stars: [canvas-design/SKILL.md](https://github.com/anthropics/skills/blob/main/skills/canvas-design/SKILL.md) exists, and its own [LICENSE.txt](https://github.com/anthropics/skills/blob/main/skills/canvas-design/LICENSE.txt) is Apache 2.0. This is an art/design-philosophy workflow, including typography and canvas refinement, rather than a statistical plotting engine. It explicitly encourages artistic freedom and permits font downloads; these parts cannot override frozen scientific geometry, required labels or data integrity. A plausible bounded role is composition review of an already validated data layer. It is not evidence that the current figures will become good simply by invoking it; font assets also need their own license checks.
- [K-Dense scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills), approximately 51.2k stars: actual [scientific-visualization](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md), [matplotlib](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/matplotlib/SKILL.md), and [seaborn](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/seaborn/SKILL.md) files were read. The repository-level license is MIT; individual frontmatter also points to upstream library licenses. Matplotlib/Seaborn skills declare Read/Write/Bash capabilities and environment-specific dependencies; the examined Matplotlib snapshot targets 3.11.2, while the current figure package ran 3.10.1. No dependency migration was performed. Seaborn adds pandas and can compute estimators/intervals automatically, which must be disabled when presenting these frozen cluster estimates.

A useful combination has explicit responsibilities: scientific-visualization defines information hierarchy and export checks; Seaborn proposes distribution/facet alternatives from fixed J-level tables without new inference; Matplotlib supplies exact point/CI geometry; canvas-design reviews composition/typography inside an immutable statistical contract. The resulting candidate must still undergo the same source-value, full-range, interval and final-size checks above. Copying several prompts or counting stars is not a rendering experiment. Root should test a genuinely different composed candidate against the rejected baseline before claiming improvement.
