"""v4 presentation layer: graphical abstract, Fig. 2 and Fig. 3.

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


# ---------------------------------------------------- graphical abstract ----
def graphical_abstract():
    with plt.rc_context({'font.sans-serif': ['Aileron', 'Arial', 'DejaVu Sans'], 'mathtext.fontset': 'custom',
                         'mathtext.rm': 'Aileron', 'mathtext.it': 'Aileron:italic', 'mathtext.bf': 'Aileron:bold'}):
        _graphical_abstract()


def _graphical_abstract():
    W, H = 190, 135
    fig = plt.figure(figsize=mm(W, H), facecolor=PAPER)
    base = fig.add_axes([0, 0, 1, 1]); base.set_xlim(0, W); base.set_ylim(0, H); base.axis('off')
    T = lambda x, y, s, **k: base.text(x, y, s, **k)

    T(8, 127, 'Refined risk estimates often leave the recording decision unchanged',
      fontsize=15.5, family='Crimson', va='center', color=INK)
    T(8, 119.6, 'Choosing 3 neurons to record in order to predict a stimulus response; simulated 12-neuron '
                'networks with known wiring', fontsize=7.6, color=MUTED, va='center')
    base.plot([8, 182], [114.6, 114.6], color=RULE, lw=.7)

    # --- network schematic (network J5000, real signed weights) ---------
    W_ = np.zeros((12, 12))
    for r in csv.DictReader((FIG1 / 'weights.csv').open()):
        W_[int(r['postsynaptic_node']), int(r['presynaptic_node'])] = float(r['weight'])
    man = json.loads((FIG1 / 'manifest.json').read_text())
    rec, stim, readout = man['selected_nodes'], man['stim'], man['readout']
    cx, cy, R = 30, 85, 19
    ang = np.pi / 2 - 2 * np.pi * np.arange(12) / 12
    pos = np.c_[cx + R * np.cos(ang), cy + R * np.sin(ang)]
    wmax = np.abs(W_).max()
    for i in range(12):
        for j in range(12):
            if i != j and W_[i, j] != 0:
                a = .13 + .55 * abs(W_[i, j]) / wmax
                base.add_patch(FancyArrowPatch(pos[j], pos[i], connectionstyle='arc3,rad=.14',
                    arrowstyle='-', lw=.55, color=('#4C7FA8' if W_[i, j] > 0 else '#C2663A'),
                    alpha=min(a, .75), shrinkA=3.5, shrinkB=3.5))
    for i, (x, y) in enumerate(pos):
        if i in rec:
            base.add_patch(Circle((x, y), 3.1, fc=SCALAR, ec='white', lw=.8, zorder=3))
        elif i == readout:
            base.add_patch(Circle((x, y), 3.1, fc='white', ec=VECTOR, lw=1.4, zorder=3))
        elif i == stim:
            base.add_patch(Circle((x, y), 3.1, fc='white', ec=FORECAST, lw=1.4, zorder=3))
        else:
            base.add_patch(Circle((x, y), 2.5, fc='#E3E8EC', ec='#B4BDC5', lw=.6, zorder=3))
    T(cx, cy + .2, 'known\nwiring', ha='center', va='center', fontsize=7, color=MUTED, linespacing=1.15)
    lx, ly = 10, 57.5
    for k, (fc_, ec_, lab) in enumerate([(SCALAR, 'white', 'recorded node (budget M = 3)'),
                                          ('white', FORECAST, 'stimulated node'),
                                          ('white', VECTOR, 'response readout')]):
        base.add_patch(Circle((lx + 1.4, ly - 4.4 * k), 1.45, fc=fc_, ec=ec_, lw=1.2))
        T(lx + 4.6, ly - 4.4 * k, lab, fontsize=6.8, va='center', color=INK)
    T(8, 40.6, 'Example: network J5000 (1 of 40)\nblue = excitatory, orange = inhibitory',
      fontsize=6.1, color=MUTED, va='center', linespacing=1.3)

    # --- three evidence columns -----------------------------------------
    xs = [58, 100, 142]; wcol = 38
    heads = [('1', 'Same recordings?', 'Do the two criteria choose\ndifferent data? (40 networks)'),
             ('2', 'Lower error?', 'Actual response MSE after\nfitting (40 networks)'),
             ('3', 'Better forecast?', 'Same data and prediction\n(40 new networks)')]
    for x, (n, h, s) in zip(xs, heads):
        base.add_patch(FancyBboxPatch((x - 1.5, 37.5), wcol + 3, 72, boxstyle='round,pad=0,rounding_size=2',
                                      fc=PANEL, ec='none'))
        base.add_patch(Circle((x + 2.3, 104.4), 2.3, fc=INK, ec='none'))
        T(x + 2.3, 104.2, n, color='white', fontsize=7.4, fontweight='bold', ha='center', va='center')
        T(x + 6.3, 104.5, h, fontsize=8, fontweight='bold', va='center')
        T(x, 97.4, s, fontsize=6.7, color=MUTED, va='center', linespacing=1.25)

    # column 1: agreement dot grids, drawn directly in mm
    def mmgrid(x0, ytop, n, same, col, cols=15, pitch=2.3):
        for k in range(n):
            r_, c_ = divmod(k, cols)
            base.add_patch(Circle((x0 + 1 + c_ * pitch, ytop - r_ * pitch), .85,
                                  fc=(col if k >= same else SAME), ec='none', zorder=3))
        return -(-n // cols)
    T(xs[0], 90.5, '68%', fontsize=14, fontweight='bold', color=SCALAR, va='center')
    T(xs[0] + 15.5, 91.7, '82 of 120 single-target', fontsize=6.7, va='center')
    T(xs[0] + 15.5, 88.9, 'designs are identical', fontsize=6.7, va='center')
    rws = mmgrid(xs[0], 83.4, 120, 82, SCALAR)
    y2 = 83.4 - rws * 2.3 - 6.4
    T(xs[0], y2 - 3.2 + 6.2, '65%', fontsize=14, fontweight='bold', color=VECTOR_TEXT, va='center')
    T(xs[0] + 15.5, y2 - 3.2 + 7.4, '26 of 40 shared-target', fontsize=6.7, va='center')
    T(xs[0] + 15.5, y2 - 3.2 + 4.6, 'designs are identical', fontsize=6.7, va='center')
    mmgrid(xs[0], y2 - 3.2, 40, 26, VECTOR)
    base.add_patch(Circle((xs[0] + 1.4, 41.4), .85, fc=SAME, ec='none'))
    T(xs[0] + 3.4, 41.4, 'same recording set', fontsize=6.1, color=MUTED, va='center')

    # column 2: relative MSE
    ax = fig.add_axes([(xs[1] + 1) / W, 54 / H, (wcol - 2) / W, 30 / H])
    forest(ax, [('Single target', eff['scalar'], SCALAR, 'o'), ('Shared target', eff['vector'], VECTOR, 's')],
           (-26, 18), [-20, 0, 15], 'Mean-MSE change vs nominal (%)', pct)
    ax.xaxis.set_label_coords(.5, -.2); ax.tick_params(axis='x', labelsize=6.8)
    T(xs[1], 40.9, '97.5% paired network-cluster CI', fontsize=6.1, color=MUTED, va='center')

    # column 3: forecast score
    T(xs[2], 88.5, '19', fontsize=14, fontweight='bold', color=FORECAST, va='center')
    T(xs[2] + 9, 89.7, 'of 40 networks better,', fontsize=6.7, va='center')
    T(xs[2] + 9, 86.9, '21 worse', fontsize=6.7, va='center')
    ax = fig.add_axes([(xs[2] + 1) / W, 54 / H, (wcol - 2) / W, 24 / H])
    forest(ax, [('Score difference', SCORE, FORECAST, 'D')], (-1.45, .5), [-1.2, -.6, 0],
           'Ensemble minus nominal score',
           lambda m, lo, hi: f'{m:+.2f}  [{lo:+.2f}, {hi:+.2f}]'.replace('-', '\u2212'))
    ax.xaxis.set_label_coords(.5, -.26); ax.tick_params(axis='x', labelsize=6.8)
    T(xs[2], 40.9, '95% paired network-cluster CI', fontsize=6.1, color=MUTED, va='center')
    for ax_ in fig.axes[1:]: ax_.patch.set_alpha(0)

    # takeaway
    base.add_patch(FancyBboxPatch((8, 21.2), 174, 13.6, boxstyle='round,pad=0,rounding_size=2', fc=INK, ec='none'))
    T(11.5, 31.4, 'WHAT THIS SHOWS', fontsize=6.2, color='#9FB3C2', va='center', fontweight='bold')
    T(11.5, 27.1, 'How much prior averaging can help is capped by how often it changes the design. All three primary',
      fontsize=7.4, color='white', va='center')
    T(11.5, 23.6, 'intervals include zero, so no stable gain is shown. The same three-step audit fits any criterion.',
      fontsize=7.4, color='white', va='center')

    base.plot([8, 182], [18.2, 18.2], color=RULE, lw=.7)
    T(8, 14.4, r'Jiayi Du$^{1*\dagger}$ and Shuaizhi Cheng$^{2\dagger}$', fontsize=8, fontweight='bold', va='center')
    T(8, 10.6, r'$^{1}$ Stiftung Louisenlund, Germany     $^{2}$ Department of Computing, Harbin Institute of Technology, China',
      fontsize=6.6, va='center')
    T(8, 7.2, r'$^{\dagger}$ Equal contribution.  * Correspondence: jiayi.du@mail.louisenlund.de',
      fontsize=6.6, color=MUTED, va='center')
    T(182, 7.2, 'Simulation only; no biological validation', fontsize=6.2, color=MUTED, va='center', ha='right')
    export(fig, 'graphical_abstract_v4')


# ----------------------------------------------------------------- Fig 2 ----
def fig2():
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

    lab(97, 99.5 + dy, 'b'); T(103, 99.5 + dy, 'Within-network error ratio, ensemble vs nominal', fontsize=8.3, va='center')
    ax = fig.add_axes([112 / Wm, 72 / Hm, 60 / Wm, 27 / Hm])
    rng = np.random.default_rng(7)
    for k, (name, col, mk) in enumerate([('Three responses', VECTOR, 's'), ('Single response', SCALAR, 'o')]):
        v = np.array([float(r['descriptive_log2_ratio']) for r in pairs if r['objective'] == name])
        y = k + rng.uniform(-.2, .2, v.size); same = v == 0
        ax.scatter(v[~same], y[~same], s=17, marker=mk, color=col, alpha=.88, edgecolor='white', lw=.4, zorder=3)
        ax.scatter([0], [k], s=46, marker=mk, facecolor='white', edgecolor=GREY, lw=1.1, zorder=2)
        ax.text(1.95, k, f'{same.sum()} of 40\nidentical (at 0)', fontsize=6.6, va='center', color=MUTED, linespacing=1.3)
    ax.axvline(0, color=MUTED, lw=.8, ls=(0, (3, 2)), zorder=1)
    ax.set_yticks([0, 1], ['Shared', 'Single']); ax.tick_params(axis='y', length=0)
    ax.set_ylim(-.55, 1.55); ax.set_xlim(-1.7, 3.2); ax.spines['left'].set_visible(False)
    ax.set_xticks([-1, 0, 1]); ax.set_xlabel('log$_2$(ensemble MSE / nominal MSE)', fontsize=7.4, labelpad=2)
    T(112, 59.4, '\u2190 ensemble lower error', fontsize=6.6, color=MUTED, va='center')
    T(172, 59.4, 'higher \u2192', fontsize=6.6, color=MUTED, va='center', ha='right')
    T(103, 55.4, 'Descriptive display; the primary estimand is the mean-MSE difference in c.', fontsize=6.2, color=MUTED, va='center')

    lab(3, 39.5, 'c'); T(9, 39.5, 'Frozen primary comparisons (40 independent networks)', fontsize=8.3, va='center')
    ax = fig.add_axes([40 / Wm, 11 / Hm, 84 / Wm, 24 / Hm])
    forest(ax, [('Single response', eff['scalar'], SCALAR, 'o'), ('Three responses', eff['vector'], VECTOR, 's')],
           (-22, 16), [-20, -10, 0, 10], 'Change in mean MSE, ensemble vs nominal (%)', pct, pitch=1.5, bg='white')
    T(132, 26, 'Both 97.5% paired', fontsize=7.2, color=MUTED, va='center')
    T(132, 22.4, 'network-cluster intervals', fontsize=7.2, color=MUTED, va='center')
    T(132, 18.8, 'include zero.', fontsize=7.2, color=MUTED, va='center')
    export(fig, 'fig2_recording_decisions_v4')


# ----------------------------------------------------------------- Fig 3 ----
def fig3():
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
    ax.set_xlim(-3.6, 1.6); ax.set_ylim(-1, 40.6); ax.set_yticks([]); ax.spines['left'].set_visible(False)
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
    export(fig, 'fig3_risk_forecasts_v4')


# ----------------------------------------------------------------- Fig 4 ----
def fig4():
    fig = plt.figure(figsize=mm(180, 88))
    lab = lambda x, y, s: fig.text(x, y, s, fontsize=10, fontweight='bold', va='top')
    settings = [('all', '5', 'All sites, M = 5'), ('all', '10', 'All sites, M = 10'),
                ('exclude_endpoints', '5', 'No endpoints, M = 5'), ('exclude_endpoints', '10', 'No endpoints, M = 10')]
    table = {}
    for r in rows('n100_paired_effects.csv'):
        if r['metric'] == 'mse' and r['condition'] == 'published_gain' and r['contrast'] in (
                'ensemble_scalar - local_scalar', 'ensemble_vector - local_vector'):
            table[(r['contrast'].split(' ')[0], r['pool'], r['budget'])] = tuple(
                100 * float(r[k]) for k in ('relative_mse_difference', 'relative_mse_ci_low', 'relative_mse_ci_high'))
    excl = 0
    for k, (key, title, col, mk, x0) in enumerate([('ensemble_scalar', 'Single-response objective', SCALAR, 'o', .17),
                                                   ('ensemble_vector', 'Three-response objective', VECTOR, 's', .60)]):
        ax = fig.add_axes([x0, .30, .17, .55])
        lab(x0 - (.16 if k == 0 else .03), .985, 'ab'[k]); fig.text(x0, .975, title, fontsize=8.5, va='top')
        ax.axvline(0, color=MUTED, lw=.8, ls=(0, (3, 2)), zorder=0)
        for i, (pool, bud, name) in enumerate(settings):
            m, lo, hi = table[(key, pool, bud)]; y = 3 - i; hit = hi < 0 or lo > 0; excl += hit
            ax.plot([max(lo, -110), min(hi, 215)], [y, y], color=col, lw=1.6, solid_capstyle='butt', zorder=2)
            ax.plot(m, y, mk, ms=6, color=col if hit else 'white', mec=col, mew=1.2, zorder=3)
            ax.text(1.06, y, f'{m:+.1f}  [{lo:+.1f}, {hi:+.1f}]'.replace('-', '\u2212'), transform=ax.get_yaxis_transform(),
                    fontsize=6.8, va='center', ha='left', color=INK)
            if k == 0: ax.text(-.04, y, name, transform=ax.get_yaxis_transform(), fontsize=7.4, va='center', ha='right')
        ax.set_xlim(-110, 215); ax.set_ylim(-.6, 3.6); ax.set_yticks([]); ax.spines['left'].set_visible(False)
        ax.set_xticks([-100, 0, 100, 200]); ax.set_xlabel('Ensemble vs nominal, mean-MSE change (%)', fontsize=7.4)
    fig.text(.17, .10, 'Filled marker: 95% interval excludes zero (4 of 8 settings, all favouring the ensemble). Hollow: includes zero.\n'
             'Exploratory: 8 independent 100-unit networks, pointwise intervals, no multiplicity adjustment; model family and N change together.',
             fontsize=6.6, color=MUTED, va='top', linespacing=1.4)
    assert excl == 4
    export(fig, 'fig4_model_extension_v4')


if __name__ == '__main__':
    graphical_abstract(); fig2(); fig3(); fig4()
    print('written:', sorted(p.name for p in OUT.glob('*_v4.*')))
