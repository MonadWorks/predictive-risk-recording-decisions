"""Shared typography, palette and drawing rules for the manuscript figures.

Physical rules follow the collaborator's refined manuscript: a 180 mm canvas,
BentonSans text, JuliaMono statistical annotations and Times New Roman maths;
8 pt panel letters, 7 pt panel titles and axis labels, 6.3 pt ticks, 6 pt
notes. Figures are drawn at final size and placed without rescaling.

Every colour has one meaning in all figures (see ROLE). Effects are ratios of
mean errors on a logarithmic axis labelled as percentage change. Pointwise 95%
intervals are thick; multiplicity-adjusted intervals are thin and pale. Filled
markers are prespecified primary comparisons; open markers are secondary.

The BentonSans subset contains empty outlines for U+2212 (minus), Delta and
<=. BentonSans negatives therefore use an en dash; JuliaMono keeps the true
minus. check_text() rejects any figure that would print an empty glyph.
"""
from functools import lru_cache
from pathlib import Path
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.text import Text
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator, NullFormatter

HERE = Path(__file__).resolve().parent
FONT_DIRS = [HERE.parent / 'pastel_figure_suite/fonts', HERE.parent / 'graphical_abstract/source/fonts']

WIDTH = 180.0
LETTER, TITLE, LABEL_PT, TICK_PT, CATEGORY, NUMBER, NOTE = 8, 7, 7, 6.3, 6.6, 6.1, 6.0

PAPER = '#FFFFFF'
INK = '#2E2531'
LABEL = '#49424B'
TICK = '#6B626D'
MUTED = '#7D7280'
RULE = '#E6DCE2'
PAIR = '#E8DFE4'
ROSE = '#E27A9E'
ROSE_DARK = '#B5708C'
READOUT = '#F2B1C7'
PALE_ROSE = '#F4BFD0'
GOLD = '#EDAF26'
GOLD_DARK = '#DB9A1D'
GREY = '#B9AEB7'
LIGHT_GREY = '#DAD4D8'
PLUM = '#6E5677'
BLEND = '#A8668F'
NOISE = ['#E27A9E', '#EFA9C2', '#F7D5E2']

ROLE = {
    'endpoints': ROSE,          # stimulation and readout sites recorded together
    'stimulus': GOLD,           # stimulation site
    'readouts': READOUT,        # readout sites
    'ordinary': GREY,           # nonendpoint sites, controls, no extra information
    'internal': PLUM,           # recurrent gain combinations
    'nominal': GREY,            # original criterion studies: nominal local risk
    'ensemble': GOLD,           # original criterion studies: prior-averaged risk
}
EN, MINUS = '–', '−'


def setup():
    for folder in FONT_DIRS:
        for path in folder.glob('*.ttf'):
            fm.fontManager.addfont(str(path))
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.sans-serif': ['BentonSans'], 'font.size': LABEL_PT,
        'axes.labelsize': LABEL_PT, 'xtick.labelsize': TICK_PT, 'ytick.labelsize': TICK_PT,
        'axes.linewidth': .6, 'axes.spines.top': False, 'axes.spines.right': False,
        'axes.edgecolor': INK, 'axes.labelcolor': LABEL, 'axes.labelpad': 3,
        'xtick.color': TICK, 'ytick.color': TICK, 'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
        'xtick.major.width': .6, 'ytick.major.width': .6, 'xtick.major.pad': 2, 'ytick.major.pad': 2,
        'xtick.minor.size': 0, 'ytick.minor.size': 0,
        'axes.unicode_minus': False, 'axes.grid': False, 'legend.frameon': False,
        'mathtext.fontset': 'custom', 'mathtext.rm': 'BentonSans', 'mathtext.it': 'Times New Roman:italic',
        'mathtext.bf': 'BentonSans:bold', 'mathtext.default': 'regular',
        'pdf.fonttype': 42, 'svg.fonttype': 'none', 'text.color': INK,
        'figure.facecolor': PAPER, 'savefig.facecolor': PAPER, 'savefig.bbox': None,
        'lines.solid_capstyle': 'butt', 'path.simplify': False,
    })


# --------------------------------------------------------------------- text
def dash(s):
    """Text for BentonSans: hyphen-minus and minus become a visible en dash."""
    return re.sub(r'(?<![A-Za-z])-(?=[\d.])', EN, str(s)).replace(MINUS, EN)


