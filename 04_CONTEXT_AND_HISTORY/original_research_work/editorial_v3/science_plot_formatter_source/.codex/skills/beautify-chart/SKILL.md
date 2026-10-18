---
name: beautify-chart
description: Use when a user wants Codex to improve an existing matplotlib plotting script for a specific conference or journal submission. Requires a script path, venue name, and the figure's fraction of column width; Codex must look up the venue specs, render the plot before editing, inspect the image, apply tightly scoped matplotlib style edits, render again, inspect again, and report what changed. Never use when the user asks to change data, colors, semantics, or subplot composition.
---

# beautify-chart

This skill turns an existing matplotlib script into a publication-ready scientific figure. The workflow is strict:

`venue lookup -> baseline render -> visual inspection -> scoped edit -> verification render -> final report`

Do not edit plot style before rendering and inspecting the baseline image. Do not claim success before rendering and inspecting the edited image.

## Inputs

Collect only missing inputs:

1. `script_path` - path to the matplotlib `.py` script.
2. `venue` - target conference or journal, e.g. `NeurIPS 2026`, `Nature Communications`, `ICML 2026`.
3. `fraction` - figure width as a fraction of the venue column width. Use `2.0` for full two-column text width when applicable.

Do not ask the user for raw values such as `column_width_in` or `body_pt` unless the venue lookup fails after a good-faith attempt.

## Codex Tooling

- Browse current official venue or publisher instructions for column width, text width, body font size, and font family. Prefer official author kit, LaTeX class, template, or publisher style pages. Cite sources in the final answer when browsing was used.
- Use shell commands to run the script from its own working directory with `MPLBACKEND=Agg`.
- Save baseline and edited renders as explicit image files, preferably beside the script or in a small task-local output directory.
- Inspect generated images with the available local image-viewing capability using absolute file paths. If image viewing is unavailable, say that verification is blocked rather than pretending visual inspection happened.
- Edit files with Codex's normal patch workflow. Keep changes narrowly scoped; preserve user edits and unrelated code.
- Do not commit unless the user explicitly asks.

## Phase 1 - Venue Lookup

Find the official venue or journal guidance and extract:

- `column_width_in` - single-column width in inches.
- `textwidth_in` - full text width in inches for two-column venues, if provided.
- `body_pt` - body text font size in points.
- Font family requirement, if mandated.

Compute final printed width:

- `fraction <= 1.0`: `W_page = fraction * column_width_in`.
- `fraction > 1.0`: for two-column venues, `W_page = (fraction / 2.0) * textwidth_in`; for single-column venues, use `fraction * column_width_in` capped by `textwidth_in` when known.

If official values cannot be found, state exactly what was attempted and ask the user for the missing numeric values. Do not invent venue specs.

Record the values before editing so the user can sanity-check them.

## Phase 2 - Baseline Render

Run the script before making style edits:

```bash
MPLBACKEND=Agg python path/to/script.py
```

Use the script's own working directory unless the user says otherwise. Do not alter data loading during this phase. If the script fails, make only the minimum fix needed to render the baseline, such as creating a missing output directory; do not fold style changes into that fix.

Open and inspect the produced PNG. If the script only writes PDF/SVG/EPS, add or use an existing `savefig` path that also produces a PNG for inspection, while preserving the intended final output.

## Phase 3 - Critical Inspection

Inspect the rendered image as it will appear at `W_page` inches wide on the page. Mentally shrink the image to printed size and write a concrete issue list before editing.

Check at least:

- Legibility of tick labels, axis labels, annotations, legend, and colorbar at final printed size.
- Visual hierarchy between labels, title, ticks, legend, and data marks.
- Overlaps, clipping, cramped margins, and subplot collisions.
- Balance of data stroke, marker size, axis spines, grid, and errorbar caps.
- Tick density, tick rotation, scientific notation, and label padding.
- Legend position, footprint, frame, handle length, and whether it covers the data climax.
- Colorbar size, label readability, and padding.
- Venue-specific requirements such as fonts and figure size limits.

Tie each issue to something visible in the baseline image. If the first inspection finds no issues, re-inspect; a truly paper-ready baseline is rare and needs an explicit reason.

