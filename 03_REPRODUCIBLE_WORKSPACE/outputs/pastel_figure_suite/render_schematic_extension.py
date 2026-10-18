"""Local presentation-only patch of frozen v5 schematic and v4 extension.
No experiments, GA rendering, or source artifact writes. All anchors in mm.
"""
from pathlib import Path
import os, runpy
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
os.environ['MPLBACKEND']='Agg'
os.environ['MPLCONFIGDIR']=str(ROOT/'work/research_cases/mpl_cache')
import matplotlib.font_manager as fm
for _f in (OUT/'fonts').glob('*.ttf'):
    fm.fontManager.addfont(str(_f))
for _n in ('Times New Roman','Times New Roman Bold','Times New Roman Italic','Times New Roman Bold Italic'):
    _p=Path('/System/Library/Fonts/Supplemental')/f'{_n}.ttf'
    if _p.exists():fm.fontManager.addfont(str(_p))
SRC=ROOT/'work/evidence/ICBR2026_v4_pack/03_figures'
ns=runpy.run_path(str(SRC/'render_teaser_v5.py'))
plt=ns['plt']; Text=__import__('matplotlib.text',fromlist=['Text']).Text
C={'SCALAR':'#E27A9E','VECTOR':'#F4BFD0','VECTOR5':'#E8A13C','VECTOR_TEXT':'#2E2531','FORECAST':'#EDAF26','SAME':'#DAD4D8','INK':'#2E2531','MUTED':'#7D7280','RULE':'#EBDCE4','PANEL':'#FDF4F8','GREY':'#B9AEB7'}
ns.update(C)
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['BentonSans','JuliaMono','DejaVu Sans'],'font.size':6.5,'xtick.labelsize':6,'ytick.labelsize':6,'text.color':'#2E2531','axes.labelcolor':'#2E2531','axes.edgecolor':'#2E2531','xtick.color':'#2E2531','ytick.color':'#2E2531','pdf.fonttype':42,'svg.fonttype':'none'})
def export(fig, stem):
    titles={'Design pool','Two criteria','Recording sets','Nominal','Prior-averaged','Recording Set A','Recording Set B','Same set?','Common','MAP fit','Response error','Score difference','Risk forecast v vs realised error e','Forecast risk and squared error','Recording agreement','Risk assessment','Single-response objective','Three-response objective'}
    categories={'Single target','Shared target','Mean-MSE change','v  forecast','e² realised'}
    for text in fig.findobj(Text):
        value=text.get_text()
        text.set_fontfamily('BentonSans'); text.set_fontstyle('normal')
        text.set_fontweight('normal'); text.set_color('#2E2531'); text.set_fontsize(6.5)
        if value in ('1','2'):
            text.set_fontsize(6.5);text.set_color('#7D7280')
        elif value in ('Recording agreement','Risk assessment'):
            text.set_fontsize(6.5);text.set_fontweight('bold')
        elif value in ('a','b','c'):
            text.set_fontsize(8); text.set_fontweight('bold')
        elif value in titles:
            text.set_fontsize(7); text.set_fontweight('bold')
        elif value in categories or value.startswith(('All sites,','No endpoints,','Endpoints excluded,')):
            text.set_fontsize(6.8)
        elif '[' in value:
            text.set_fontsize(6.5)
            if value.strip()[:1] in ('+', '-', '\u2212'):
                text.set_fontfamily('JuliaMono'); text.set_color('#2E2531')
        else:
            text.set_fontsize(6); text.set_color('#7D7280')
    if stem=='fig1_audit':
        for text in fig.findobj(Text):
            if text.get_text() in ('a','b','c','Same set?','Response error','Score difference'):
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
    if stem=='fig1_audit':
        import re,json
        base=fig.axes[0]
        for text in fig.findobj(Text):
            v=text.get_text()
            if v in ('Single target','Shared target'):
                text.set_fontsize(6);text.set_color('#49424B')
            if re.match(r'^[+−-]\d',v) or v.startswith('['):
                text.set_fontfamily('JuliaMono');text.set_fontsize(6);text.set_color('#2E2531')
            if v in ('Forecast risk, v','Squared error, e²'):
                text.set_fontsize(6.4);text.set_color('#49424B')
            if v=='log v + e²/v':
                text.set_fontfamily('Times New Roman');text.set_fontsize(6.8);text.set_color('#49424B')
        fig.canvas.draw();renderer=fig.canvas.get_renderer();issues=[];bounds=[]
        for text in base.texts:
            x,y=text.get_position();container=None
            if 148<=x<=177 and 42<=y<=77:container=(148,42,177,77)
            elif 148<=x<=177 and 8<=y<=38:container=(148,8,177,38)
            elif 87<=x<=143 and 8<=y<=38:container=(87,8,143,38)
            if container:
                b=text.get_window_extent(renderer).transformed(base.transData.inverted())
                got=[b.x0,b.y0,b.x1,b.y1];bounds.append({'text':text.get_text(),'bounds_mm':got,'container_mm':container})
                if b.x0<container[0]+.4 or b.x1>container[2]-.4 or b.y0<container[1]+.3 or b.y1>container[3]-.3:issues.append(text.get_text())
        assert not issues,('text exceeds panel',issues)
        overlaps=[]
        texts=[t for t in base.texts if 148<=t.get_position()[0]<=177 and 8<=t.get_position()[1]<=77]
        for i,t in enumerate(texts):
            for u in texts[i+1:]:
                if t.get_window_extent(renderer).overlaps(u.get_window_extent(renderer)):overlaps.append([t.get_text(),u.get_text()])
        assert not overlaps,overlaps
        (OUT/'fig1_layout_audit.json').write_text(json.dumps({'panel_text_bounds':bounds,'panel_overflow':issues,'result_panel_text_overlaps':overlaps,'aligned_box_left_edges_mm':[87,87],'illustrative_bar_left_mm':109.5,'callout_number_x_mm':9,'callout_text_x_mm':12.5,'callout_title_body_spacing_mm':5.6,'estimated_intervals_unchanged':True},indent=2))
    for ext in ('pdf','svg','png'):
        fig.savefig(OUT/f'{stem}.{ext}',dpi=300,facecolor='white',bbox_inches=None)
    plt.close(fig)
