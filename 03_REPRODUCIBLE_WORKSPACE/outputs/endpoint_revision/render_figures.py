"""Re-render the nine extension figures from their frozen plotting sources.

The sources, numerical results, labels and coordinates remain intact. This
presentation layer replaces colors only and writes current manuscript assets.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.collections import Collection
from matplotlib.patches import Patch
from figure_style import apply_palette

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1] / 'work/recording_extensions'
STEMS = {
    'endpoint_evidence', 'fitting_sensitivity', 'mechanism_evidence',
    'method_validation', 'parameter_mechanism', 'structure_robustness',
    'limited_budget', 'combination_controls', 'recording_information',
}


def geometry(fig):
    """Fingerprint coordinates, data, labels and opacity independently of color."""
    h = hashlib.sha256()
    def add(x):
        if isinstance(x, np.ndarray):
            h.update(str((x.shape, x.dtype)).encode()); h.update(x.tobytes())
        else:
            h.update(repr(x).encode())
    for ax in fig.axes:
        add((ax.get_xlim(), ax.get_ylim(), ax.get_xscale(), ax.get_yscale(), ax.get_position().bounds))
    for a in fig.findobj():
        add(type(a).__name__); add(a.get_alpha()); add(a.get_visible())
        if isinstance(a, Line2D):
            add(np.asarray(a.get_xdata())); add(np.asarray(a.get_ydata()))
            add((a.get_linewidth(), a.get_linestyle(), a.get_marker(), a.get_markersize()))
        elif isinstance(a, Collection):
            add(np.asarray(a.get_offsets())); add(a.get_linewidths())
            for p in a.get_paths(): add(p.vertices); add(p.codes)
            for rgba in [a.get_facecolors(), a.get_edgecolors()]: add(rgba[:, 3])
        elif isinstance(a, Patch):
            add(a.get_path().vertices); add(a.get_transform().get_matrix()); add(a.get_linewidth())
        elif isinstance(a, matplotlib.text.Text):
            add((a.get_text(), a.get_position(), a.get_fontsize(), a.get_rotation()))
    return h.hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(mod)
    return mod


def main(out, audit=None):
    out.mkdir(parents=True, exist_ok=True)
    original = Figure.savefig
    checks = {}
    def save(fig, path, *args, **kwargs):
        name = Path(path).stem
        if name not in STEMS:
            raise ValueError('Unexpected figure: ' + str(path))
        fig.canvas.draw()
        before = geometry(fig)
        apply_palette(fig)
        after = geometry(fig)
        assert before == after, 'Palette changed figure geometry: ' + name
        checks[name] = {'geometry_unchanged': True, 'geometry_sha256': before}
        original(fig, out / Path(path).name, *args, **kwargs)
    Figure.savefig = save
    try:
        r2 = module('endpoint_round2_figures', RESEARCH/'round2/code/figures.py')
        r2.endpoint_plot(); r2.fit_plot()
        r3 = module('endpoint_round3_figures', RESEARCH/'round3/code/figures.py')
        r3.main()
        r4 = module('figures4', RESEARCH/'round4/code/figures4.py')
        r4.main()
        r5 = module('endpoint_round5_figures', RESEARCH/'round5/code/figures5.py')
        r5.main()
    finally:
        Figure.savefig = original
        plt.close('all')
    assert set(checks) == STEMS
    if audit:
        audit.write_text(json.dumps(checks, indent=2) + '\n')
    print(f'Rendered {len(checks)} figures; all data, labels and geometry unchanged.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=HERE/'figures')
    parser.add_argument('--audit', type=Path)
    args = parser.parse_args()
    main(args.out, args.audit)
