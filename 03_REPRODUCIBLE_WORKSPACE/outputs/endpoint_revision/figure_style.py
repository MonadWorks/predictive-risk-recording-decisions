"""Physical typography and palette of the collaborator's refined manuscript.

All manuscript figures use a 180 mm canvas, BentonSans text, 8 pt panel
letters, 7 pt panel titles/axis labels and 6.3 pt tick labels. JuliaMono is
reserved for aligned statistical annotations. Pink denotes the focal result;
gold and muted plum distinguish comparison conditions.
Numbers belong on scales or in comparisons that need them. Avoid metric cards
and repeated statistical summaries already conveyed by the plot or caption.
"""
from pathlib import Path
import numpy as np
from matplotlib import colors, font_manager as fm
from matplotlib.lines import Line2D
from matplotlib.collections import Collection
from matplotlib.patches import Patch

PAPER = '#FFFFFF'
PANEL = '#FDF4F8'
INK = '#2E2531'
MUTED = '#7D7280'
RULE = '#EBDCE4'
ROSE = '#E27A9E'
PINK = ROSE
PALE_ROSE = '#F4BFD0'
PLUM = '#7D7280'
GOLD = '#EDAF26'
GREY = '#B9AEB7'
LIGHT_GREY = '#DAD4D8'
TICK = '#6B626D'
LABEL = '#49424B'
HERE = Path(__file__).resolve().parent

COLOR_MAP = {
    '#176b66': ROSE, '#3e827d': ROSE,
    '#a9bfba': PALE_ROSE,
    '#697da6': PLUM, '#9280ad': PLUM,
    '#c38135': GOLD, '#bd8e60': GOLD,
    '#9f4e48': PLUM,
    '#9dabb8': GREY, '#7b8290': GREY,
    '#a2a9b3': LIGHT_GREY, '#8b7555': GOLD,
    '#000000': INK,
}


def setup(plt):
    for p in (HERE.parent/'pastel_figure_suite/fonts').glob('*.ttf'):
        fm.fontManager.addfont(str(p))
    for suffix in ('', ' Bold', ' Italic', ' Bold Italic'):
        p=Path('/System/Library/Fonts/Supplemental')/f'Times New Roman{suffix}.ttf'
        if p.exists(): fm.fontManager.addfont(str(p))
    plt.rcParams.update({
        'font.family':'sans-serif', 'font.sans-serif':['BentonSans','DejaVu Sans'],
        'font.size':7, 'axes.labelsize':7, 'xtick.labelsize':6.3, 'ytick.labelsize':6.3,
        'axes.linewidth':.6, 'axes.spines.top':False, 'axes.spines.right':False,
        'xtick.major.size':2.5, 'ytick.major.size':2.5,
        'xtick.major.width':.6, 'ytick.major.width':.6,
        'pdf.fonttype':42, 'svg.fonttype':'none', 'mathtext.fontset':'stix',
        'mathtext.default':'rm', 'axes.unicode_minus':False,
        'mathtext.rm':'Times New Roman', 'mathtext.it':'Times New Roman:italic',
        'mathtext.bf':'Times New Roman:bold', 'text.color':INK,
        'axes.labelcolor':LABEL, 'axes.edgecolor':INK, 'xtick.color':TICK,
        'ytick.color':TICK, 'figure.facecolor':PAPER, 'savefig.facecolor':PAPER,
        'savefig.bbox':None,
    })


def recolor(value):
    """Replace RGB only, preserving per-point opacity and empty colors."""
    try: rgba=colors.to_rgba_array(value)
    except (ValueError,TypeError): return value
    if not len(rgba): return value
    changed=False
    for old,new in COLOR_MAP.items():
        mask=np.all(np.isclose(rgba[:,:3],colors.to_rgb(old),atol=1e-8),axis=1)
        if mask.any(): rgba[mask,:3]=colors.to_rgb(new); changed=True
    if not changed:return value
    return tuple(rgba[0]) if len(rgba)==1 and isinstance(value,(str,tuple)) else rgba


def apply_palette(fig):
    for a in fig.findobj():
        if isinstance(a,Line2D):
            for field in ('color','markerfacecolor','markeredgecolor','markerfacecoloralt'):
                getattr(a,'set_'+field)(recolor(getattr(a,'get_'+field)()))
        elif isinstance(a,Collection):
            a.set_facecolor(recolor(a.get_facecolor()));a.set_edgecolor(recolor(a.get_edgecolor()))
        elif isinstance(a,Patch):
            a.set_facecolor(recolor(a.get_facecolor()));a.set_edgecolor(recolor(a.get_edgecolor()))
