"""v5 teaser layer (copied constants/data checks from render_v4.py; no new statistics).
Outputs: fig_audit_schematic_v5, graphical_abstract_v5, fig2_recording_decisions_v5, fig3_risk_forecasts_v5.
v4 presentation layer: graphical abstract, Fig. 2 and Fig. 3.

Reads only the frozen tables in ../05_data_and_code. No new inference: every
plotted number is a frozen v2/v3 estimate or a count taken directly from the
frozen tables. Asserts below stop the run if a count drifts from the paper.
Run:  python render_v4.py   (needs numpy + matplotlib)
"""
import csv, json, os, sys
from pathlib import Path
os.environ.setdefault('MPLBACKEND', 'Agg')
HERE = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(HERE / '.cache/mpl'))
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

PACK = HERE.parent
DATA = PACK / '05_data_and_code/source_data'
FIG1 = PACK / '05_data_and_code/fig1_data'
OUT = HERE

# Palette v4 (checked in style/palette_check.py): ultramarine = single response, vermilion = shared
# (three-response), plum = risk forecast. Pairwise colour-vision-simulated dE >= 43 between the three.
INK = '#15202B'; MUTED = '#5A6570'; RULE = '#D9D4C9'; PANEL = '#EFEBE3'; PAPER = '#F7F4EE'
SCALAR = '#2A3BCC'; VECTOR = '#DC4F1E'; FORECAST = '#8A2F7A'; GREY = '#8A939B'; SAME = '#C9C4B8'
VECTOR_TEXT = '#B4360C'   # vermilion is 3.7:1 on paper; text uses the darker 5.5:1 variant
def tcol(c): return VECTOR_TEXT if c == VECTOR else c

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 8, 'axes.linewidth': .6, 'axes.edgecolor': INK, 'text.color': INK,
    'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK,
    'xtick.labelsize': 7.5, 'ytick.labelsize': 7.5, 'axes.spines.top': False,
    'axes.spines.right': False, 'pdf.fonttype': 42, 'svg.fonttype': 'none',
    'mathtext.fontset': 'dejavusans', 'figure.facecolor': 'white', 'savefig.facecolor': 'white',
    'axes.unicode_minus': True})


def mm(w, h): return w / 25.4, h / 25.4


def rows(name):
    with (DATA / name).open() as f: return list(csv.DictReader(f))


def export(fig, stem):
    for ext in ('pdf', 'svg', 'png'):
        fig.savefig(OUT / f'{stem}.{ext}', dpi=300, bbox_inches=None, facecolor=fig.get_facecolor())
    plt.close(fig)


# ---------------------------------------------------------------- data ----
agree = rows('holdout_design_agreement.csv')
n_single = sum(r['objective'] == 'single_response' for r in agree)
same_single = sum(r['objective'] == 'single_response' and r['identical'] == 'True' for r in agree)
n_shared = sum(r['objective'] == 'three_responses' for r in agree)
same_shared = sum(r['objective'] == 'three_responses' and r['identical'] == 'True' for r in agree)
assert (same_single, n_single, same_shared, n_shared) == (82, 120, 26, 40)

eff = {}
for r in rows('holdout_paired_effects.csv'):
    if r['primary'] == 'True' and r['metric'] == 'mse':
        eff['scalar' if 'scalar' in r['contrast'] else 'vector'] = (
            100 * float(r['relative_mse_difference']), 100 * float(r['relative_mse_ci_low']),
            100 * float(r['relative_mse_ci_high']))
assert [round(v, 2) for v in eff['scalar']] == [-3.74, -18.48, 12.12]
assert [round(v, 2) for v in eff['vector']] == [2.69, -2.95, 11.51]

fc = json.loads((DATA / 'forecast_summary.json').read_text())['primary']
SCORE = (fc['score_difference'], fc['score_difference_ci_low'], fc['score_difference_ci_high'])
assert [round(v, 5) for v in SCORE] == [-.45565, -1.15857, .02367]
net3 = rows('fig3_networks.csv')
assert len(net3) == 40 and sum(float(r['score_difference']) < 0 for r in net3) == 19

pairs = rows('fig2_network_pairs.csv')
assert len(pairs) == 80
identical_pairs = sum(float(r['descriptive_log2_ratio']) == 0 for r in pairs)
assert identical_pairs == 39  # network-objective cells with exactly equal MSE


