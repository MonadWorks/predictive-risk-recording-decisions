# Latest Fig.2/3 audit: descriptive ratios and separated score interval

2026-10-17 (Asia/Shanghai). Independent read-only verification of the latest PNG/PDF/SVG, renderer and frozen source tables. Only this audit report is written in the project. Temporary PDF renders were used for visual checks. No source, plot, inference or data were changed.

## Immediate issues / required documentation alignment

1. **Current manuscript captions lag the new panels.** At audit time Fig.2 caption still described paired MSE-versus-MSE logarithmic axes and an identity line. It must now state x=nominal MSE on a log axis, y=within-J log2(ensemble MSE/nominal MSE), null y=0, and explicitly call a/b descriptive diagnostics. This is not the ratio of aggregate means, a new primary endpoint, or a mean-log-ratio inference. Panel c remains the original raw-MSE primary difference with 97.5% intervals. Define E/N in the caption.
2. Fig.3 caption still located the mean and 95% interval in b. It must distinguish **b = all 40 individual network differences on the complete range** and **c = population mean and frozen 95% CI on a separate scale**. State that the two panels show distinct statistical objects, so no individual value is omitted by c's limits.
3. Minor display issue: Fig.2 appears to request only three x major ticks, but additional minor power-of-ten labels remain visible, creating irregular dense groups. Use a NullFormatter/NullLocator for minor ticks if the intent is three labels. This is a readability issue, not a numeric-position error.

## Verified improvements and preserved numerical contracts

- Fig.2 a/b each has exactly 40 SVG data markers, all planned IDs. Every descriptive ratio was independently recomputed as log2(E/N) from the original J-level MSEs; marker SVG coordinates were inverted and agree. Scalar ratio range [−0.5802303, +1.4684051], vector range [−1.3904725, +0.6024050]; all are inside [−1.65,+1.65], so neither tail is clipped. All baseline MSEs remain positive and inside the common log x limits. No pseudocount or ratio-based filtering was introduced. Ratios sharing a denominator with x must not be treated as independent causal evidence of a baseline-difficulty effect.
- Fig.2 c still shows the two original raw-MSE differences and complete 97.5% limits. The factor 1e5 is only the labelled display unit. Source rows are identical to the frozen effect table, and actual SVG interval endpoints invert back to the same numbers.
- Fig.3 a has 40 nominal plus 40 ensemble risk points on the same actual-MSE y values. All lie inside the complete shared log bounds. The two additional one-symbol SVG collections are legend symbols, not extra data.
- Fig.3 b retains all 40 network scores including the large negative tail (minimum about −11.67); there is no discarded outlier. Fig.3 c's mean and limits equal the frozen summary, and the actual SVG error-bar path endpoints reproduce them. Its positive upper endpoint now extends 0.852 mm, approximately 10.1 pixels at 300dpi beyond zero. In the actual PDF render the positive cap is visibly separated from the zero line, addressing the earlier subpixel issue without modifying the interval.
- Colours retain objective semantics; open/filled symbols distinguish individual nominal/ensemble forecasts only where those are separately plotted. Original primary tests and independent follow-up are not pooled or redefined.
- PNGs and independently rendered PDFs were inspected. No page-edge clipping, text overlap, missing glyph or point/CI cutoff was observed. Both PDFs remain 180mm wide, fonts embedded, with intended 138/100mm heights. This is a content/readability audit, not an aesthetic approval or journal-compliance certification. Exact ties can still overplot even when all 40 markers are present; source IDs preserve the count.

## Independent numeric/artifact record

```json
{
  "fig2": {
    "Single response": {
      "markers": 40,
      "descriptive_log2_ratio_range": [
        -0.5802303339945198,
        1.468405092972353
      ],
      "actual_svg_coordinates_verified": true
    },
    "Three responses": {
      "markers": 40,
      "descriptive_log2_ratio_range": [
        -1.3904725419633468,
        0.6024050028921151
      ],
      "actual_svg_coordinates_verified": true
    }
  },
  "fig2_primary_raw_differences": [
    {
      "contrast": "ensemble_scalar - local_scalar",
      "effect": "-2.586421129091058e-06",
      "ci_low": "-1.4713046771189118e-05",
      "ci_high": "4.826304931626923e-06",
      "confidence_level": "0.975"
    },
    {
      "contrast": "ensemble_vector - local_vector",
      "effect": "1.923627390429782e-06",
      "ci_low": "-1.1479707624311079e-06",
      "ci_high": "6.8260498523981685e-06",
      "confidence_level": "0.975"
    }
  ],
  "fig3_score_range": [
    -11.67124304146914,
    1.0667274098208435
  ],
  "fig3_svg_collections": [
    40,
    40,
    1,
    1,
    40
  ],
  "fig3_primary": {
    "mean": -0.4556473561820947,
    "ci95": [
      -1.1585679104693787,
      0.023668677150677265
    ]
  },
  "fig3_positive_ci_extent_mm": 0.8520723774243816,
  "fig3_positive_ci_extent_300dpi_px": 10.063846977453327,
  "pdf_checks": [
    {
      "figure": "fig2_recording_decisions",
      "pdf_size_mm": [
        179.9999222222222,
        137.99996388888886
      ],
      "png_pixels": [
        2125,
        1629
      ],
      "all_fonts_embedded": true,
      "output_hashes_verified": true
    },
    {
      "figure": "fig3_risk_forecasts",
      "pdf_size_mm": [
        179.9999222222222,
        100.00015277777776
      ],
      "png_pixels": [
        2125,
        1181
      ],
      "all_fonts_embedded": true,
      "output_hashes_verified": true
    }
  ]
}
```

## Limits

No new bootstrap or test was introduced. This audit verifies that the new display transformation and separated axes preserve the frozen evidence; it does not establish method benefit, equivalence, biological validation, full probability calibration or satisfactory overall aesthetic design. The captions should be brought into agreement before this version is presented as a self-contained paper.

## Audited artifact hashes

- `fig2_recording_decisions.pdf`: `458d222a767b50b0ffde2a4492523c38e46c94c46a9d5acaade7a8c292ffc9b5`
- `fig2_recording_decisions.svg`: `1f01853e7488aed6fe41993b0b6b156f648ecadafbb1c34ea82d2b7af783480e`
- `fig2_recording_decisions.png`: `9fbe944afa52317b98b7dade4446cb617480fc16a9a41818c264d7cadd665938`
- `fig3_risk_forecasts.pdf`: `f960424496ec081eeca63696ca87f1ec4ee1ddd7cc0e705852698fec9df69525`
- `fig3_risk_forecasts.svg`: `114d9a9dab55f0a00bfac6bcb028360456bfd8b8abc3adba9cd2cb6f111d6929`
- `fig3_risk_forecasts.png`: `2fc9f77debc180c311382667ac0bcf35e7e06b47c94f880d7ce10bab9ec5e390`


## Closing readback after the independent audit

The manuscript captions now match the actual Fig.2/3 panels. Minor log tick locators/formatters were disabled; the final Fig.2 has only the three intended major labels on each x axis. The root agent opened the final PNG after this change. All nine current figures and the graphical abstract passed the PDF font/dimension and raster-free SVG preflight in `figures/export_preflight.json`. The exact current artifact hashes are in that receipt and `figures/figure_manifest.json`; the historical hashes above identify the earlier audited render. The statistical arrays and intervals did not change.
