"""Local presentation-only patch of frozen v5 schematic and v4 extension.
No experiments, GA rendering, or source artifact writes. All anchors in mm.
"""
from pathlib import Path
import os, runpy
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
os.environ['MPLBACKEND']='Agg'
os.environ['MPLCONFIGDIR']=str(ROOT/'work/research_cases/mpl_cache')
SRC=ROOT/'work/evidence/ICBR2026_v4_pack/03_figures'
ns=runpy.run_path(str(SRC/'render_teaser_v5.py'))
plt=ns['plt']; Text=__import__('matplotlib.text',fromlist=['Text']).Text
C={'SCALAR':'#B73E70','VECTOR':'#D99AB3','VECTOR_TEXT':'#87385F','FORECAST':'#87385F','SAME':'#C9C5C8','INK':'#111111','MUTED':'#555055','RULE':'#D8C5CF','PANEL':'#FCF5F8','GREY':'#B9A6AF'}
ns.update(C)
plt.rcParams.update({'font.family':'Arial','font.size':6.5,'xtick.labelsize':6,'ytick.labelsize':6,'text.color':'#111111','axes.labelcolor':'#111111','axes.edgecolor':'#111111','xtick.color':'#111111','ytick.color':'#111111','pdf.fonttype':42,'svg.fonttype':'none'})
def export(fig, stem):
    titles={'Design pool','Two criteria','Recording sets','Nominal','Prior-averaged','Recording Set A','Recording Set B','Same set?','Common','MAP fit','Response error','Forecast score','Risk forecast v vs realised error e','Single-response objective','Three-response objective'}
    categories={'Single target','Shared target','Mean-MSE change','v  forecast','e² realised'}
    for text in fig.findobj(Text):
        value=text.get_text()
        text.set_fontfamily('Arial'); text.set_fontstyle('normal')
        text.set_fontweight('normal'); text.set_color('#27232B'); text.set_fontsize(6.5)
        if value in ('a','b','c'):
            text.set_fontsize(8); text.set_fontweight('bold')
        elif value in titles:
            text.set_fontsize(7); text.set_fontweight('bold')
        elif value in categories or value.startswith(('All sites,','No endpoints,')):
            text.set_fontsize(6.8)
        elif '[' in value:
            text.set_fontsize(6.5)
        else:
            text.set_fontsize(6); text.set_color('#776F78')
    if stem=='fig1_audit':
        for text in fig.findobj(Text):
            if text.get_text() in ('a','b','c','Same set?','Response error','Forecast score'):
                text.set_verticalalignment('baseline')
    for ax in fig.axes:
        for text in ax.get_xticklabels()+ax.get_yticklabels():
            text.set_fontsize(6.3);text.set_fontweight('normal');text.set_color('#6B626D')
        for text in (ax.xaxis.label,ax.yaxis.label):
            text.set_fontsize(7);text.set_fontweight('normal');text.set_color('#49424B')
    # Extension letters and titles share their top baseline, using physical mm anchors.
    if stem=='fig5_extension':
        for text in fig.texts:
            if text.get_text() in ('a','b','Single-response objective','Three-response objective'):
                text.set_y(.965); text.set_verticalalignment('baseline')
    for ext in ('pdf','svg','png'):
        fig.savefig(OUT/f'{stem}.{ext}',dpi=300,facecolor='white',bbox_inches=None)
    plt.close(fig)
ns['export']=export
# Rebind original functions to patched globals, retaining original geometry.
source=(SRC/'render_teaser_v5.py').read_text()
import ast
module=ast.parse(source)
for node in module.body:
    if isinstance(node,ast.FunctionDef) and node.name in ('box','arrow','badge','setbar','propbar','canvas','audit_schematic'):
        code=ast.get_source_segment(source,node)
        if node.name=='box':
            code=code.replace("boxstyle=f'round,pad=0,rounding_size={r}'", "boxstyle='square,pad=0'")
            code=code.replace("ec=ec, lw=lw", "ec=RULE, lw=.6")
        if node.name=='badge':
            code="def badge(base, x, y, n, r=3., fs=8):\n    xx,yy = {1:(89,72.5),2:(150,72.5),3:(150,33.2)}[n]\n    base.text(xx,yy,'abc'[n-1],fontsize=8,fontweight='bold',va='center',ha='left',color=INK,zorder=9)"
        if node.name=='audit_schematic':
            code=code.replace("24, FORECAST), ('e² realised', 31, INK)","19, FORECAST), ('e² realised', 25, INK)")
            code=code.replace("fc='#E3E8EC', ec='#B4BDC5'","fc='#F3DBE6', ec='#CDA0B5'")
            code=code.replace("'fig_audit_schematic_v5'","'fig1_audit'")
            begin=code.index('    # \"cannot differ\" arrow')
            end=code.index('    # lower row',begin)
            code=code[:begin]+code[end:]
            begin=code.index('    # key insight (left lower)')
            end=code.index('    export(fig,',begin)
            code=code[:begin]+"    T(7, 28, 'Identical recording sets and deterministic fitting\\nproduce identical point predictions.', fontsize=6.5, va='center', linespacing=1.4)\n    T(7, 16, 'Risk forecasts are evaluated separately\\nagainst the realised prediction error.', fontsize=6.5, va='center', linespacing=1.4)\n"+code[end:]
        exec(code,ns)
ns['audit_schematic']()
# Extension uses the same frozen CSV. Original estimator/CI calculations retained.
source=(SRC/'render_v4.py').read_text()
for node in ast.parse(source).body:
    if isinstance(node,ast.FunctionDef) and node.name=='fig4':
        code=ast.get_source_segment(source,node).replace("'fig4_model_extension_v4'","'fig5_extension'")
        # Physical anchors remain original 180 x 88 mm. Improve shared-target edge contrast.
        code=code.replace("mec=col, mew=1.2","mec=(FORECAST if k == 1 else col), mew=1.0")
        exec(code,ns)
if '--fig1-only' not in __import__('sys').argv: ns['fig4']()
print('Rendered fig1_audit and fig5_extension from frozen sources.')
