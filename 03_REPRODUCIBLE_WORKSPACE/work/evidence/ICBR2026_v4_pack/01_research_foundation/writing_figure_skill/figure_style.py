"""Optional final-size Matplotlib defaults; no statistical transformations."""
from pathlib import Path
import matplotlib as mpl

MM_PER_INCH=25.4
COLORS={'scalar':'#0072B2','vector':'#D55E00','reference':'#6E6E6E',
        'ink':'#20262B','grid':'#DFE3E6'}

def apply_style():
    mpl.rcParams.update({
        'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],
        'font.size':8.5,'axes.labelsize':8.5,'axes.titlesize':9,
        'axes.titleweight':'normal','axes.linewidth':0.65,
        'axes.edgecolor':COLORS['ink'],'text.color':COLORS['ink'],
        'axes.labelcolor':COLORS['ink'],'xtick.color':COLORS['ink'],'ytick.color':COLORS['ink'],
        'xtick.labelsize':8,'ytick.labelsize':8,'xtick.major.width':0.6,'ytick.major.width':0.6,
        'xtick.major.size':3,'ytick.major.size':3,'lines.linewidth':1,
        'axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False,
        'legend.fontsize':8,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none',
        'savefig.dpi':300,'figure.dpi':160,'savefig.bbox':None,'savefig.facecolor':'white',
        'mathtext.fontset':'dejavusans','axes.unicode_minus':True,
    })

def size_mm(width=180,height=120):
    return width/MM_PER_INCH,height/MM_PER_INCH

def export(fig,stem):
    """Keep the requested physical page size; do not silently tight-crop it."""
    stem=Path(stem);stem.parent.mkdir(parents=True,exist_ok=True)
    for ext in ('pdf','svg','png'):
        fig.savefig(stem.with_suffix('.'+ext),bbox_inches=None,dpi=300)