def forest(ax, items, xlim, ticks, xlabel, fmt, pitch=1.6, bg=PANEL):
    ax.axvline(0, color=MUTED, lw=.8, ls=(0, (3, 2)), zorder=0)
    n = len(items)
    for i, (label, (m, lo, hi), col, mk) in enumerate(items):
        y = (n - 1 - i) * pitch
        ax.plot([lo, hi], [y, y], color=col, lw=1.8, solid_capstyle='butt', zorder=2)
        ax.plot([lo, lo], [y - .16, y + .16], color=col, lw=1.1)
        ax.plot([hi, hi], [y - .16, y + .16], color=col, lw=1.1)
        ax.plot(m, y, mk, color=col, ms=6, mec='white', mew=.8, zorder=3)
        ax.text(xlim[0], y + .98, label, fontsize=7.6, color=tcol(col), va='center', ha='left', fontweight='bold', zorder=5,
                bbox=dict(boxstyle='square,pad=0.15', fc=bg, ec='none'))
        ax.text(xlim[0], y + .55, fmt(m, lo, hi), fontsize=7, color=INK, va='center', ha='left', zorder=5,
                bbox=dict(boxstyle='square,pad=0.15', fc=bg, ec='none'))
    ax.set_ylim(-.5, (n - 1) * pitch + 1.3); ax.set_xlim(*xlim)
    ax.set_yticks([]); ax.spines['left'].set_visible(False)
    ax.set_xticks(ticks); ax.set_xlabel(xlabel, fontsize=7, labelpad=2)
    ax.tick_params(axis='x', length=2.5, pad=2)


def pct(m, lo, hi): return f'{m:+.1f}%  [{lo:+.1f}, {hi:+.1f}]'.replace('-', '−')


def dot_grid(ax, n, same, cols, color, x0=0., y0=0., r=.34):
    for k in range(n):
        row, col = divmod(k, cols)
        ax.add_patch(Circle((x0 + col, y0 - row), r, facecolor=color if k >= same else SAME,
                            edgecolor='none', lw=0))
    return -(-n // cols)




# ================================================================ v5 helpers ==
from matplotlib.patches import Rectangle
PCT_S = 100 * same_single / n_single   # 68.3
PCT_V = 100 * same_shared / n_shared   # 65.0


def box(base, x0, y0, x1, y1, fc='white', ec=RULE, lw=.7, r=1.8, z=1):
    base.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle=f'round,pad=0,rounding_size={r}',
                                  fc=fc, ec=ec, lw=lw, zorder=z))


def arrow(base, p, q, color=MUTED, lw=1., rad=0., ms=7, ls='-', z=4):
    base.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=ms, lw=lw, color=color,
                                   connectionstyle=f'arc3,rad={rad}', shrinkA=0, shrinkB=0, linestyle=ls, zorder=z))


def badge(base, x, y, n, r=3., fs=8):
    base.add_patch(Circle((x, y), r, fc=INK, ec='white', lw=1., zorder=8))
    base.text(x, y - .1, str(n), color='white', fontsize=fs, fontweight='bold', ha='center', va='center', zorder=9)


def setbar(base, x0, y, slots, n=12, pitch=1.6, r=.55, col=INK):
    for k in range(n):
        base.add_patch(Circle((x0 + k * pitch, y), r, fc=(col if k in slots else SAME), ec='none', zorder=4))


def propbar(base, x0, y, w, h, frac, col):
    base.add_patch(Rectangle((x0, y), w * frac, h, fc=SAME, ec='none', zorder=4))
    base.add_patch(Rectangle((x0 + w * frac, y), w * (1 - frac), h, fc=col, ec='none', zorder=4))


def canvas(W, H, face='white'):
    fig = plt.figure(figsize=mm(W, H), facecolor=face)
    base = fig.add_axes([0, 0, 1, 1]); base.set_xlim(0, W); base.set_ylim(0, H); base.axis('off')
    return fig, base


SLOTS = {1, 5, 9}   # illustrative recorded slots of the 12-neuron pool