def signed(v, digits=2):
    """JuliaMono number with a true minus sign and explicit plus sign."""
    s = f'{v:+.{digits}f}'
    return s.replace('-', MINUS)


def ci_text(est, lo, hi, digits=2):
    return f'{signed(est, digits)} [{signed(lo, digits)}, {signed(hi, digits)}]'


def pct_label(ratio):
    p = (ratio - 1) * 100
    if abs(p) < 1e-9:
        return '0'
    s = f'{p:+.2f}'.rstrip('0').rstrip('.')
    return (s + '%').replace('-', EN)


def power_label(x, pos=None):
    e = int(round(np.log10(x)))
    return '$\\mathdefault{10^{%s}}$' % (str(e).replace('-', EN))


# --------------------------------------------------------------- canvas
class Canvas:
    """Figure in millimetre coordinates with checked manual annotations."""

    def __init__(self, height):
        setup()
        self.h = float(height)
        self.fig = plt.figure(figsize=(WIDTH / 25.4, self.h / 25.4))
        self.base = self.fig.add_axes([0, 0, 1, 1], zorder=-10)
        self.base.set(xlim=(0, WIDTH), ylim=(0, self.h))
        self.base.set_axis_off()
        self.manual = []

    def ax(self, x, y, w, h, **kw):
        a = self.fig.add_axes([x / WIDTH, y / self.h, w / WIDTH, h / self.h], **kw)
        a.patch.set_alpha(0)
        return a

    def text(self, x, y, s, size=CATEGORY, color=INK, weight='normal', family=None, ha='left', va='baseline', **kw):
        t = self.base.text(x, y, s if family == 'JuliaMono' else dash(s), fontsize=size, color=color,
                           fontweight=weight, ha=ha, va=va, **kw)
        if family:
            t.set_fontfamily(family)
        self.manual.append(t)
        return t

    def header(self, x, y, letter, title):
        if letter:
            self.text(x, y, letter, LETTER, weight='bold')
        self.text(x + (5 if letter else 0), y, title, TITLE, weight='bold')

    def note(self, x, y, s, **kw):
        return self.text(x, y, s, NOTE, color=MUTED, **kw)

    def mono(self, x, y, s, size=NUMBER, color=INK, **kw):
        return self.text(x, y, s, size, color=color, family='JuliaMono', **kw)

    def rule(self, x0, x1, y, color=RULE, lw=.6):
        self.base.plot([x0, x1], [y, y], color=color, lw=lw, solid_capstyle='butt')

    def marker(self, x, y, color, filled=True, size=3.4, edge=None, shape='o'):
        self.base.plot([x], [y], marker=shape, ms=size, mfc=color if filled else PAPER,
                       mec=edge or (color if not filled else color), mew=.8, ls='none')

    def y_of(self, ax, value):
        """Millimetre y of a data value in a linear-y axes."""
        disp = ax.transData.transform((ax.get_xlim()[0], value))
        return self.base.transData.inverted().transform(disp)[1]

    def x_of(self, ax, value):
        """Millimetre x of a data value in a linear-x axes."""
        disp = ax.transData.transform((value, ax.get_ylim()[0]))
        return self.base.transData.inverted().transform(disp)[0]

    def categories(self, ax, labels, y, size=CATEGORY, **kw):
        """Category labels centred under strip positions 0..k-1, top edge at y mm."""
        return [self.text(self.x_of(ax, k), y, s, size, ha='center', va='top', linespacing=1.15, **kw)
                for k, s in enumerate(labels)]


# ----------------------------------------------------------- axis styles
def clean(ax, left=True, bottom=True):
    for side, spine in ax.spines.items():
        spine.set_visible((side == 'left' and left) or (side == 'bottom' and bottom))
        spine.set_linewidth(.6)
        spine.set_color(INK)
    ax.tick_params(colors=TICK, labelcolor=TICK, labelsize=TICK_PT, width=.6, length=2.5, pad=2)
    ax.xaxis.label.set_color(LABEL)
    ax.yaxis.label.set_color(LABEL)


