"""Local presentation-only revision of historical render_supp_v4.py fig1().
Signed weights use grey-purple / white / rose; source arrays remain frozen.
Run with the existing research-v2-env Python. No graphical abstract is touched.
"""
import csv, json, os
from pathlib import Path
os.environ.setdefault('MPLBACKEND', 'Agg')
HERE = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(HERE / '.cache/mpl'))
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import Circle
from matplotlib.ticker import FuncFormatter, MaxNLocator, LogLocator, NullFormatter, FixedLocator

PACK = Path(__file__).resolve().parents[2] / 'work/evidence/ICBR2026_v4_pack'
DATA = PACK / '05_data_and_code/source_data'
FIG1 = PACK / '05_data_and_code/fig1_data'
FIG1X = PACK / '05_data_and_code/fig1_data_extra'
V3_OVERVIEW = PACK.parent / 'outputs/research_craft_v3/figure_redesign/data_overview'  # optional cross-check only
OUT1 = HERE
OUTS = HERE / 'supplementary_v4'
# No supplementary directory created by this standalone figure.

# ---- palette (copied from render_v4.py / style/STYLE.md) ----------------------------------------
INK = '#15202B'; MUTED = '#5A6570'; RULE = '#D9D4C9'; PANEL = '#EFEBE3'; PAPER = '#F7F4EE'
SCALAR = '#B73E70'; VECTOR = '#D99AB3'; FORECAST = '#87385F'; GREY = '#8C7F88'; SAME = '#C9C5C8'
VECTOR_TEXT = INK
POS = '#B73E70'; NEG = '#413A43'   # sign of a connection weight (as in the graphical abstract: blue +, orange -)
def tcol(c): return VECTOR_TEXT if c == VECTOR else c

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 6.5, 'axes.linewidth': .6, 'axes.edgecolor': INK, 'text.color': INK,
    'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK,
    'xtick.labelsize': 6.5, 'ytick.labelsize': 6.5, 'axes.spines.top': False,
    'axes.spines.right': False, 'pdf.fonttype': 42, 'svg.fonttype': 'none',
    'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic', 'mathtext.bf': 'Arial:bold', 'figure.facecolor': 'white', 'savefig.facecolor': 'white',
    'axes.unicode_minus': True})
MINUS = '−'
STRICT = True


def rows(name, base=DATA):
    with (base / name).open() as f: return list(csv.DictReader(f))


def export(fig, path_stem, svg=True):
    for ext in ('pdf', 'png') + (('svg',) if svg else ()):
        fig.savefig(f'{path_stem}.{ext}', dpi=300, bbox_inches=None, facecolor=fig.get_facecolor())
    plt.close(fig)


class Page:
    """Figure with a full-page axes in millimetres (origin bottom-left) plus helpers for mm-placed axes."""
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.fig = plt.figure(figsize=(W / 25.4, H / 25.4))
        self.base = self.fig.add_axes([0, 0, 1, 1]); self.base.set_xlim(0, W); self.base.set_ylim(0, H)
        self.base.axis('off')
        self.texts = []

    def T(self, x, y, s, **k):
        k.setdefault('va', 'center')
        t = self.base.text(x, y, s, **k); self.texts.append(t); return t

    def ax(self, l, b, w, h, **kw):
        a = self.fig.add_axes([l / self.W, b / self.H, w / self.W, h / self.H], **kw)
        a.patch.set_alpha(0); return a

    def label(self, x, y, s): return self.T(x, y, s, fontsize=8, fontweight='bold')

    def check_text(self):
        """No text may leave the page and no two drawn text boxes in the base layer may overlap."""
        self.fig.canvas.draw(); r = self.fig.canvas.get_renderer()
        W, H = self.fig.canvas.get_width_height()
        boxes = []
        hidden = set()
        for a in self.fig.axes:
            for axis in (a.xaxis, a.yaxis):
                lo, hi = sorted(axis.get_view_interval())
                for tk in axis.get_major_ticks() + axis.get_minor_ticks():
                    if not (lo <= tk.get_loc() <= hi) or not tk.get_visible(): hidden.update((tk.label1, tk.label2))
        for t in self.fig.findobj(matplotlib.text.Text):
            if not t.get_visible() or not t.get_text().strip() or t in hidden: continue
            b = t.get_window_extent(r)
            if b.width == 0 or b.height == 0: continue
            assert b.x0 >= -1 and b.y0 >= -1 and b.x1 <= W + 1 and b.y1 <= H + 1, f'text off page: {t.get_text()!r}'
            boxes.append((t, b))
        bad = []
        for i, (t1, b1) in enumerate(boxes):
            for t2, b2 in boxes[i + 1:]:
                if t1.get_text() == t2.get_text(): continue
                if b1.x0 < b2.x1 - 1 and b2.x0 < b1.x1 - 1 and b1.y0 < b2.y1 - 1 and b2.y0 < b1.y1 - 1:
                    bad.append((t1.get_text(), t2.get_text()))
        if bad: print('OVERLAP', bad)
        STRICT and (not bad or (_ for _ in ()).throw(AssertionError(f'overlapping text: {bad}')))


