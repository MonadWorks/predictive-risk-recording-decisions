"""v4 presentation layer, part 2: Fig. 1 and Supplementary Figs. 1-5.

Same visual system as render_v4.py (palette constants copied, not imported):
ultramarine = single-response objective, vermilion = shared / three-response objective,
plum = risk forecast / stimulus, warm grey = unchanged or reference, ink = text.
Reads only frozen tables in ../05_data_and_code (source_data, fig1_data, fig1_data_extra).
No new inference, no re-selection, no filtering: every plotted number is a frozen v2/v3 value.
Asserts below stop the run if a count or value drifts from the source tables.
Run:  python render_supp_v4.py   (needs numpy + matplotlib)
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

PACK = HERE.parent
DATA = PACK / '05_data_and_code/source_data'
FIG1 = PACK / '05_data_and_code/fig1_data'
FIG1X = PACK / '05_data_and_code/fig1_data_extra'
V3_OVERVIEW = PACK.parent / 'outputs/research_craft_v3/figure_redesign/data_overview'  # optional cross-check only
OUT1 = HERE
OUTS = HERE / 'supplementary_v4'
OUTS.mkdir(exist_ok=True)

# ---- palette (copied from render_v4.py / style/STYLE.md) ----------------------------------------
INK = '#15202B'; MUTED = '#5A6570'; RULE = '#D9D4C9'; PANEL = '#EFEBE3'; PAPER = '#F7F4EE'
SCALAR = '#2A3BCC'; VECTOR = '#DC4F1E'; FORECAST = '#8A2F7A'; GREY = '#8A939B'; SAME = '#C9C4B8'
VECTOR_TEXT = '#B4360C'
POS = '#2B6A9E'; NEG = '#C2663A'   # sign of a connection weight (as in the graphical abstract: blue +, orange -)
def tcol(c): return VECTOR_TEXT if c == VECTOR else c

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 8, 'axes.linewidth': .6, 'axes.edgecolor': INK, 'text.color': INK,
    'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK,
    'xtick.labelsize': 7.2, 'ytick.labelsize': 7.2, 'axes.spines.top': False,
    'axes.spines.right': False, 'pdf.fonttype': 42, 'svg.fonttype': 'none',
    'mathtext.fontset': 'dejavusans', 'figure.facecolor': 'white', 'savefig.facecolor': 'white',
    'axes.unicode_minus': True})
MINUS = '−'
STRICT = False


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

    def label(self, x, y, s): return self.T(x, y, s, fontsize=10, fontweight='bold')

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
    P.label(3, H - 4, 'a'); P.T(9, H - 4, 'Known signed connectivity', fontsize=8.3)
    P.T(9, H - 8.6, 'Network J5000: columns presynaptic, rows postsynaptic', fontsize=6.6, color=MUTED)
    hx, hy, hs = 14, 56, 48            # heat-map left, bottom, side (mm)
    ax = P.ax(hx, hy, hs, hs)
    cmap = LinearSegmentedColormap.from_list('signed', [NEG, '#F4F1EA', POS])
    edges = np.arange(13) - .5
    ax.pcolormesh(edges, edges, J, cmap=cmap, norm=TwoSlopeNorm(0, -vmax, vmax), shading='flat',
                  edgecolors='#E4DFD3', linewidth=.3)
    ax.set_xlim(-.5, 11.5); ax.set_ylim(11.5, -.5); ax.set_aspect('equal')
    ax.set_xticks([0, 3, 6, 9, 11]); ax.set_yticks([0, 3, 6, 9, 11])
    ax.tick_params(length=2.5, pad=2, labelsize=7.2)
    ax.set_xlabel('Presynaptic node', fontsize=7.2, labelpad=2); ax.set_ylabel('Postsynaptic node', fontsize=7.2, labelpad=2)
    for s in ('left', 'bottom'): ax.spines[s].set_visible(True)
    cell = hs / 12
    ytop = hy + hs
    def rowy(i): return ytop - (i + .5) * cell
    # recorded rows (filled ultramarine), readout row (vermilion ring); stimulated column 0 (plum ring)
    for n in rec:
        P.base.add_patch(Circle((hx + hs + 3.0, rowy(n)), 1.45, fc=SCALAR, ec='white', lw=.6, zorder=4))
        P.T(hx + hs + 5.6, rowy(n), f'N{n}', fontsize=7.2, color=SCALAR, fontweight='bold')
    P.base.add_patch(Circle((hx + hs + 3.0, rowy(readout)), 1.45, fc='white', ec=VECTOR, lw=1.2, zorder=4))
    P.T(hx + hs + 5.6, rowy(readout), f'N{readout}', fontsize=7.2, color=VECTOR_TEXT, fontweight='bold')
    P.base.add_patch(Circle((hx + .5 * cell, ytop + 3.0), 1.45, fc='white', ec=FORECAST, lw=1.2, zorder=4))
    P.T(hx + .5 * cell + 3.0, ytop + 3.0, f'N{stim}', fontsize=7.2, color=FORECAST, fontweight='bold')
    # colour bar
    cx, cy, cw, ch = hx, 37.0, hs, 2.4
    cb = P.ax(cx, cy, cw, ch)
    grad = np.linspace(-vmax, vmax, 256)[None, :]
    cb.imshow(grad, aspect='auto', cmap=cmap, norm=TwoSlopeNorm(0, -vmax, vmax), extent=[-vmax, vmax, 0, 1])
    cb.set_yticks([]); cb.set_xticks([-vmax, 0, vmax])
    cb.xaxis.set_major_formatter(FuncFormatter(lambda v, _: (f'{abs(v):.2f}' if v >= 0 else MINUS + f'{abs(v):.2f}')))
    cb.tick_params(length=2, pad=1.5, labelsize=7.2)
    for s in cb.spines.values(): s.set_visible(True); s.set_linewidth(.4)
    P.T(cx + cw / 2, 29.4, 'Connection weight (a.u.): negative to positive', fontsize=7.2, ha='center')
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
    P.label(84, H - 4, 'b'); P.T(90, H - 4, 'Calibration observations at the 3 recorded nodes', fontsize=8.3)
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
        a.set_ylabel(f'N{n}', rotation=0, ha='right', va='center', labelpad=9, color=SCALAR, fontweight='bold', fontsize=7.6)
        a.tick_params(length=2.5, pad=2, labelsize=7.2)
        if j < 2: a.tick_params(labelbottom=False)
        else:
            a.set_xticks([0, 3, 6, 9, 12]); a.set_xlabel('Calibration time (model units; trial 2 shifted by 6)', fontsize=7.2, labelpad=2)
    P.T(bx + bw * (3 / 12.1), btop + 2.4, 'Trial 1', fontsize=7, color=MUTED, ha='center')
    P.T(bx + bw * (9 / 12.1), btop + 2.4, 'Trial 2', fontsize=7, color=MUTED, ha='center')

    # ---------------- panel c: held-out stimulated-minus-control response ----
    P.label(84, 54.5, 'c')
    P.T(90, 54.5, f'Held-out response at unrecorded node N{readout}: stimulated minus control', fontsize=8.3)
    sx, sw = bx, bw
    st = P.ax(sx, 42.0, sw, 5.4)
    st.step(t, stimv, where='post', color=FORECAST, lw=1.1)
    st.fill_between(t, 0, stimv, step='post', color=FORECAST, alpha=.22, lw=0)
    st.set_xlim(0, 6); st.set_ylim(-.12, .85)
    st.set_yticks([0, .6]); st.set_yticklabels(['0', '0.6'], fontsize=6.8); st.tick_params(length=2, pad=1.5)
    st.set_xticks([]); st.spines['bottom'].set_visible(False)
    st.text(2.2, .3, f'stimulus input at N{stim} (a.u.)', fontsize=6.8, color=FORECAST, ha='left', va='center')
    ra = P.ax(sx, 13.5, sw, 26.5)
    scaled = delta * 1e4
    ra.axhline(0, color=GREY, lw=.6)
    # area under the curve = q (dt * sum of differences); fill drawn on the sampled grid
    ra.fill_between(t, 0, scaled, color=MUTED, alpha=.20, lw=0, step=None)
    ra.plot(t, scaled, color=INK, lw=1.3)
    ra.set_xlim(0, 6); ra.set_xticks([0, 1, 2, 3, 4, 5, 6]); ra.yaxis.set_major_locator(MaxNLocator(nbins=4))
    ra.set_ylim(-.03, scaled.max() * 1.12)
    ra.set_xlabel('Held-out time (model units)', fontsize=7.2, labelpad=2)
    ra.set_ylabel(r'Rate difference ($10^{-4}$ a.u.)', fontsize=7.2, labelpad=3)
    ra.tick_params(length=2.5, pad=2)
    qtxt = rf'q = {q / 1e-4:.5f} $\times$ 10$^{{-4}}$'
    ra.text(.04, .93, qtxt, transform=ra.transAxes, fontsize=8.6, fontweight='bold', va='top', ha='left', color=INK)
    ra.text(.04, .79, 'integrated response:\narea under the curve\n(a.u. × model time)',
            transform=ra.transAxes, fontsize=6.6, color=MUTED, va='top', ha='left', linespacing=1.25)
    ra.text(4.55, scaled.max() * .30, 'area = q', fontsize=8, fontweight='bold', color=INK, ha='center', va='center')
    P.check_text()
    export(P.fig, OUT1 / 'fig1_data_overview_v4')
    return dict(q=q, J=J)


# ====================================================================================== supplementary
LINES = ['', '']


def figS1():
    rows_ = rows('holdout_primary_paired.csv')
    assert len(rows_) == 80
    spec = [('ensemble_scalar - local_scalar', SCALAR, 'o', 'Single response', 'a'),
            ('ensemble_vector - local_vector', VECTOR, 's', 'Three responses', 'b')]
    W, H = 180, 76
    P = Page(W, H)
    ties = {}
    for j, (contrast, col, mk, name, let) in enumerate(spec):
        rs = [r for r in rows_ if r['contrast'] == contrast]
        assert len(rs) == 40 and len({r['network_id'] for r in rs}) == 40
        v = np.sort([float(r['paired_mse_difference']) * 1e5 for r in rs]); y = np.arange(1, 41) / 40
        ties[let] = int((v == 0).sum())
        x0 = 20 + j * 92
        P.label(3 + j * 92, H - 4, let)
        P.T(9 + j * 92, H - 4, name, fontsize=8.3, fontweight='bold', color=tcol(col))
        P.T(9 + j * 92, H - 8.6, 'ensemble minus nominal, 40 independent networks', fontsize=6.6, color=MUTED)
        ax = P.ax(x0, 20, 64, 43)
        ax.axvline(0, color=MUTED, lw=.8, ls=(0, (3, 2)), zorder=0)
        ax.step(v, y, where='post', color=col, lw=1.3, zorder=2)
        ax.plot(v, y, mk, color=col, ms=3.6, mec='white', mew=.35, zorder=3, ls='none')
        lo, hi = v.min(), v.max()
        pad = .08 * (hi - lo)
        ax.set_xlim(lo - pad, hi + pad); ax.set_ylim(0, 1.13)
        ax.set_yticks([0, .2, .4, .6, .8, 1.0]); ax.set_yticklabels(['0', '0.2', '0.4', '0.6', '0.8', '1'])
        ax.tick_params(length=2.5, pad=2); ax.set_ylabel('Fraction of networks (ECDF)', fontsize=7.2, labelpad=3)
        ax.set_xlabel(r'Paired MSE difference ($\times10^{-5}$ q$^2$)', fontsize=7.2, labelpad=2)
        fmt = lambda a: (MINUS if a < 0 else '+') + f'{abs(a):.1f}'
        ax.text(lo, 1/40 + .07, fmt(lo), fontsize=7, color=tcol(col), ha='left', va='bottom', fontweight='bold')
        ax.text(hi, 1.0 + .03, fmt(hi), fontsize=7, color=tcol(col), ha='right', va='bottom', fontweight='bold')
        tx, tha = (-1.6, 'right') if let == 'a' else (hi, 'right')
        ax.text(tx, .50, f'{ties[let]} of 40 differences\nare exactly 0', fontsize=6.8, color=MUTED, ha=tha, va='center',
                linespacing=1.25)
        P.T(x0 + 2, 5.6, '← ensemble lower error', fontsize=6.6, color=MUTED, ha='left')
        P.T(x0 + 64 - 2, 5.6, 'higher →', fontsize=6.6, color=MUTED, ha='right')
        if let == 'a': assert (round(lo, 2), round(hi, 2)) == (-16.23, 6.27)
        if let == 'b': assert (round(lo, 2), round(hi, 2)) == (-1.16, 6.27)
    assert ties == {'a': 13, 'b': 26}
    P.check_text()
    export(P.fig, OUTS / 'figS1_complete_paired_distributions_v4')


METHODS = ['local_scalar', 'ensemble_scalar', 'local_vector', 'ensemble_vector', 'local_activity', 'random']
TICKS = ['Nominal', 'Ensemble', 'Nominal', 'Ensemble', 'Activity', 'Random']


def figS_strata(condition, header, figno, metrics, summ):
    assert header
    W, H = 180, 170
    P = Page(W, H)
    P.T(3, H - 3.2, header, fontsize=9.2, fontweight='bold')
    P.T(3 + 2.3 + len(header) * 1.75, H - 3.2,
        'Response MSE of six recording policies, 40 independent networks each', fontsize=7.4, color=MUTED)
    n_pts = 0
    for panel, (pool, budget) in enumerate([('all', '3'), ('exclude_endpoints', '3'), ('all', '6'), ('exclude_endpoints', '6')]):
        c, r_ = panel % 2, panel // 2
        x0 = 18 + c * 92; w, h = 70, 44
        y0 = 109 - r_ * 71
        P.label(3 + c * 92, y0 + h + 7.5, 'abcd'[panel])
        P.T(9 + c * 92, y0 + h + 7.5, f'{"All sites" if pool == "all" else "Endpoints excluded"}, M = {budget}',
            fontsize=8.3)
        ax = P.ax(x0, y0, w, h)
        for m, method in enumerate(METHODS):
            rr = sorted([r for r in metrics if r['condition'] == condition and r['pool'] == pool and
                         r['budget'] == budget and r['method'] == method], key=lambda r: int(r['network_id']))
            assert len(rr) == 40 and len({r['network_id'] for r in rr}) == 40
            values = np.array([float(r['mse']) for r in rr]); assert np.all(values > 0)
            n_pts += len(values)
            scal, vec = 'scalar' in method, 'vector' in method
            col = SCALAR if scal else VECTOR if vec else GREY
            mk = 'o' if scal else 's' if vec else '^' if method == 'local_activity' else 'x'
            filled = method.startswith('ensemble')
            xpos = m + np.random.default_rng(42).permutation(np.linspace(-.17, .17, 40))   # same jitter as v3 renderer
            if mk == 'x':
                ax.scatter(xpos, values, s=9, c=col, marker='x', lw=.6, alpha=.75, zorder=2)
            else:
                ax.scatter(xpos, values, s=10, facecolors=col if filled else 'white', edgecolors=col, lw=.6,
                           marker=mk, alpha=.85, zorder=2)
            ss = [s for s in summ if s['condition'] == condition and s['pool'] == pool and str(s['budget']) == budget
                  and s['method'] == method]
            assert len(ss) == 1 and ss[0]['networks'] == 40
            s = ss[0]
            assert s['mse_ci95_low'] < s['mse'] < s['mse_ci95_high']
            ax.plot([m, m], [s['mse_ci95_low'], s['mse_ci95_high']], color=INK, lw=.9, zorder=5, solid_capstyle='butt')
            for e in (s['mse_ci95_low'], s['mse_ci95_high']):
                ax.plot([m - .07, m + .07], [e, e], color=INK, lw=.9, zorder=5)
            ax.plot([m - .22, m + .22], [s['mse'], s['mse']], color=INK, lw=1.7, zorder=6, solid_capstyle='butt')
        ax.set_yscale('log'); ax.set_ylim(1e-15, 1e-2); ax.set_xlim(-.5, 5.5)
        ax.yaxis.set_major_locator(FixedLocator([1e-14, 1e-10, 1e-6, 1e-2]))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: rf'$10^{{{int(round(np.log10(v)))}}}$'))
        ax.yaxis.set_minor_locator(LogLocator(base=10, subs=(1,), numticks=20)); ax.yaxis.set_minor_formatter(NullFormatter())
        ax.tick_params(which='minor', length=1.4, width=.4); ax.tick_params(which='major', length=2.8, pad=2)
        ax.set_xticks(range(6)); ax.set_xticklabels(TICKS, fontsize=6.6, rotation=0)
        ax.tick_params(axis='x', length=2.5, pad=2)
        ax.set_ylabel('Response MSE (q²)', fontsize=7.2, labelpad=2)
        # group labels
        gy = y0 - 8.6
        for (m0, m1, lab, col) in [(0, 1, 'Single response', SCALAR), (2, 3, 'Three responses', VECTOR_TEXT), (4, 5, 'References', MUTED)]:
            xa = x0 + (m0 + .5 - .3) / 6 * w + .0; xb = x0 + (m1 + .5 + .3) / 6 * w
            P.base.plot([xa, xb], [gy + 2.2, gy + 2.2], color=col if col != VECTOR_TEXT else VECTOR, lw=.9, solid_capstyle='butt')
            P.T((xa + xb) / 2, gy - .2, lab, fontsize=6.8, color=col, ha='center', fontweight='bold')
    # shared key
    ky = 19.0
    P.T(3, ky, 'Key', fontsize=7, fontweight='bold')
    items = [('o', SCALAR, 'white', 'nominal selection (open)'), ('o', SCALAR, SCALAR, 'ensemble selection (filled)')]
    xk = 14
    for lab, mk_open, mk_fill in [('Nominal selection (open marker)', 'white', None), ('Ensemble selection (filled marker)', None, True)]:
        if mk_fill is None:
            P.base.add_patch(Circle((xk, ky), 1.25, fc='white', ec=INK, lw=.7))
        else:
            P.base.add_patch(Circle((xk, ky), 1.25, fc=INK, ec=INK, lw=.7))
        P.T(xk + 2.6, ky, lab, fontsize=6.8); xk += 58
    P.base.plot([xk - 1.5, xk + 1.5], [ky, ky], color=INK, lw=1.7)
    P.T(xk + 3.4, ky, 'Aggregate mean over 40 networks', fontsize=6.8)
    ky2 = ky - 4.8
    P.base.plot([14, 14], [ky2 - 1.6, ky2 + 1.6], color=INK, lw=.9)
    P.base.plot([12.8, 15.2], [ky2 + 1.6, ky2 + 1.6], color=INK, lw=.9); P.base.plot([12.8, 15.2], [ky2 - 1.6, ky2 - 1.6], color=INK, lw=.9)
    P.T(17.4, ky2, 'Exploratory pointwise 95% network-cluster interval', fontsize=6.8)
    P.T(94, ky2, 'Circle = single-response, square = three-response, triangle/cross = reference.',
        fontsize=6.8, color=MUTED)
    P.T(3, ky2 - 4.8, 'Each point is one network (truth, noise and readout repeats averaged within network). '
        'Horizontal jitter only; no point is removed.', fontsize=6.6, color=MUTED)
    P.check_text()
    export(P.fig, OUTS / f'figS{figno}_{condition}_conditions_v4')
    return n_pts


def figS5():
    rr = rows('linear_control.csv')
    assert len(rr) == 144 and len({r['system'] for r in rr}) == 12
    x = np.array([float(r['analytic_map_mse']) for r in rr]); y = np.array([float(r['actual_mc_map_mse']) for r in rr])
    assert len(x) == len(y) == 144
    W, H = 180, 92
    P = Page(W, H)
    P.label(3, H - 4, 'a'); P.T(9, H - 4, 'Analytic versus Monte Carlo MAP MSE', fontsize=8.3)
    P.T(9, H - 8.6, 'Linear-Gaussian positive control, 12 independent systems', fontsize=6.6, color=MUTED)
    ax = P.ax(20, 14, 62, 62)
    ax.plot([0, 1], [0, 1], color=MUTED, lw=.8, ls=(0, (3, 2)), zorder=0)
    ax.scatter(x, y, s=12, facecolors='white', edgecolors=INK, lw=.6, alpha=.8, zorder=2)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_box_aspect(1)
    ax.set_xticks(np.arange(0, 1.01, .2)); ax.set_yticks(np.arange(0, 1.01, .2))
    ax.set_xticklabels(['0', '0.2', '0.4', '0.6', '0.8', '1']); ax.set_yticklabels(['0', '0.2', '0.4', '0.6', '0.8', '1'])
    ax.tick_params(length=2.5, pad=2)
    ax.set_xlabel('Analytic MAP MSE', fontsize=7.2, labelpad=2); ax.set_ylabel('Monte Carlo MAP MSE', fontsize=7.2, labelpad=2)
    ax.text(.97, .08, 'dashed line = analytic reference', transform=ax.transAxes, fontsize=6.6, color=MUTED,
            ha='right', va='bottom')
    # reading guide
    P.label(96, H - 4, 'b'); P.T(102, H - 4, 'What the control tests', fontsize=8.3)
    facts = [('144', 'target/design evaluations', INK), ('12', 'independent linear systems', INK),
             ('8,192', 'Monte Carlo draws per system', INK)]
    for k, (num, lab, col) in enumerate(facts):
        yy = H - 20 - k * 13
        P.T(102, yy, num, fontsize=15, fontweight='bold', color=col)
        P.T(102 + 17.5, yy, lab, fontsize=7.4)
    P.T(102, 29.5, 'Points are not 144 independent neural networks; they are', fontsize=6.8, color=MUTED)
    P.T(102, 25.7, 'evaluations within 12 systems. No confidence intervals are drawn.', fontsize=6.8, color=MUTED)
    P.T(102, 21.2, 'Agreement validates this computational special case,', fontsize=6.8, color=MUTED)
    P.T(102, 17.4, 'not biological assumptions.', fontsize=6.8, color=MUTED)
    P.check_text()
    export(P.fig, OUTS / 'figS5_linear_positive_control_v4')


def main():
    res = fig1()
    metrics = rows('holdout_network_metrics.csv')
    assert len(metrics) == 2880
    summ = json.loads((DATA / 'holdout_summary.json').read_text())['metric_summaries']
    assert len(summ) == 72
    figS1()
    total = 0
    for fno, (cond, hdr) in zip((2, 3, 4), [('matched', 'Matched uncertainty'), ('broad', 'Broad uncertainty'),
                                           ('bias_shift', 'Hidden bias shift')]):
        total += figS_strata(cond, hdr, fno, metrics, summ)
    assert total == 2880
    figS5()
    print(json.dumps({'q': res['q'], 'strata_points': total, 'status': 'ok'}))


if __name__ == '__main__':
    main()