def log_axis(axis, lo, hi, every=1):
    axis.axes.set_xscale('log') if axis is axis.axes.xaxis else axis.axes.set_yscale('log')
    e0, e1 = int(np.ceil(np.log10(lo) - 1e-9)), int(np.floor(np.log10(hi) + 1e-9))
    ticks = [10.0 ** e for e in range(e0, e1 + 1) if (e - e0) % every == 0]
    axis.set_major_locator(FixedLocator(ticks))
    axis.set_major_formatter(FuncFormatter(power_label))
    axis.set_minor_locator(NullLocator())
    axis.set_minor_formatter(NullFormatter())
    (axis.axes.set_xlim if axis is axis.axes.xaxis else axis.axes.set_ylim)(lo, hi)


def ratio_axis(ax, lo, hi, ticks, label='Change in mean MSE', ref=True):
    """Logarithmic ratio axis labelled as percentage change."""
    ax.set_xscale('log')
    ax.set_xlim(lo, hi)
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: pct_label(x)))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_minor_formatter(NullFormatter())
    if ref:
        ax.axvline(1, color=MUTED, lw=.55, ls=(0, (2.2, 2.2)), zorder=0)
    ax.set_xlabel(label, fontsize=LABEL_PT, color=LABEL, labelpad=2.5)
    clean(ax, left=False)
    ax.set_yticks([])


def ratio(change_pct):
    return 1 + np.asarray(change_pct, dtype=float) / 100


def interval(ax, y, est, lo, hi, color, filled=True, adjusted=None, size=3.6, lw=1.15, marker='o'):
    """One comparison: pale adjusted interval, solid pointwise interval and marker."""
    if adjusted is not None:
        ax.plot(ratio(adjusted), [y, y], color=color, lw=.55, alpha=.55, zorder=1, solid_capstyle='butt')
        for end in ratio(adjusted):
            ax.plot([end, end], [y - .12, y + .12], color=color, lw=.55, alpha=.55, zorder=1)
    ax.plot(ratio([lo, hi]), [y, y], color=color, lw=lw, zorder=2, solid_capstyle='butt')
    ax.plot([ratio(est)], [y], marker=marker, ms=size, mfc=color if filled else PAPER, mec=color,
            mew=.9, ls='none', zorder=3)


# ------------------------------------------------------------- strip plots
def boot_mean_ci(v, seed=381, reps=10000):
    v = np.asarray(v, dtype=float)
    ix = np.random.default_rng(seed).integers(0, len(v), (reps, len(v)))
    return np.percentile(v[ix].mean(1), [2.5, 97.5])


def strip(ax, values, colors, paired=True, seed=11, width=.17, size=7.5, mean=True, edges=None):
    """Network dots per condition, light lines joining each network, ink mean and 95% interval."""
    values = [np.asarray(v, dtype=float) for v in values]
    n = len(values[0])
    rng = np.random.default_rng(seed)
    jitter = rng.uniform(-width, width, (len(values), n))
    xs = np.arange(len(values))[:, None] + jitter
    if paired:
        for i in range(n):
            ax.plot(xs[:, i], [v[i] for v in values], color=PAIR, lw=.35, zorder=1, solid_joinstyle='round')
    for k, v in enumerate(values):
        ax.scatter(xs[k], v, s=size, color=colors[k], edgecolors=(edges[k] if edges else 'none'),
                   linewidths=.35, zorder=2, alpha=.92)
        if mean:
            lo, hi = boot_mean_ci(v)
            ax.plot([k, k], [lo, hi], color=INK, lw=.75, zorder=4, solid_capstyle='butt')
            ax.plot([k - .26, k + .26], [v.mean()] * 2, color=INK, lw=1.3, zorder=4, solid_capstyle='butt')
    ax.set_xlim(-.6, len(values) - .4)
    ax.set_xticks([])
    clean(ax, bottom=False)


# --------------------------------------------------------------------- QA
@lru_cache(None)
def empty_glyphs(path):
    from fontTools.ttLib import TTFont
    from fontTools.pens.boundsPen import BoundsPen
    font = TTFont(path)
    glyphs = font.getGlyphSet()
    empty = set()
    for code, name in font.getBestCmap().items():
        if chr(code).isspace():
            continue
        pen = BoundsPen(glyphs)
        glyphs[name].draw(pen)
        if pen.bounds is None:
            empty.add(code)
    return frozenset(empty)