ns['export']=export

def refine_audit(code):
    code=code.replace("fc='#E3E8EC', ec='#B4BDC5'", "fc='#FBEAF1', ec='#EAB8CC'")
    code=code.replace("'fig_audit_schematic_v5'", "'fig1_audit'")
    a=code.index('    # layer 2 box');b=code.index('    # "cannot differ" arrow',a)
    code=code[:a]+"""    # Compact, aligned result block; frozen values are unchanged.
    box(base, 148, 42, 177, 77, fc=PANEL)
    arrow(base, (143, ym), (148, ym))
    T(155, 72.5, 'Response error', va='baseline')
    T(150.5, 68.2, 'Mean-MSE change', va='center')
    T(150.5, 63.0, 'Single target', va='center')
    T(174.5, 63.0, f'{eff['scalar'][0]:+.1f}%'.replace('-', '−'), ha='right', va='center')
    T(174.5, 59.5, f'[{eff['scalar'][1]:+.1f}, {eff['scalar'][2]:+.1f}]'.replace('-', '−'), ha='right', va='center')
    T(150.5, 54.5, 'Shared target', va='center')
    T(174.5, 54.5, f'{eff['vector'][0]:+.1f}%'.replace('-', '−'), ha='right', va='center')
    T(174.5, 51.0, f'[{eff['vector'][1]:+.1f}, {eff['vector'][2]:+.1f}]'.replace('-', '−'), ha='right', va='center')
    T(150.5, 45.5, '97.5% CIs include zero', va='center')
    badge(base, 148, 77, 2)

"""+code[b:]
    a=code.index('    # "cannot differ" arrow');b=code.index('    # lower row',a);code=code[:a]+code[b:]
    a=code.index('    # lower row');b=code.index('    # key insight (left lower)',a)
    code=code[:a]+"""    # The lower forecast box shares x=87 with the recording-agreement box.
    box(base, 87, 8, 143, 38)
    arrow(base, (133.5, 49), (133.5, 38.5))
    T(90, 33.4, 'Forecast risk and squared error', va='baseline')
    T(90, 29.4, 'Fixed point prediction; different risk estimates', va='center')
    for nm, yy, width, col in [('Forecast risk, v', 23.3, 19, VECTOR), ('Squared error, e²', 17.4, 25, '#B5708C')]:
        T(90, yy, nm, va='center')
        base.add_patch(Rectangle((109.5, yy-1.2), width, 2.4, fc=col, ec='none', zorder=4))
    T(90, 11.0, 'Illustration only (not experimental values)', va='center')

    box(base, 148, 8, 177, 38, fc=PANEL)
    arrow(base, (143, 23), (148, 23))
    T(155, 33.2, 'Score difference', va='baseline')
    T(162.5, 28.1, 'log v + e²/v', ha='center', va='center')
    T(162.5, 24.9, 'Lower is better', ha='center', va='center')
    T(150.5, 20.8, f'{SCORE[0]:+.2f}'.replace('-', '−'), va='center')
    T(150.5, 17.2, f'[{SCORE[1]:+.2f}, {SCORE[2]:+.2f}]'.replace('-', '−'), va='center')
    T(150.5, 13.5, '95% CI includes zero', va='center')
    T(150.5, 10.2, 'Lower in 19/40 networks', va='center')
    badge(base, 148, 38, 3)

"""+code[b:]
    a=code.index('    # key insight (left lower)');b=code.index('    export(fig,',a)
    code=code[:a]+"""    T(9, 33.4, '1', va='baseline')
    T(12.5, 33.4, 'Recording agreement', va='baseline')
    T(12.5, 27.8, 'Identical data and deterministic fitting yield\\nidentical point predictions.', va='center', linespacing=1.25)
    T(9, 18.5, '2', va='baseline')
    T(12.5, 18.5, 'Risk assessment', va='baseline')
    T(12.5, 12.9, 'Fix the point prediction; evaluate risk estimates\\nagainst the realised squared error.', va='center', linespacing=1.25)
"""+code[b:]
    return code

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
            code=refine_audit(code)
        exec(code,ns)
ns['audit_schematic']()
# Extension uses the same frozen CSV. Original estimator/CI calculations retained.
source=(SRC/'render_v4.py').read_text()
for node in ast.parse(source).body:
    if isinstance(node,ast.FunctionDef) and node.name=='fig4':
        code=ast.get_source_segment(source,node).replace("'fig4_model_extension_v4'","'fig5_extension'")
        # Physical anchors remain original 180 x 88 mm. Panel letters share the
        # title gutter; the three-response series stays a single warm hue family
        # (no amber edge mixed onto pink markers); footnote left-aligns to canvas.
        code=code.replace("lab(x0 - (.16 if k == 0 else .03), .985, 'ab'[k])","lab(x0 - .03, .985, 'ab'[k])")
        code=code.replace("('ensemble_vector', 'Three-response objective', VECTOR, 's', .60)","('ensemble_vector', 'Three-response objective', VECTOR5, 's', .60)")
        code=code.replace("fig.text(.17, .10, 'Filled marker:","fig.text(.02, .10, 'Filled marker:")
        exec(code,ns)
if '--fig1-only' not in __import__('sys').argv: ns['fig4']()
print('Rendered fig1_audit and fig5_extension from frozen sources.')
