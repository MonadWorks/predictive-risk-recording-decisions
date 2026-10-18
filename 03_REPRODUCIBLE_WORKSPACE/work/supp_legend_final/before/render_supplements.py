"""Pink supplementary presentation only; adapted locally from the historical v4 renderer.
Reads frozen CSV/JSON; no model fitting, no CI recalculation, no selection changes.
The historical data assertions and plotting arrays are preserved.
"""
import csv, json, os
from pathlib import Path
os.environ.setdefault('MPLBACKEND', 'Agg')
HERE = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(HERE.parents[1] / 'work/pastel-cache'))
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import Circle
from matplotlib.ticker import FuncFormatter, MaxNLocator, LogLocator, NullFormatter, FixedLocator

PACK = HERE.parents[1] / 'work/evidence/ICBR2026_v4_pack'
DATA = PACK / '05_data_and_code/source_data'
FIG1 = PACK / '05_data_and_code/fig1_data'
FIG1X = PACK / '05_data_and_code/fig1_data_extra'
V3_OVERVIEW = PACK.parent / 'outputs/research_craft_v3/figure_redesign/data_overview'  # optional cross-check only
OUT1 = HERE
OUTS = HERE / 'supplementary'
OUTS.mkdir(exist_ok=True)

# ---- fonts: BentonSans text, Times New Roman math, JuliaMono numeric callouts --------------------
import matplotlib.font_manager as fm
for _f in (HERE / 'fonts').glob('*.ttf'):
    fm.fontManager.addfont(str(_f))
for _n in ('Times New Roman', 'Times New Roman Bold', 'Times New Roman Italic', 'Times New Roman Bold Italic'):
    _p = Path('/System/Library/Fonts/Supplemental') / f'{_n}.ttf'
    if _p.exists(): fm.fontManager.addfont(str(_p))

# ---- palette: pastel rose primary + sunflower amber complement -----------------------------------
INK = '#2E2531'; MUTED = '#7D7280'; RULE = '#EBDCE4'; PANEL = '#FDF4F8'; PAPER = '#FFFFFF'
SCALAR = '#E27A9E'; VECTOR = '#F4BFD0'; FORECAST = '#EDAF26'; FORECAST_LINE = '#DB9A1D'; GREY = '#B9AEB7'; SAME = '#DAD4D8'
VECTOR_EDGE = '#B5708C'
VECTOR_TEXT = '#2E2531'
AXIS_TEXT = '#49424B'; TICK_TEXT = '#6B626D'
POS = '#C25E88'; NEG = '#4E4350'   # connection-weight sign: rose positive, deep plum negative
def tcol(c): return INK

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['BentonSans', 'JuliaMono', 'DejaVu Sans'],
    'font.size': 6, 'axes.linewidth': .6, 'axes.edgecolor': INK, 'text.color': INK,
    'axes.labelcolor': AXIS_TEXT, 'xtick.color': TICK_TEXT, 'ytick.color': TICK_TEXT,
    'xtick.labelsize': 6.3, 'ytick.labelsize': 6.3, 'axes.spines.top': False,
    'axes.spines.right': False, 'pdf.fonttype': 42, 'svg.fonttype': 'none',
    'mathtext.fontset': 'custom', 'mathtext.rm': 'Times New Roman', 'mathtext.it': 'Times New Roman:italic', 'mathtext.bf': 'Times New Roman:bold', 'figure.facecolor': 'white', 'savefig.facecolor': 'white',
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
        size = k.get('fontsize', 6)
        if size >= 7:
            k.update(fontsize=size, fontweight='bold', color=INK)
        elif size == 6.5:
            k.update(fontsize=6.5, fontweight='normal', color=INK)
        else:
            k.update(fontsize=6, fontweight='normal', color=MUTED)
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
        P.T(9 + j * 92, H - 4, name, fontsize=7, fontweight='bold', color=tcol(col))
        P.T(9 + j * 92, H - 8.6, 'Ensemble minus nominal; 40 independent networks', fontsize=6.6, color=MUTED)
        ax = P.ax(x0, 20, 64, 43)
        ax.axvline(0, color=MUTED, lw=.8, ls=(0, (3, 2)), zorder=0)
        ax.step(v, y, where='post', color=col, lw=1.3, zorder=2)
        ax.plot(v, y, mk, color=col, ms=3.6, mec=VECTOR_EDGE if col == VECTOR else 'white', mew=.45, zorder=3, ls='none')
        lo, hi = v.min(), v.max()
        pad = .08 * (hi - lo)
        ax.set_xlim(lo - pad, hi + pad); ax.set_ylim(0, 1.13)
        ax.set_yticks([0, .2, .4, .6, .8, 1.0]); ax.set_yticklabels(['0', '0.2', '0.4', '0.6', '0.8', '1'])
        ax.tick_params(length=2.5, pad=2); ax.set_ylabel('Fraction of networks (ECDF)', fontsize=7, labelpad=3)
        ax.set_xlabel(r'Paired MSE difference ($\times10^{-5}$ q$^2$)', fontsize=7, labelpad=2)
        fmt = lambda a: (MINUS if a < 0 else '+') + f'{abs(a):.1f}'
        ax.text(lo, 1/40 + .07, fmt(lo), fontsize=6.5, color=INK, ha='left', va='bottom', fontweight='normal', fontfamily='JuliaMono')
        ax.text(hi, 1.0 + .03, fmt(hi), fontsize=6.5, color=INK, ha='right', va='bottom', fontweight='normal', fontfamily='JuliaMono')
        tx, tha = (-1.6, 'right') if let == 'a' else (hi, 'right')
        ax.text(tx, .50, f'{ties[let]}/40 differences\nexactly zero', fontsize=6, color=MUTED, ha=tha, va='center',
                linespacing=1.25)
        P.base.annotate('', xy=(x0 + 2, 5.6), xytext=(x0 + 5.0, 5.6),
                        arrowprops=dict(arrowstyle='->', color=MUTED, lw=.7, shrinkA=0, shrinkB=0))
        P.T(x0 + 6.0, 5.6, 'ensemble lower error', fontsize=6.6, color=MUTED, ha='left')
        P.T(x0 + 64 - 8.0, 5.6, 'higher', fontsize=6.6, color=MUTED, ha='right')
        P.base.annotate('', xy=(x0 + 64 - 2, 5.6), xytext=(x0 + 64 - 5.0, 5.6),
                        arrowprops=dict(arrowstyle='->', color=MUTED, lw=.7, shrinkA=0, shrinkB=0))
        if let == 'a': assert (round(lo, 2), round(hi, 2)) == (-16.23, 6.27)
        if let == 'b': assert (round(lo, 2), round(hi, 2)) == (-1.16, 6.27)
    assert ties == {'a': 13, 'b': 26}
    P.check_text()
    export(P.fig, OUTS / 'figS1_complete_paired_distributions_pastel')