def glyph_problems(t, s=None):
    """Characters of s (default: t's text) that would print as an empty outline.

    Strings containing maths are laid out by the mathtext parser, which reports
    the actual font file and character of every glyph it places.
    """
    from matplotlib.mathtext import MathTextParser
    s = t.get_text() if s is None else s
    prop = t.get_fontproperties()
    if t.get_usetex():
        return []
    if len(re.findall(r'(?<!\\)\$', s)) >= 2:
        glyphs = MathTextParser('path').parse(s, 72, prop).glyphs
        return [chr(num) for font, _, num, _, _ in glyphs if num in empty_glyphs(font.fname)]
    empty = empty_glyphs(fm.findfont(prop))
    return [c for c in s if ord(c) in empty]


def check_text(fig, manual=(), min_size=5.0, layout=True):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.bbox.width, fig.bbox.height
    problems = []
    texts = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]
    for t in texts:
        if t.axes is not None and t in (t.axes.get_xticklabels() + t.axes.get_yticklabels()):
            lo, hi = sorted(t.axes.get_xlim() if t in t.axes.get_xticklabels() else t.axes.get_ylim())
            pos = t.get_position()[0 if t in t.axes.get_xticklabels() else 1]
            if not (lo - 1e-12 <= pos <= hi + 1e-12):
                continue
        b = t.get_window_extent(r)
        if b.x0 < -.5 or b.y0 < -.5 or b.x1 > W + .5 or b.y1 > H + .5:
            problems.append(('outside canvas', t.get_text()))
        if layout and t.get_fontsize() < min_size - 1e-9:
            problems.append(('font below %.1f pt' % min_size, t.get_text(), t.get_fontsize()))
        bad = glyph_problems(t)
        if bad:
            problems.append(('empty glyph', t.get_text(), Path(fm.findfont(t.get_fontproperties())).name, bad))
    if not layout:
        assert not problems, problems
        return len(texts)
    # Manual annotations, axis labels and visible tick labels must not collide.
    checked = [t for t in manual if t.get_visible() and t.get_text().strip()]
    for ax in fig.axes:
        for label in (ax.xaxis.label, ax.yaxis.label):
            if label.get_visible() and label.get_text().strip():
                checked.append(label)
        for ticks, lim in ((ax.get_xticklabels(), ax.get_xlim()), (ax.get_yticklabels(), ax.get_ylim())):
            lo, hi = sorted(lim)
            for t in ticks:
                pos = t.get_position()[0 if ticks is ax.get_xticklabels() else 1]
                if t.get_visible() and t.get_text().strip() and lo - 1e-12 <= pos <= hi + 1e-12:
                    checked.append(t)
    gap = .8 / 25.4 * fig.dpi
    for ax in fig.axes:
        lo, hi = sorted(ax.get_xlim())
        ticks = sorted([t.get_window_extent(r) for t in ax.get_xticklabels()
                        if t.get_visible() and t.get_text().strip() and lo - 1e-12 <= t.get_position()[0] <= hi + 1e-12],
                       key=lambda b: b.x0)
        for b, c in zip(ticks, ticks[1:]):
            if c.x0 - b.x1 < gap:
                problems.append(('crowded x ticks', ax.get_xlabel()))
    boxes = [(t, t.get_window_extent(r)) for t in checked]
    for i, (t, b) in enumerate(boxes):
        for u, c in boxes[i + 1:]:
            if b.overlaps(c) and min(b.x1, c.x1) - max(b.x0, c.x0) > .8 and min(b.y1, c.y1) - max(b.y0, c.y0) > .8:
                problems.append(('overlap', t.get_text(), u.get_text()))
    assert not problems, problems
    return len(texts)


def save(canvas_or_fig, path, manual=None):
    fig = canvas_or_fig.fig if isinstance(canvas_or_fig, Canvas) else canvas_or_fig
    manual = canvas_or_fig.manual if isinstance(canvas_or_fig, Canvas) and manual is None else (manual or [])
    n = check_text(fig, manual)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path.with_suffix('.pdf'), metadata={'CreationDate': None, 'ModDate': None})
    fig.savefig(path.with_suffix('.png'), dpi=300)
    plt.close(fig)
    return {'texts_checked': n, 'size_mm': [WIDTH, round(fig.get_size_inches()[1] * 25.4, 2)]}