## Phase 4 - Design The Visual System

Use `venue`, `W_page`, `body_pt`, chart type, and the issue list to choose the style system.

Recommended printed-page values:

- `figsize`: width should equal `W_page`. Height should match chart type unless the existing aspect is deliberate:
  - line, scatter, or bar: `0.60-0.70 * width`
  - distribution, violin, or box: about `0.75 * width`
  - heatmap, spatial plot, or confusion matrix: about `1.00 * width`
- Typography: tick labels and legend usually `body_pt - 2` to `body_pt - 3`; axis labels around `body_pt - 1` to `body_pt`. Keep labels at least as large as ticks.
- Captioned paper figures: on-figure titles are auxiliary. For column-width panels, set `axes.titlesize <= axes.labelsize` and keep title padding tight, or remove an unnecessary title only if the script already relies on captions and the user intent is clear.
- Strokes: data lines should be visibly stronger than spines; grid lines should recede.
- Markers: markers should read as points, not just line thickening; marker size should usually be at least about `3 * line width`.
- Error bars: add explicit `capsize` and `capthick` to `errorbar(...)`; these are not fully handled by rcParams.
- Legend: keep it inside the axes by default with `ncol=1`. Shrink via font size, handle length, padding, and spacing before considering `ncol > 1` or outside placement.
- Ticks: tune tick sizes, widths, and pads; avoid changing semantic tick locators unless density is itself the visual problem and the change preserves meaning.
- Font family: follow the venue mandate if there is one; otherwise preserve the user's existing family.

Present the intended changes as a single `plt.rcParams.update({...})` block plus any necessary per-call adjustments.

Never touch data values, colors, colormaps, linestyles, semantic axis limits, log scales, subplot grid structure, or the meaning of plotted elements.

## Phase 5 - Apply Edits

Patch the script in place:

- Insert or replace one central `plt.rcParams.update({...})` block near the matplotlib import.
- Replace only the relevant `figsize=...` argument on `plt.figure(...)` or `plt.subplots(...)`.
- Remove stale per-call `fontsize=`, `labelsize=`, `linewidth=`, and `markersize=` kwargs when they conflict with the central style block.
- Add explicit `capsize=` and `capthick=` to each `errorbar(...)`.
- Keep layout changes minimal. Prefer `layout="constrained"` or `fig.tight_layout(...)` only when needed to resolve clipping or spacing issues.
- Do not reorder unrelated code, rename variables, or rewrite plotting semantics.

## Phase 6 - Verification Render

Render again and inspect the edited PNG before reporting success.

Also measure edge padding in pixels rather than relying only on visual judgement. Use Python/Pillow or another local image library to find the non-background bounding box and report whether any drawn content touches the canvas edge. A few pixels of apparent whitespace in a thumbnail can still hide clipped rotated text.

For every Phase 3 issue, mark it:

- `resolved`
- `partial`
- `still present`

Then scan for regressions:

- New clipping or insufficient save padding.
- New overlaps from the smaller printed width.
- Over-thickened data lines or oversized markers.
- Legend covering the data climax after being moved or widened.
- Colorbar or subplot spacing becoming cramped.

If a listed issue remains or a regression appears, make one targeted adjustment and re-render. Cap at 2-3 edit/render iterations before checking in with the user.

## Phase 7 - Final Report

Summarize:

- Venue spec values used: `column_width_in`, `textwidth_in` if relevant, `body_pt`, and font family.
- Computed `W_page` and the input `fraction`.
- Key changes: figsize, font sizes, linewidths, marker size, ticks, legend, and errorbar caps.
- Baseline issues and their verification status after editing.
- Absolute paths to the baseline and edited image files.
- Any remaining limitations, including failed venue lookup, unavailable image viewing, or tests/renders that could not be run.

## Red Flags

Stop and reconsider if:

- You are about to edit style before rendering and inspecting the baseline image.
- You are about to report success before rendering and inspecting the edited image.
- The venue lookup failed and you are inventing column widths or body font sizes.
- The issue list is empty without a clear reason.
- You are changing data, colors, colormaps, linestyles, or plot semantics to make the figure look better.