# ============================================================ audit schematic ==
def audit_schematic():
    W, H = 180, 98
    fig, base = canvas(W, H)
    T = lambda x, y, s, **k: base.text(x, y, s, zorder=6, **k)
    ym = 60   # main row centre

    # design pool
    box(base, 3, 44, 22, 78)
    T(12.5, 73.5, 'Design pool', fontsize=7.4, fontweight='bold', ha='center', va='center')
    T(12.5, 69.6, 'recordable\nneurons', fontsize=6.4, color=MUTED, ha='center', va='center', linespacing=1.2)
    for k in range(12):
        r_, c_ = divmod(k, 4)
        base.add_patch(Circle((6.4 + c_ * 3.9, 60.5 - r_ * 3.9), 1.25, fc='#E3E8EC', ec='#B4BDC5', lw=.5, zorder=4))
    # two criteria
    for yc, a, b in [(69, 'Nominal', 'local risk'), (51, 'Prior-averaged', 'local risk')]:
        box(base, 27, yc - 7, 54, yc + 7, fc='white', ec=GREY if yc == 69 else INK, lw=.9 if yc == 69 else 1.3)
        T(40.5, yc + 2.2, a, fontsize=7.2, fontweight='bold', ha='center', va='center')
        T(40.5, yc - 2.4, b, fontsize=6.6, color=MUTED, ha='center', va='center')
        arrow(base, (22, ym), (27, yc))
    T(40.5, 81.2, 'Two criteria', fontsize=7.2, fontweight='bold', ha='center', va='center')
    # recording sets
    for yc, nm in [(69, 'Set A'), (51, 'Set B')]:
        box(base, 59, yc - 7, 80, yc + 7)
        T(69.5, yc + 3.6, f'Recording {nm}', fontsize=6.6, fontweight='bold', ha='center', va='center')
        setbar(base, 61.4, yc - 2.0, SLOTS, pitch=1.6)
        T(69.5, yc - 5.0, '3 of 12 neurons', fontsize=5.9, color=MUTED, ha='center', va='center')
        arrow(base, (54, yc), (59, yc))
    T(69.5, 81.2, 'Recording sets', fontsize=7.2, fontweight='bold', ha='center', va='center')

    # layer 1 box
    box(base, 87, 42, 119, 77, fc=PANEL, ec=INK, lw=1.1)
    for yy in (69, 51):
        base.plot([80, 83.5, 83.5, 80][:2], [yy, yy], color=MUTED, lw=.9)
    base.plot([83.5, 83.5], [51, 69], color=MUTED, lw=.9)
    arrow(base, (83.5, ym), (87, ym))
    T(94.5, 72.5, 'Same set?', fontsize=7.8, fontweight='bold', va='center')
    T(103, 67.2, 'identical designs', fontsize=6.2, color=MUTED, ha='center', va='center')
    T(90, 63.6, 'Single target', fontsize=6.4, color=SCALAR, fontweight='bold', va='center')
    propbar(base, 90, 59.2, 26, 2.6, PCT_S / 100, SCALAR)
    T(90, 56.6, f'{same_single}/{n_single} identical', fontsize=6.4, va='center')
    T(90, 52.4, 'Shared target', fontsize=6.4, color=VECTOR_TEXT, fontweight='bold', va='center')
    propbar(base, 90, 48.0, 26, 2.6, PCT_V / 100, VECTOR)
    T(90, 45.4, f'{same_shared}/{n_shared} identical', fontsize=6.4, va='center')
    badge(base, 87, 77, 1)

    # fit
    box(base, 124, 49, 143, 71)
    T(133.5, 64.5, 'Common', fontsize=7.4, fontweight='bold', ha='center', va='center')
    T(133.5, 60.6, 'MAP fit', fontsize=7.4, fontweight='bold', ha='center', va='center')
    T(133.5, 55.2, 'same model\nand prior', fontsize=6, color=MUTED, ha='center', va='center', linespacing=1.2)
    arrow(base, (119, ym), (124, ym))

    # layer 2 box
    box(base, 148, 42, 177, 77, fc=PANEL, ec=INK, lw=1.1)
    arrow(base, (143, ym), (148, ym))
    T(155, 72.5, 'Response error', fontsize=7.8, fontweight='bold', va='center')
    T(162.5, 67.6, 'predicted q vs hidden truth', fontsize=6.2, color=MUTED, ha='center', va='center')
    T(150.5, 62.8, 'Mean-MSE change', fontsize=6.4, fontweight='bold', va='center')
    T(150.5, 58.8, f'{eff["scalar"][0]:+.1f}%  [{eff["scalar"][1]:+.1f}, {eff["scalar"][2]:+.1f}]'.replace('-', '−'),
      fontsize=6.4, color=SCALAR, va='center', fontweight='bold')
    T(150.5, 54.6, f'{eff["vector"][0]:+.1f}%  [{eff["vector"][1]:+.1f}, {eff["vector"][2]:+.1f}]'.replace('-', '−'),
      fontsize=6.4, color=VECTOR_TEXT, va='center', fontweight='bold')
    T(150.5, 49.6, '97.5% CI; both include 0', fontsize=6.0, color=MUTED, va='center')
    T(150.5, 46.0, '(single | shared target)', fontsize=5.9, color=MUTED, va='center')
    badge(base, 148, 77, 2)

    # "cannot differ" arrow, layer 1 -> layer 2
    arrow(base, (92, 79.5), (160, 79.5), color=INK, lw=1.3, rad=-.28, ms=9)
    T(126, 92.6, 'cannot differ if sets are identical', fontsize=7.6, fontweight='bold', style='italic',
      ha='center', va='center')

    # lower row ------------------------------------------------------
    box(base, 92, 8, 143, 38)
    arrow(base, (133.5, 49), (133.5, 38.5))
    T(94.5, 33.4, 'Risk forecast v vs realised error e', fontsize=7.2, fontweight='bold', va='center')
    T(94.5, 29.6, 'same data and prediction; only v differs', fontsize=5.9, color=MUTED, va='center')
    for k, (nm, w_, col) in enumerate([('v  forecast', 24, FORECAST), ('e² realised', 31, INK)]):
        yy = 23.2 - k * 6.4
        T(95, yy, nm, fontsize=6.6, va='center', color=col, fontweight='bold')
        base.add_patch(Rectangle((115, yy - 1.5), w_, 3, fc=col, ec='none', zorder=4))
    T(95, 10.6, 'good forecast: v close to e²', fontsize=6, color=MUTED, va='center')

    box(base, 148, 8, 177, 38, fc=PANEL, ec=INK, lw=1.1)
    arrow(base, (143, 23), (148, 23))
    T(155, 33.2, 'Forecast score', fontsize=7.8, fontweight='bold', va='center')
    T(162.5, 28.8, 'log v + e²/v  (lower is better)', fontsize=6.1, color=MUTED, ha='center', va='center')
    T(150.5, 23.6, f'{SCORE[0]:+.2f}  [{SCORE[1]:+.2f}, {SCORE[2]:+.2f}]'.replace('-', '−'), fontsize=6.8,
      fontweight='bold', color=FORECAST, va='center')
    T(150.5, 19.6, '95% CI; includes 0', fontsize=6.0, color=MUTED, va='center')
    T(150.5, 15.6, '19 of 40 networks favour', fontsize=6.0, va='center')
    T(150.5, 12.0, 'prior-averaged risk', fontsize=6.0, va='center')
    badge(base, 148, 38, 3)

    # key insight (left lower)
    base.add_patch(Rectangle((3, 8), 1.1, 30, fc=INK, ec='none'))
    T(7, 34, 'Key insight', fontsize=7.6, fontweight='bold', va='center')
    T(7, 23.5, 'A better risk estimate can improve a prediction only\nby changing which neurons are recorded, or by\n'
               'forecasting the error more accurately.', fontsize=6.6, va='center', linespacing=1.4)
    T(7, 12.8, 'Audit layers:  1 decision agreement,  2 response error,\n3 forecast accuracy.', fontsize=6.2,
      color=MUTED, va='center', linespacing=1.4)
    export(fig, 'fig_audit_schematic_v5')