# =========================================================================================== Fig. 1
def fig1():
    man = json.loads((FIG1 / 'manifest.json').read_text())
    assert man['network_id'] == 5000 and man['selected_nodes'] == [6, 8, 11]
    rec, stim, readout = man['selected_nodes'], man['stim'], man['readout']
    assert (stim, readout) == (0, 4)
    Q_PAPER = 2.43518e-4

    J = np.zeros((12, 12))
    for r in rows('weights.csv', FIG1): J[int(r['postsynaptic_node']), int(r['presynaptic_node'])] = float(r['weight'])
    assert len(rows('weights.csv', FIG1)) == 144
    npz = V3_OVERVIEW / 'source_arrays.npz'
    if npz.exists(): assert np.array_equal(np.load(npz)['J'], J)
    vmax = np.abs(J).max()
    assert round(vmax, 2) == .42 and (J > 0).any() and (J < 0).any()

    obs = rows('calibration_observations.csv', FIG1X)
    assert len(obs) == 180
    resp = rows('heldout_response.csv', FIG1X)
    assert len(resp) == 120
    t = np.array([float(r['time_model_units']) for r in resp])
    delta = np.array([float(r['difference_rate_au']) for r in resp])
    stimv = np.array([float(r['stimulus_input']) for r in resp])
    dt = .05
    assert np.allclose(np.diff(t), dt) and all(int(r['readout_node']) == readout for r in resp)
    assert np.allclose(delta, [float(r['stimulated_rate_au']) - float(r['control_rate_au']) for r in resp], atol=1e-15)
    q = dt * delta.sum()
    assert abs(q - man['q_rebuilt']) < 1e-15 and abs(q - man['q_csv']) < 1e-15
    assert f'{q / 1e-4:.5f}' == '2.43518' and abs(q - Q_PAPER) < 5e-10
    assert set(stimv) == {0., .6} and t[stimv > 0].min() == 1.0 and t[stimv > 0].max() < 2.0

    W, H = 180, 122
    P = Page(W, H)

    # ---------------- panel a: known signed connectivity -------------------
    P.label(3, H - 4, 'a'); P.T(9, H - 4, 'Known signed connectivity', fontsize=7)
    P.T(9, H - 8.6, 'Network J5000: columns presynaptic, rows postsynaptic', fontsize=6.6, color=MUTED)
    hx, hy, hs = 14, 56, 48            # heat-map left, bottom, side (mm)
    ax = P.ax(hx, hy, hs, hs)
    cmap = LinearSegmentedColormap.from_list('signed', [NEG, '#FFFFFF', POS])
    edges = np.arange(13) - .5
    ax.pcolormesh(edges, edges, J, cmap=cmap, norm=TwoSlopeNorm(0, -vmax, vmax), shading='flat',
                  edgecolors='#E9E5E8', linewidth=.3)
    ax.set_xlim(-.5, 11.5); ax.set_ylim(11.5, -.5); ax.set_aspect('equal')
    ax.set_xticks([0, 3, 6, 9, 11]); ax.set_yticks([0, 3, 6, 9, 11])
    ax.tick_params(length=2.5, pad=2, labelsize=6.5)
    ax.set_xlabel('Presynaptic node', fontsize=6.5, labelpad=2); ax.set_ylabel('Postsynaptic node', fontsize=6.5, labelpad=2)
    for s in ('left', 'bottom'): ax.spines[s].set_visible(True)
    cell = hs / 12
    ytop = hy + hs
    def rowy(i): return ytop - (i + .5) * cell
    # recorded rows (filled ultramarine), readout row (vermilion ring); stimulated column 0 (plum ring)
    for n in rec:
        P.base.add_patch(Circle((hx + hs + 3.0, rowy(n)), 1.45, fc=SCALAR, ec='white', lw=.6, zorder=4))
        P.T(hx + hs + 5.6, rowy(n), f'N{n}', fontsize=6.5, color=INK)
    P.base.add_patch(Circle((hx + hs + 3.0, rowy(readout)), 1.45, fc='white', ec=VECTOR, lw=1.2, zorder=4))
    P.T(hx + hs + 5.6, rowy(readout), f'N{readout}', fontsize=6.5, color=INK)
    P.base.add_patch(Circle((hx + .5 * cell, ytop + 3.0), 1.45, fc='white', ec=FORECAST, lw=1.2, zorder=4))
    P.T(hx + .5 * cell + 3.0, ytop + 3.0, f'N{stim}', fontsize=6.5, color=INK)
    # colour bar
    cx, cy, cw, ch = hx, 37.0, hs, 2.4
    cb = P.ax(cx, cy, cw, ch)
    grad = np.linspace(-vmax, vmax, 256)[None, :]
    cb.imshow(grad, aspect='auto', cmap=cmap, norm=TwoSlopeNorm(0, -vmax, vmax), extent=[-vmax, vmax, 0, 1])
    cb.set_yticks([]); cb.set_xticks([-vmax, 0, vmax])
    cb.xaxis.set_major_formatter(FuncFormatter(lambda v, _: (('+' if v > 0 else '') + f'{abs(v):.2f}' if v >= 0 else MINUS + f'{abs(v):.2f}')))
    cb.tick_params(length=2, pad=1.5, labelsize=6.5)
    for s in cb.spines.values(): s.set_visible(True); s.set_linewidth(.4)
    P.T(cx + cw / 2, 29.4, 'Connection weight (a.u.): negative to positive', fontsize=6.5, ha='center')
    # key
    kx, ky = 9, 21.0
    keys = [('rec', f'recorded nodes N{rec[0]}, N{rec[1]}, N{rec[2]}  (calibration data)'),
            ('stim', f'stimulated node N{stim}  (input during t = 1 to 2)'),
            ('read', f'readout N{readout}  (not recorded)')]
    for k, (kind, lab) in enumerate(keys):
        y = ky - 4.4 * k
        if kind == 'rec': P.base.add_patch(Circle((kx, y), 1.45, fc=SCALAR, ec='white', lw=.6))
        elif kind == 'stim': P.base.add_patch(Circle((kx, y), 1.45, fc='white', ec=FORECAST, lw=1.2))
        else: P.base.add_patch(Circle((kx, y), 1.45, fc='white', ec=VECTOR, lw=1.2))
        P.T(kx + 3.4, y, lab, fontsize=6.6)

    # ---------------- panel b: calibration observations ---------------------
    bx, bw = 100, 76
    P.label(84, H - 4, 'b'); P.T(90, H - 4, 'Calibration at recorded nodes', fontsize=7)
    P.T(90, H - 8.6, 'Noisy rates (a.u.), two trials from the same initial state',
        fontsize=6.6, color=MUTED)
    bh, gap, btop = 11.2, 2.0, H - 17
    axb = []
    for j, n in enumerate(rec):
        a = P.ax(bx, btop - bh - j * (bh + gap), bw, bh); axb.append(a)
        for trial in (1, 2):
            rr = [r for r in obs if int(r['node']) == n and int(r['trial']) == trial]
            assert len(rr) == 30
            x = np.array([float(r['time_model_units']) for r in rr]) + (trial - 1) * 6
            y = np.array([float(r['observed_rate_au']) for r in rr])
            a.plot(x, y, '-o', color=SCALAR, lw=.7, ms=2.4, mew=0)
        a.axvline(6, color=GREY, lw=.7, ls=(0, (2, 2)))
        a.set_xlim(-.15, 11.95); a.yaxis.set_major_locator(MaxNLocator(nbins=3))
        P.T(88, btop - bh / 2 - j * (bh + gap), f'N{n}', ha='left', fontsize=7, color=INK)
        a.tick_params(length=2.5, pad=2, labelsize=6.5)
        if j < 2: a.tick_params(labelbottom=False)
        else:
            a.set_xticks([0, 3, 6, 9, 12]); a.set_xlabel('Calibration time (model units; trial 2 shifted by 6)', fontsize=6.5, labelpad=2)
    P.T(bx + bw * (3 / 12.1), btop + 2.4, 'Trial 1', fontsize=7, color=MUTED, ha='center')
    P.T(bx + bw * (9 / 12.1), btop + 2.4, 'Trial 2', fontsize=7, color=MUTED, ha='center')

    # ---------------- panel c: held-out stimulated-minus-control response ----
    P.label(84, 54.5, 'c')
    P.T(90, 54.5, f'Held-out response at N{readout}', fontsize=7)
    sx, sw = bx, bw
    st = P.ax(sx, 42.0, sw, 5.4)
    st.step(t, stimv, where='post', color=FORECAST, lw=1.1)
    st.fill_between(t, 0, stimv, step='post', color=FORECAST, alpha=.22, lw=0)
    st.set_xlim(0, 6); st.set_ylim(-.12, .85)
    st.set_yticks([0, .6]); st.set_yticklabels(['0', '0.6'], fontsize=6.8); st.tick_params(length=2, pad=1.5)
    st.set_xticks([]); st.spines['bottom'].set_visible(False)
    st.text(2.2, .3, f'stimulus input at N{stim} (a.u.)', fontsize=6.5, color=INK, ha='left', va='center')
    ra = P.ax(sx, 13.5, sw, 26.5)
    scaled = delta * 1e4
    ra.axhline(0, color=GREY, lw=.6)
    # area under the curve = q (dt * sum of differences); fill drawn on the sampled grid
    ra.fill_between(t, 0, scaled, color=FORECAST, alpha=.16, lw=0, step=None)
    ra.plot(t, scaled, color=FORECAST, lw=1.1)
    ra.set_xlim(0, 6); ra.set_xticks([0, 1, 2, 3, 4, 5, 6]); ra.yaxis.set_major_locator(MaxNLocator(nbins=4))
    ra.set_ylim(-.03, scaled.max() * 1.12)
    ra.set_xlabel('Held-out time (model units)', fontsize=6.5, labelpad=2)
    ra.set_ylabel(r'Rate difference ($10^{-4}$ a.u.)', fontsize=6.5, labelpad=3)
    ra.tick_params(length=2.5, pad=2)
    qtxt = rf'q = {q / 1e-4:.5f} $\times$ 10$^{{-4}}$'
    P.T(100, 2.8, qtxt + ' a.u. × model time', fontsize=6.5, color=INK)
    P.T(90, 50.3, 'Stimulated minus control; shaded integral gives q', fontsize=6.5, color=MUTED)
    P.check_text()
    export(P.fig, OUT1 / 'fig2_data_overview')
    return dict(q=q, J=J)



if __name__ == "__main__":
    fig1()