METHODS = ['local_scalar', 'ensemble_scalar', 'local_vector', 'ensemble_vector', 'local_activity', 'random']
TICKS = ['Nominal', 'Ensemble', 'Nominal', 'Ensemble', 'Activity', 'Random']


def figS_strata(condition, header, figno, metrics, summ):
    assert header
    W, H = 180, 170
    P = Page(W, H)
    P.T(3, H - 3.2, header, fontsize=7, fontweight='bold')
    P.T(44, H - 3.2,
        'Six recording policies; 40 independent networks', fontsize=6.7, color=MUTED)
    n_pts = 0
    for panel, (pool, budget) in enumerate([('all', '3'), ('exclude_endpoints', '3'), ('all', '6'), ('exclude_endpoints', '6')]):
        c, r_ = panel % 2, panel // 2
        x0 = 18 + c * 92; w, h = 68, 44
        y0 = 109 - r_ * 71
        P.label(3 + c * 92, y0 + h + 7.5, 'abcd'[panel])
        P.T(9 + c * 92, y0 + h + 7.5, f'{"All sites" if pool == "all" else "Endpoints excluded"}, M = {budget}',
            fontsize=7)
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
                ax.scatter(xpos, values, s=10, facecolors=col if filled else 'white', edgecolors=VECTOR_EDGE if vec else col, lw=.6,
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
        ax.set_xticks(range(6)); ax.set_xticklabels(TICKS, fontsize=6.3, rotation=0)
        ax.tick_params(axis='x', length=2.5, pad=2)
        ax.set_ylabel('Response MSE (q²)', fontsize=7, labelpad=2)
        # group labels
        gy = y0 - 8.6
        for (m0, m1, lab, col) in [(0, 1, 'Single response', SCALAR), (2, 3, 'Three responses', VECTOR), (4, 5, 'References', MUTED)]:
            xa = x0 + (m0 + .5 - .3) / 6 * w + .0; xb = x0 + (m1 + .5 + .3) / 6 * w
            P.base.plot([xa, xb], [gy + 2.2, gy + 2.2], color=col if col != VECTOR_TEXT else VECTOR, lw=.9, solid_capstyle='butt')
            P.T((xa + xb) / 2, gy - .2, lab, fontsize=6.8, color=INK, ha='center', fontweight='bold')
    # shared key
    ky = 19.0
    P.T(3, ky, 'Key', fontsize=7, fontweight='bold')
    items = [('o', SCALAR, 'white', 'nominal selection (open)'), ('o', SCALAR, SCALAR, 'ensemble selection (filled)')]
    xk = 14
    for lab, mk_open, mk_fill in [('Nominal (open)', 'white', None), ('Ensemble (filled)', None, True)]:
        if mk_fill is None:
            P.base.add_patch(Circle((xk, ky), 1.25, fc='white', ec=INK, lw=.7))
        else:
            P.base.add_patch(Circle((xk, ky), 1.25, fc=INK, ec=INK, lw=.7))
        P.T(xk + 2.6, ky, lab, fontsize=6.8); xk += 58
    P.base.plot([xk - 1.5, xk + 1.5], [ky, ky], color=INK, lw=1.7)
    P.T(xk + 3.4, ky, 'Mean across networks', fontsize=6.8)
    ky2 = ky - 4.8
    P.base.plot([14, 14], [ky2 - 1.6, ky2 + 1.6], color=INK, lw=.9)
    P.base.plot([12.8, 15.2], [ky2 + 1.6, ky2 + 1.6], color=INK, lw=.9); P.base.plot([12.8, 15.2], [ky2 - 1.6, ky2 - 1.6], color=INK, lw=.9)
    P.T(17.4, ky2, 'Exploratory pointwise 95% network-cluster interval', fontsize=6.8)
    P.T(94, ky2, 'Circle: single response; square: three responses; triangle/cross: references.',
        fontsize=6.8, color=MUTED)
    P.T(3, ky2 - 4.8, 'Each point is one network, averaged over truth, noise and readout repeats. '
        'All 40 networks shown; horizontal jitter only.', fontsize=6.6, color=MUTED)
    P.check_text()
    export(P.fig, OUTS / f'figS{figno}_{condition}_conditions_pastel')
    return n_pts


def figS5():
    rr = rows('linear_control.csv')
    assert len(rr) == 144 and len({r['system'] for r in rr}) == 12
    x = np.array([float(r['analytic_map_mse']) for r in rr]); y = np.array([float(r['actual_mc_map_mse']) for r in rr])
    assert len(x) == len(y) == 144
    W, H = 180, 92
    P = Page(W, H)
    P.label(3, H - 4, 'a'); P.T(9, H - 4, 'Analytic versus Monte Carlo MAP MSE', fontsize=7)
    P.T(9, H - 8.6, 'Linear-Gaussian positive control, 12 independent systems', fontsize=6.6, color=MUTED)
    ax = P.ax(20, 14, 62, 62)
    ax.plot([0, 1], [0, 1], color=MUTED, lw=.8, ls=(0, (3, 2)), zorder=0)
    ax.scatter(x, y, s=12, facecolors='#FBEAF1', edgecolors=SCALAR, lw=.6, alpha=.8, zorder=2)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_box_aspect(1)
    ax.set_xticks(np.arange(0, 1.01, .2)); ax.set_yticks(np.arange(0, 1.01, .2))
    ax.set_xticklabels(['0', '0.2', '0.4', '0.6', '0.8', '1']); ax.set_yticklabels(['0', '0.2', '0.4', '0.6', '0.8', '1'])
    ax.tick_params(length=2.5, pad=2)
    ax.set_xlabel('Analytic MAP MSE', fontsize=7, labelpad=2); ax.set_ylabel('Monte Carlo MAP MSE', fontsize=7, labelpad=2)
    ax.text(.97, .08, 'Dashed line: equality', transform=ax.transAxes, fontsize=6, color=MUTED,
            ha='right', va='bottom')
    # Compact protocol table: labels and counts have common column anchors.
    P.label(96, H - 4, 'b'); P.T(102, H - 4, 'Linear-Gaussian control', fontsize=7)
    facts = [('Independent systems', '12'), ('Target–design evaluations', '144'),
             ('Monte Carlo draws per system', '8,192')]
    for k, (label, value) in enumerate(facts):
        yy = 71 - k * 6
        P.T(102, yy, label, fontsize=6.5)
        tt=P.T(174, yy, value, fontsize=6.5, ha='right')
        tt.set_fontfamily('JuliaMono')
    P.base.plot([102, 174], [76, 76], color=RULE, lw=.6)
    P.base.plot([102, 174], [54, 54], color=RULE, lw=.6)
    P.T(102, 45, 'Numerical agreement', fontsize=6.5)
    P.T(102, 40.5, 'Checks the linear-Gaussian risk calculation', fontsize=6)
    P.T(102, 37, 'and MAP fit; biological validity is not tested.', fontsize=6)
    P.T(102, 25.5, 'The 144 evaluations are nested within 12 systems.', fontsize=6)
    P.T(102, 22, 'No confidence intervals are shown.', fontsize=6)
    P.check_text()
    export(P.fig, OUTS / 'figS5_linear_positive_control_pastel')


def main():
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
    print(json.dumps({'strata_points': total, 'ecdf_points': 80, 'linear_points': 144, 'status': 'ok'}))


if __name__ == '__main__':
    main()