# ========================================================= graphical abstract v5 ==
def graphical_abstract_v5():
    with plt.rc_context({'font.sans-serif': ['Aileron', 'Arial', 'DejaVu Sans'], 'mathtext.fontset': 'custom',
                         'mathtext.rm': 'Aileron', 'mathtext.it': 'Aileron:italic', 'mathtext.bf': 'Aileron:bold'}):
        _ga5()


def _ga5():
    W, H = 190, 135
    fig, base = canvas(W, H, PAPER)
    T = lambda x, y, s, **k: base.text(x, y, s, zorder=6, **k)
    T(8, 128, 'Refined risk estimates often leave the recording decision unchanged',
      fontsize=15.5, family='Crimson', va='center', color=INK)
    T(8, 121.2, 'Choosing 3 neurons to record in order to predict a stimulus response; simulated 12-neuron '
                'networks with known wiring', fontsize=7.6, color=MUTED, va='center')
    base.plot([8, 182], [116.8, 116.8], color=RULE, lw=.7)

    xs = [8, 67, 126]; wc = 56          # column spans (x .. x+wc)
    top, bot = 85.5, 34.3
    # ---- pipeline strip (y 92..113) ----
    sy0, sy1 = 92.5, 113.5
    for x in xs:
        box(base, x, sy0, x + wc, sy1, fc='white', ec=RULE, lw=.7, z=1)
    T(8 + 1.6, 109.9, 'HOW A RECORDING CHOICE BECOMES A PREDICTION', fontsize=5.6, color='#9AA3AB', fontweight='bold', va='center') if False else None
    # chain 1: pool -> two criteria -> sets A,B
    for k in range(12):
        r_, c_ = divmod(k, 4)
        base.add_patch(Circle((11.3 + c_ * 2.5, 107.6 - r_ * 2.5), .85, fc='#E3E8EC', ec='#B4BDC5', lw=.4, zorder=4))
    T(14.8, 98.6, 'neuron\npool', fontsize=6.2, color=MUTED, ha='center', va='center', linespacing=1.15)
    for yc, nm, ec in [(107.2, 'nominal', GREY), (98.4, 'prior-averaged', INK)]:
        box(base, 24.5, yc - 3.3, 43.5, yc + 3.3, fc='white', ec=ec, lw=.9, r=1.4, z=3)
        T(34, yc, nm, fontsize=6.4, ha='center', va='center', fontweight='bold')
        arrow(base, (20.6, 103), (24.5, yc), ms=5, lw=.7)
        arrow(base, (43.5, yc), (46.6, yc), ms=5, lw=.7)
    for yc, nm in [(107.2, 'A'), (98.4, 'B')]:
        setbar(base, 47.6, yc, SLOTS, pitch=1.2, r=.45)
        T(49.2, yc - 3.6, f'set {nm}', fontsize=5.9, color=MUTED, va='center') if False else None
    T(54.2, 102.9, 'sets A, B', fontsize=6.2, color=MUTED, ha='center', va='center')
    # chain 2: common fit -> q vs truth
    box(base, 71, 97, 91, 109, fc=PANEL, ec='none', r=1.4, z=3)
    T(81, 105.2, 'common', fontsize=6.6, fontweight='bold', ha='center', va='center')
    T(81, 101.2, 'MAP fit', fontsize=6.6, fontweight='bold', ha='center', va='center')
    arrow(base, (91, 103), (95.5, 103), ms=6, lw=.9)
    T(105.5, 106, 'predicted q', fontsize=6.6, ha='center', va='center')
    T(105.5, 102.2, 'vs hidden', fontsize=6.6, ha='center', va='center')
    T(105.5, 98.4, 'truth', fontsize=6.6, ha='center', va='center')
    T(117, 103, '', fontsize=1)
    # chain 3: forecast v vs e
    T(128.5, 108.2, 'risk forecast v of the error', fontsize=6.4, va='center', fontweight='bold')
    base.add_patch(Rectangle((129, 104.1), 26, 2.4, fc=FORECAST, ec='none', zorder=4))
    T(156.5, 105.3, 'v', fontsize=6.4, color=FORECAST, fontweight='bold', va='center')
    T(128.5, 100.2, 'vs realised error e', fontsize=6.4, va='center', fontweight='bold')
    base.add_patch(Rectangle((129, 96.2), 26, 2.4, fc=INK, ec='none', zorder=4))
    T(150.5, 97.4, 'e', fontsize=6.4, fontweight='bold', va='center')
    # strip -> next arrows between chains
    arrow(base, (62, 103), (69, 103), ms=5, lw=.8)
    arrow(base, (119.5, 103), (128, 103), ms=5, lw=.8)

    # ---- evidence columns ----
    heads = [('1', 'Same recordings?', 'Do the criteria choose different\ndata? (40 networks)'),
             ('2', 'Lower response error?', 'Actual MSE after the common fit\n(40 networks)'),
             ('3', 'Better forecast?', 'Same data and prediction\n(40 new networks)')]
    for x, (n, h, s) in zip(xs, heads):
        box(base, x, bot, x + wc, top, fc=PANEL, ec='none', z=0)
        badge(base, x + 5.2, 89.3, n, r=2.9, fs=8)
        T(x + 10, 81.4, h, fontsize=8.4, fontweight='bold', va='center') if False else None
        T(x + 10.2, 89.3, h, fontsize=8.6, fontweight='bold', va='center', color=INK)
        T(x + 2.2, 80.4, s, fontsize=6.7, color=MUTED, va='center', linespacing=1.25)

    # column 1: dots
    x0 = xs[0] + 2.2
    def mmgrid(xg, ytop, n, same, col, cols=28, pitch=1.9):
        for k in range(n):
            r_, c_ = divmod(k, cols)
            base.add_patch(Circle((xg + .8 + c_ * pitch, ytop - r_ * pitch), .72,
                                  fc=(col if k >= same else SAME), ec='none', zorder=3))
        return -(-n // cols)
    T(x0, 72.0, '68%', fontsize=14, fontweight='bold', color=SCALAR, va='center')
    T(x0 + 15.5, 73.1, f'{same_single} of {n_single} single-target', fontsize=6.8, va='center')
    T(x0 + 15.5, 70.3, 'designs are identical', fontsize=6.8, va='center')
    rws = mmgrid(x0, 65.3, 120, 82, SCALAR)
    y2 = 65.3 - rws * 1.9 - 1.4
    T(x0, y2 - 3.4, '65%', fontsize=14, fontweight='bold', color=VECTOR_TEXT, va='center')
    T(x0 + 15.5, y2 - 2.3, f'{same_shared} of {n_shared} shared-target', fontsize=6.8, va='center')
    T(x0 + 15.5, y2 - 5.1, 'designs are identical', fontsize=6.8, va='center')
    mmgrid(x0, y2 - 9.0, 40, 26, VECTOR)
    base.add_patch(Circle((x0 + .8, 38.6), .75, fc=SAME, ec='none'))
    T(x0 + 2.8, 38.6, 'same recording set', fontsize=6.2, color=MUTED, va='center')

    # column 2: relative MSE
    ax = fig.add_axes([(xs[1] + 2) / W, 48 / H, (wc - 4) / W, 25 / H])
    forest(ax, [('Single target', eff['scalar'], SCALAR, 'o'), ('Shared target', eff['vector'], VECTOR, 's')],
           (-24, 18), [-20, 0, 15], 'Mean-MSE change vs nominal (%)', pct)
    ax.xaxis.set_label_coords(.5, -.2); ax.tick_params(axis='x', labelsize=6.8); ax.patch.set_alpha(0)
    T(xs[1] + 2.2, 36.8, '97.5% paired network-cluster CI', fontsize=6.2, color=MUTED, va='center')

    # column 3
    x3 = xs[2] + 2.2
    T(x3, 72.0, '19', fontsize=14, fontweight='bold', color=FORECAST, va='center')
    T(x3 + 9.5, 73.1, 'of 40 networks better,', fontsize=6.8, va='center')
    T(x3 + 9.5, 70.3, '21 worse', fontsize=6.8, va='center')
    ax = fig.add_axes([(xs[2] + 2) / W, 49 / H, (wc - 4) / W, 18 / H])
    forest(ax, [('Score difference', SCORE, FORECAST, 'D')], (-1.45, .5), [-1.2, -.6, 0],
           'Ensemble minus nominal score',
           lambda m, lo, hi: f'{m:+.2f}  [{lo:+.2f}, {hi:+.2f}]'.replace('-', '\u2212'))
    ax.xaxis.set_label_coords(.5, -.32); ax.tick_params(axis='x', labelsize=6.8); ax.patch.set_alpha(0)
    T(x3, 38.6, 'One network supplies 64% of the', fontsize=6.2, color=MUTED, va='center')
    T(x3, 36.0, 'summed difference; 95% paired CI', fontsize=6.2, color=MUTED, va='center')

    # takeaway
    box(base, 8, 19.4, 182, 31.6, fc=INK, ec='none')
    T(11.5, 29.0, 'WHAT THIS SHOWS', fontsize=6.2, color='#9FB3C2', va='center', fontweight='bold')
    T(11.5, 25.3, 'How much prior averaging can help is capped by how often it changes the design. All three primary',
      fontsize=7.4, color='white', va='center')
    T(11.5, 21.8, 'intervals include zero, so no stable gain is shown. The three-layer audit can be applied to other criteria.',
      fontsize=7.4, color='white', va='center')
    base.plot([8, 182], [17.6, 17.6], color=RULE, lw=.7)
    T(8, 14.4, r'Jiayi Du$^{1*\dagger}$ and Shuaizhi Cheng$^{2\dagger}$', fontsize=8, fontweight='bold', va='center')
    T(8, 10.6, r'$^{1}$ Stiftung Louisenlund, Germany     $^{2}$ Department of Computing, Harbin Institute of Technology, China',
      fontsize=6.6, va='center')
    T(8, 7.2, r'$^{\dagger}$ Equal contribution.  * Correspondence: jiayi.du@mail.louisenlund.de',
      fontsize=6.6, color=MUTED, va='center')
    T(182, 7.2, 'Simulation only; no biological validation', fontsize=6.2, color=MUTED, va='center', ha='right')
    export(fig, 'graphical_abstract_v5')


def fig2_v5():
    Wm, Hm = 180, 110
    fig = plt.figure(figsize=mm(Wm, Hm))
    base = fig.add_axes([0, 0, 1, 1]); base.set_xlim(0, Wm); base.set_ylim(0, Hm); base.axis('off')
    T = lambda x, y, s, **k: base.text(x, y, s, **k)
    lab = lambda x, y, s: T(x, y, s, fontsize=10, fontweight='bold', va='center')
    dy = 6.5
    lab(3, 99.5 + dy, 'a'); T(9, 99.5 + dy, 'Do the two criteria choose different recordings?', fontsize=8.3, va='center')
    pitch = 2.55
    def grid(x0, ytop, n, same, col):
        for k in range(n):
            r_, c_ = divmod(k, 15)
            base.add_patch(Circle((x0 + c_ * pitch, ytop - r_ * pitch), .95,
                                  fc=(col if k >= same else SAME), ec='none'))
        return -(-n // 15)
    T(9, 91.5 + dy, 'Single-response designs', fontsize=7.6, fontweight='bold', color=SCALAR, va='center')
    T(9, 87.9 + dy, f'{same_single} of {n_single} identical (68%)', fontsize=7.2, va='center')
    r1 = grid(10, 83.2 + dy, 120, same_single, SCALAR)
    y2 = 83.2 + dy - r1 * pitch - 6.2
    T(9, y2 + 4.2, 'Shared (three-response) designs', fontsize=7.6, fontweight='bold', color=VECTOR_TEXT, va='center')
    T(9, y2 + .6, f'{same_shared} of {n_shared} identical (65%)', fontsize=7.2, va='center')
    grid(10, y2 - 4.0, 40, same_shared, VECTOR)
    ly = y2 - 4.0 - 3 * pitch - 1.2
    base.add_patch(Circle((10, ly), .95, fc=SAME, ec='none')); T(12.4, ly, 'same set', fontsize=6.6, color=MUTED, va='center')
    base.add_patch(Circle((29, ly), .95, fc=SCALAR, ec='none')); base.add_patch(Circle((32, ly), .95, fc=VECTOR, ec='none'))
    T(34.4, ly, 'different set', fontsize=6.6, color=MUTED, va='center')

    base.add_patch(FancyArrowPatch((46.6, 94.5), (52, 98.2), arrowstyle='-', lw=0))
    T(52.5, 96.6, 'Grey = same recordings:\nthe fit sees the same\ndata, so error cannot\ndiffer (see b, at 0).', fontsize=6.4, color=INK,
      fontweight='bold', va='center', linespacing=1.3)
    arrow(base, (52, 96.6), (47.2, 94.6), color=INK, lw=.9, ms=7)
    lab(97, 99.5 + dy, 'b'); T(103, 99.5 + dy, 'Within-network error ratio, ensemble vs nominal', fontsize=8.3, va='center')
    ax = fig.add_axes([112 / Wm, 66 / Hm, 60 / Wm, 33 / Hm])
    rng = np.random.default_rng(7)
    for k, (name, col, mk) in enumerate([('Three responses', VECTOR, 's'), ('Single response', SCALAR, 'o')]):
        v = np.array([float(r['descriptive_log2_ratio']) for r in pairs if r['objective'] == name])
        y = k + rng.uniform(-.2, .2, v.size); same = v == 0
        ax.scatter(v[~same], y[~same], s=17, marker=mk, color=col, alpha=.88, edgecolor='white', lw=.4, zorder=3)
        ax.scatter([0], [k], s=46, marker=mk, facecolor='white', edgecolor=GREY, lw=1.1, zorder=2)
        ax.text(1.95, k, f'{same.sum()} of 40\nidentical (at 0)', fontsize=6.6, va='center', color=MUTED, linespacing=1.3)
    ax.axvline(0, color=MUTED, lw=.8, ls=(0, (3, 2)), zorder=1)
    vs_ = np.array([float(r['descriptive_log2_ratio']) for r in pairs if r['objective'] == 'Single response'])
    out = vs_[np.argmax(np.abs(vs_))]
    ax.annotate('identical designs\ncannot differ:\nratio exactly 1', xy=(0, 1.0), xytext=(-.9, 1.95), fontsize=6.6,
                color=INK, ha='center', va='center', linespacing=1.25, fontweight='bold',
                arrowprops=dict(arrowstyle='-|>', color=INK, lw=.9, shrinkA=1, shrinkB=5, mutation_scale=7), zorder=6)
    ax.annotate('one network\n(log$_2$ ratio %+.1f)' % out, xy=(out, 1.07), xytext=(out - .1, 1.95), fontsize=6.6, color=INK,
                ha='center', va='center', linespacing=1.25, fontweight='bold',
                arrowprops=dict(arrowstyle='-|>', color=INK, lw=.9, shrinkA=1, shrinkB=3, mutation_scale=7), zorder=6)
    ax.set_yticks([0, 1], ['Shared', 'Single']); ax.tick_params(axis='y', length=0)
    ax.set_ylim(-.55, 2.35); ax.set_xlim(-1.7, 3.2); ax.spines['left'].set_visible(False)
    ax.set_xticks([-1, 0, 1]); ax.set_xlabel('log$_2$(ensemble MSE / nominal MSE)', fontsize=7.4, labelpad=2)
    T(112, 55.6, '\u2190 ensemble lower error', fontsize=6.6, color=MUTED, va='center')
    T(172, 55.6, 'higher \u2192', fontsize=6.6, color=MUTED, va='center', ha='right')
    T(103, 51.4, 'Descriptive display; the primary estimand is the mean-MSE difference in c.', fontsize=6.2, color=MUTED, va='center')

    lab(3, 39.5, 'c'); T(9, 39.5, 'Frozen primary comparisons (40 independent networks)', fontsize=8.3, va='center')
    ax = fig.add_axes([40 / Wm, 11 / Hm, 84 / Wm, 24 / Hm])
    forest(ax, [('Single response', eff['scalar'], SCALAR, 'o'), ('Three responses', eff['vector'], VECTOR, 's')],
           (-22, 16), [-20, -10, 0, 10], 'Change in mean MSE, ensemble vs nominal (%)', pct, pitch=1.5, bg='white')
    T(132, 26, 'Both 97.5% paired', fontsize=7.2, color=MUTED, va='center')
    T(132, 22.4, 'network-cluster intervals', fontsize=7.2, color=MUTED, va='center')
    T(132, 18.8, 'include zero.', fontsize=7.2, color=MUTED, va='center')
    export(fig, 'fig2_recording_decisions_v5')




def fig3_v5():
    fig = plt.figure(figsize=mm(180, 92))
    lab = lambda x, y, s: fig.text(x, y, s, fontsize=10, fontweight='bold', va='top')
    risk_n = np.array([float(r['nominal_risk']) for r in net3]); risk_e = np.array([float(r['ensemble_risk']) for r in net3])
    mse = np.array([float(r['raw_mse']) for r in net3]); diff = np.array([float(r['score_difference']) for r in net3])

    ax = fig.add_axes([.085, .17, .30, .68])
    lab(.012, .985, 'a'); fig.text(.05, .975, 'Forecast risk vs actual MSE', fontsize=8.5, va='top')
    lo, hi = 3e-8, 3e-2
    ax.plot([lo, hi], [lo, hi], color=GREY, lw=.8, ls=(0, (3, 3)), zorder=0)
    for a, b, m in zip(risk_n, risk_e, mse):
        ax.plot([a, b], [m, m], color=SAME, lw=.8, zorder=1)
    ax.scatter(risk_n, mse, s=17, facecolor='white', edgecolor=FORECAST, lw=.9, zorder=3, label='Nominal')
    ax.scatter(risk_e, mse, s=17, color=FORECAST, edgecolor='white', lw=.4, zorder=4, label='Ensemble')
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel('Forecast risk (q\u00B2)'); ax.set_ylabel('Actual MSE (q\u00B2)')
    ax.legend(loc='upper left', fontsize=7.5, handletextpad=.2, borderaxespad=.1)
    ax.text(.97, .05, 'below line: forecast\nexceeds actual error', transform=ax.transAxes, fontsize=6.6,
            color=MUTED, ha='right', va='bottom', linespacing=1.3)

    ax = fig.add_axes([.48, .17, .28, .68])
    lab(.44, .985, 'b'); fig.text(.48, .975, 'All 40 network differences', fontsize=8.5, va='top')
    order = np.argsort(diff)[::-1][::-1]  # ascending: best (most negative) first
    clip = -3.4; vals = np.maximum(diff[order], clip); ypos = 39 - np.arange(40)  # best at the top
    ax.axvline(0, color=MUTED, lw=.8, ls=(0, (3, 2)), zorder=1)
    ax.barh(ypos, vals, color=[FORECAST if d < 0 else SAME for d in diff[order]], height=.78, zorder=2)
    for i in np.where(diff[order] < clip)[0]:
        ax.text(.12, ypos[i], f'{diff[order][i]:.1f} (bar clipped)'.replace('-', '\u2212'), fontsize=6.6, color=INK, va='center', ha='left')
        for dx in (-3.18, -3.06):
            ax.plot([dx - .06, dx + .06], [ypos[i] - .55, ypos[i] + .55], color='white', lw=1.3, zorder=4)
        ax.annotate('one network = 64% of the\nsummed difference', xy=(-3.4, ypos[i] + .5), xytext=(-1.7, 44.3), fontsize=6.8,
                    color=INK, fontweight='bold', ha='center', va='center', linespacing=1.3,
                    arrowprops=dict(arrowstyle='-|>', color=INK, lw=.9, shrinkA=1, shrinkB=1, mutation_scale=7), zorder=6)
    ax.set_xlim(-3.6, 1.6); ax.set_ylim(-1, 47.5); ax.set_yticks([]); ax.spines['left'].set_visible(False)
    ax.set_xlabel('Ensemble \u2212 nominal score')
    ax.text(1.55, 30, '19 better', fontsize=7.4, color=FORECAST, fontweight='bold', va='center', ha='right')
    ax.text(-3.5, 6, '21 worse', fontsize=7.2, color=MUTED, fontweight='bold', va='center', ha='left')

    ax = fig.add_axes([.86, .17, .11, .68])
    lab(.80, .985, 'c'); fig.text(.84, .975, 'Population', fontsize=8.5, va='top')
    m, l, h = SCORE
    ax.axhline(0, color=MUTED, lw=.8, ls=(0, (3, 2)), zorder=0)
    ax.plot([0, 0], [l, h], color=INK, lw=1.8, solid_capstyle='butt'); ax.plot(0, m, 'D', color=INK, ms=6, mec='white')
    for yy in (l, h): ax.plot([-.12, .12], [yy, yy], color=INK, lw=1.1)
    ax.set_xlim(-.6, .9); ax.set_ylim(-1.35, .4); ax.set_xticks([]); ax.spines['bottom'].set_visible(False)
    ax.set_ylabel('Mean score difference')
    ax.text(.17, m, f'{m:.2f}'.replace('-', '\u2212'), fontsize=7.5, va='center')
    fig.text(.84, .07, '95% CI [\u22121.16, +0.02]', fontsize=7, color=MUTED, va='top')
    export(fig, 'fig3_risk_forecasts_v5')




if __name__ == '__main__':
    audit_schematic(); graphical_abstract_v5(); fig2_v5(); fig3_v5()
