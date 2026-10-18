# Figure 1: real model data, fixed illustrative case

Use `fig1_data_overview.pdf` for a manuscript, `fig1_data_overview.svg` for editable vectors/text, and `fig1_data_overview.png` for preview. Page size: 180 × 80 mm; Arial body text 8–9 pt. `caption.md` contains the scientific caption.

The case was fixed by index: J5000, broad prior, truth draw 0, noise draw 0, target 0, endpoint-excluded pool, budget 3, local-scalar design. Selected neurons are 6, 8 and 11; stimulation is at neuron 0; readout is neuron 4. It was not chosen by plotting performance or response magnitude.

All weights, observations and response curves were reconstructed using the frozen main-study source snapshot, protocol, design record and exact original noise stream. The response integral is 0.0002435178366808455, identical to the recorded q_true with absolute difference zero. No MAP refit, new method comparison, image generator or invented trajectory was used.

`weights.csv`, `calibration_observations.csv` and `heldout_response.csv` contain the plotted data. `source_arrays.npz` additionally retains full arrays and the noise realization. `manifest.json` records source/output hashes, fonts, selection, verification and display transformations.

Interpretation: independent n=1 simulated network, illustrating what is measured and predicted. It does not establish a between-method effect or biological validation. Trial 2 is shifted by 6 model-time units for display and separated by a dashed boundary; there is no connecting segment between trials. B uses separate y scales to retain each neuron's rate variation. C scales rate differences by 10,000 in the labelled display; q is the original discrete dt-weighted sum. Heatmap limits are symmetric around zero.

Reproduce from the project root with the existing environment:

```bash
NUMBA_CACHE_DIR=/tmp/icbr-data-overview-numba MPLCONFIGDIR=/tmp/icbr-data-overview-mpl XDG_CACHE_HOME=/tmp/icbr-data-overview-cache PYTHONDONTWRITEBYTECODE=1 work/research-v2-env/bin/python outputs/research_craft_v3/figure_redesign/data_overview/make_data_overview.py
```

Visual review: the rendered PNG was opened and inspected. Initial glyph fallback and bottom-label overlap were corrected; the final layout retains visible margins and no overlapping data labels. Numeric checks establish correspondence to the frozen simulation, not general scientific validity or venue compliance.
