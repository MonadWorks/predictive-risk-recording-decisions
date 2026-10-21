"""Palette shared by the current figures and graphical abstract."""
import numpy as np
from matplotlib import colors
from matplotlib.lines import Line2D
from matplotlib.collections import Collection
from matplotlib.patches import Patch

PAPER = '#FEFDFC'
PANEL = '#FAF7F8'
INK = '#2E2531'
MUTED = '#655D69'
RULE = '#DED5DC'
ROSE = '#B14F7C'
PINK = '#CA799A'
PALE_ROSE = '#D9A9BF'
PLUM = '#65566F'
GOLD = '#D4A239'
GREY = '#A29AA5'
LIGHT_GREY = '#D6D0D5'

# Keep each original category distinct; recolor every matching artist and legend.
COLOR_MAP = {
    '#176b66': ROSE, '#3e827d': ROSE,
    '#a9bfba': PALE_ROSE,
    '#697da6': PLUM, '#9280ad': PLUM,
    '#c38135': GOLD, '#bd8e60': GOLD,
    '#9f4e48': PLUM,
    '#9dabb8': GREY, '#7b8290': GREY,
    '#a2a9b3': LIGHT_GREY, '#8b7555': GOLD,
}


def recolor(value):
    """Replace RGB only, preserving per-point opacity and empty colors."""
    try:
        rgba = colors.to_rgba_array(value)
    except (ValueError, TypeError):
        return value
    if not len(rgba):
        return value
    changed = False
    for old, new in COLOR_MAP.items():
        mask = np.all(np.isclose(rgba[:, :3], colors.to_rgb(old), atol=1e-8), axis=1)
        if mask.any():
            rgba[mask, :3] = colors.to_rgb(new)
            changed = True
    if not changed:
        return value
    return tuple(rgba[0]) if len(rgba) == 1 and isinstance(value, (str, tuple)) else rgba


def apply_palette(fig):
    for artist in fig.findobj():
        if isinstance(artist, Line2D):
            for field in ('color', 'markerfacecolor', 'markeredgecolor', 'markerfacecoloralt'):
                old = getattr(artist, 'get_' + field)()
                getattr(artist, 'set_' + field)(recolor(old))
        elif isinstance(artist, Collection):
            artist.set_facecolor(recolor(artist.get_facecolor()))
            artist.set_edgecolor(recolor(artist.get_edgecolor()))
        elif isinstance(artist, Patch):
            artist.set_facecolor(recolor(artist.get_facecolor()))
            artist.set_edgecolor(recolor(artist.get_edgecolor()))
