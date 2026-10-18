from pathlib import Path
import ast,os,runpy,json
ROOT=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026');OUT=ROOT/'outputs/graphical_abstract_redesign'
os.environ['MPLBACKEND']='Agg';os.environ['MPLCONFIGDIR']=str(ROOT/'work/ga_redesign/mpl')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.text import Text
from matplotlib.patches import FancyBboxPatch,Circle
for p in (ROOT/'outputs/pastel_figure_suite/fonts').glob('*.ttf'):fm.fontManager.addfont(str(p))
for name in ['Times New Roman','Times New Roman Italic','Times New Roman Bold']:
 p=Path('/System/Library/Fonts/Supplemental')/(name+'.ttf')
 if p.exists():fm.fontManager.addfont(str(p))
SRC=ROOT/'work/evidence/ICBR2026_v4_pack/03_figures/render_v4.py';ns=runpy.run_path(str(SRC))
ns.update(INK='#2E2531',MUTED='#655D69',RULE='#DED5DC',PANEL='#F6F3F4',PAPER='#FEFDFC',SCALAR='#CA799A',VECTOR='#65566F',VECTOR_TEXT='#65566F',FORECAST='#9C537C',GREY='#8A828D',SAME='#D6D0D5')
ns['tcol']=lambda c:c
plt.rcParams.update({'font.family':'BentonSans','font.sans-serif':['BentonSans'],'mathtext.fontset':'custom','mathtext.rm':'Times New Roman','mathtext.it':'Times New Roman:italic','mathtext.bf':'Times New Roman:bold','pdf.fonttype':42,'svg.fonttype':'none'})
# Reuse original forest geometry, limits and values; only typography is adjusted.
origforest=ns['forest']
def forest(*args,**kw):
 origforest(*args,**kw)
 a=args[0]
 for t in a.findobj(Text):
  if t.get_text():
   t.set_fontfamily('BentonSans');t.set_color(ns['INK'] if t.get_color() in ['#15202B'] else t.get_color());t.set_fontsize(t.get_fontsize()*1.18)
 a.xaxis.label.set_fontsize(8.1)
 for t in a.get_xticklabels():t.set_fontsize(8)
ns['forest']=forest
module=ast.parse(SRC.read_text());fn=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='_graphical_abstract')
class Patch(ast.NodeTransformer):
 def visit_Expr(self,node):
  if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='T':
   st=' '.join(n.value for n in ast.walk(node.value) if isinstance(n,ast.Constant) and isinstance(n.value,str))
   if any(k in st for k in ['Jiayi Du','Stiftung Louisenlund','Equal contribution','Simulation only; no biological validation']):return None
  # Original footer rule removed with author block.
  if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr=='plot':
   if '[18.2, 18.2]' in ast.unparse(node):return None
  return self.generic_visit(node)
 def visit_Constant(self,node):
  if not isinstance(node.value,str):return node
  replacements={
   'Refined risk estimates often leave the recording decision unchanged':'Prior-averaged risk often leaves recording decisions unchanged',
   'Choosing 3 neurons to record in order to predict a stimulus response; simulated 12-neuron ':'Record 3 units to predict an integrated stimulus response: simulated 12-unit ',
   'networks with known wiring':'networks; known connectivity, uncertain physiology',
   'known\nwiring':'known\nconnectivity',
   'Example: network J5000 (1 of 40)\nblue = excitatory, orange = inhibitory':r'$q=\int [r_{\mathrm{stim}}(t)-r_{\mathrm{control}}(t)]\,dt$',
   'recorded node (budget M = 3)':'recorded node (M = 3)',
   'Same recordings?':'Recording agreement',
   'Lower error?':'Response error',
   'Better forecast?':'Risk forecasts',
   'Do the two criteria choose\ndifferent data? (40 networks)':'Nominal vs prior-averaged risk\n40 independent networks',
   'Actual response MSE after\nfitting (40 networks)':'Common MAP fit and budget\n40 independent networks',
   'Same data and prediction\n(40 new networks)':'Fixed data and point prediction\n40 new independent networks',
   'Single target':'Single response',
   'Shared target':'Shared three-response',
   'Score difference':'MSE-forecast score difference',
   'WHAT THIS SHOWS':'PRIMARY AND EXPLORATORY FINDINGS',
   'How much prior averaging can help is capped by how often it changes the design. All three primary':'Identical recordings yield identical predictions under the common fit. Primary error and forecast intervals include zero.',
   'intervals include zero, so no stable gain is shown. The same three-step audit fits any criterion.':'In the 100-unit extension, 4 of 8 intervals exclude zero, all favouring prior averaging (8 networks; exploratory).',
   'Mean-MSE change vs nominal (%)':'Mean-MSE change (%)',
   'Ensemble minus nominal score':'Prior-averaged minus nominal',
   'of 40 networks better,':'of 40 networks score lower;',
   '21 worse':'21 score higher',
  }
  
  if node.value.startswith('Choosing 3 neurons to record in order to predict a stimulus response;'):
   return ast.copy_location(ast.Constant('Record 3 units to predict an integrated stimulus response: known connectivity, uncertain physiology; simulated 12-unit networks'),node)
  return ast.copy_location(ast.Constant(replacements.get(node.value,node.value)),node)
 def visit_Call(self,node):
  # scale physical canvas, preserve Claude coordinate system and panel geometry.
  if isinstance(node.func,ast.Name) and node.func.id=='mm' and len(node.args)==2 and all(isinstance(a,ast.Name) for a in node.args):node.args=[ast.Constant(260),ast.Constant(185)]
  # Change network positive/negative edge colours locally, keep all signed weights.
  if isinstance(node.func,ast.Name) and node.func.id=='T':
   st=' '.join(n.value for n in ast.walk(node) if isinstance(n,ast.Constant) and isinstance(n.value,str))
   for kw in node.keywords:
    if kw.arg=='fontsize' and isinstance(kw.value,ast.Constant):
     size=kw.value.value;kw.value=ast.Constant(18.5 if size==15.5 else 16 if size==14 else size*1.19)
    if kw.arg=='family':kw.value=ast.Constant('Times New Roman')
    if kw.arg=='color' and isinstance(kw.value,ast.Constant) and kw.value.value=='white':kw.value=ast.Name(id='INK',ctx=ast.Load())
   if 'Example: network J5000' in st:
    for kw in node.keywords:
     if kw.arg=='fontsize':kw.value=ast.Constant(9)
    node.keywords.append(ast.keyword(arg='family',value=ast.Constant('Times New Roman')))
   if 'WHAT THIS SHOWS' in st:
    for kw in node.keywords:
     if kw.arg=='color':kw.value=ast.Name(id='MUTED',ctx=ast.Load())
  return self.generic_visit(node)
fn=Patch().visit(fn);ast.fix_missing_locations(fn);exec(compile(ast.Module(body=[fn],type_ignores=[]),str(SRC),'exec'),ns)

def export(fig,stem):
 # Frame polish: use Fig1's thin outline, very light fill, and restrained type weight.
 base=fig.axes[0]
 for patch in base.patches:
  if isinstance(patch,FancyBboxPatch):
   # Three original evidence panels remain; summary panel is expanded into reclaimed footer.
   if patch.get_y()<30:
    patch.set_y(5.2);patch.set_height(29.6);patch.set_facecolor('#F5F2F4');patch.set_edgecolor('#DED5DC');patch.set_linewidth(.65)
   else:patch.set_facecolor('#FAF7F8');patch.set_edgecolor('#DED5DC');patch.set_linewidth(.6)
  if isinstance(patch,Circle):
   # Tiny dark heading badges replaced by quiet numerals without a black disc.
   if abs(patch.get_radius()-2.3)<.01:patch.set_facecolor('none');patch.set_edgecolor('none')
   x,y=patch.center
   if (abs(x-30)<.01 and abs(y-104)<.01) or (abs(x-11.4)<.01 and abs(y-53.1)<.01):patch.set_edgecolor('#D4A239')
 # Fix original risk/stimulus role collision only on network and legend.
 # Display post-stimulation target with a small exact q definition replacing old source caption.
 for t in fig.findobj(Text):
  v=t.get_text()
  if not v.strip():continue
  if v in ['1','2','3']:
   t.set_fontfamily('BentonSans');t.set_fontsize(9);t.set_color('#655D69');t.set_fontweight('normal')
  if v in ['Recording agreement','Response error','Risk forecasts']:
   t.set_fontsize(9.5);t.set_fontweight('bold')
  if v.startswith('82 of 120') or v.startswith('26 of 40'):t.set_fontsize(8.0)
  if v in ['Single response','Shared three-response','MSE-forecast score difference']:t.set_fontsize(8.4)
  if v.startswith('PRIMARY AND EXPLORATORY'):
   t.set_text('With identical recordings, the common estimator gives identical predictions.');t.set_position((11.5,29.2));t.set_fontsize(9.0);t.set_fontweight('normal');t.set_color('#2E2531')
  if v.startswith('Identical recordings yield'):
   t.set_text('All primary response-error and risk-forecast intervals include zero.');t.set_position((11.5,23.2));t.set_fontsize(9.0)
  if v.startswith('In the 100-unit extension'):
   t.set_text('Exploratory 100-unit family: 4 of 8 intervals exclude zero, all favouring prior averaging (8 independent networks).');t.set_position((11.5,16.8));t.set_fontsize(9.0)
 # Font-realised minus signs: the supplied Benton subset lacks a usable minus glyph.
  # Keep all numerical strings in JuliaMono, matching the manuscript figure roles.
  if any(ch.isdigit() for ch in v) and (v.startswith(('+','−','-')) or v in ['−20','0','15','−1.2','−0.6','0.0']):
   t.set_fontfamily('JuliaMono');t.set_fontsize(8.0)
  if t.get_bbox_patch() is not None:t.get_bbox_patch().set_facecolor('#FAF7F8')
 # New precision notes sit inside retained summary frame, not a footer stripe.
 base.text(142,80.5,'One network supplies 64% of the\nsummed score difference',fontsize=7.7,color='#655D69',va='center',fontfamily='BentonSans',linespacing=1.2)
 base.text(8,36.5,'Blue: positive; orange: negative connections',fontsize=6.7,color='#655D69',va='center',fontfamily='BentonSans')
 base.text(11.5,10.4,'Extension: unadjusted 95% intervals; one point estimate reverses sign. All quantities are simulated.',fontsize=7.5,color='#655D69',va='center',fontfamily='BentonSans')
 # First-round check of font-realised text extents and overlaps.
 fig.canvas.draw();r=fig.canvas.get_renderer();B=[]
 for t in fig.findobj(Text):
  if not t.get_visible() or not t.get_text().strip():continue
  # exclude invisible auto-axis tick labels outside limits
  if t.axes and t.axes is not base:
   pass
  b=t.get_window_extent(r);p=base.transData.inverted().transform([[b.x0,b.y0],[b.x1,b.y1]])
  B.append({'text':t.get_text(),'bbox':p.tolist(),'font':t.get_fontfamily(),'size':t.get_fontsize()})
 overlaps=[]
 for i,a in enumerate(B):
  for b in B[i+1:]:
   x,y=a['bbox'];u,v=b['bbox']
   if min(y[0],v[0])-max(x[0],u[0])>.2 and min(y[1],v[1])-max(x[1],u[1])>.2:overlaps.append([a['text'],b['text']])
 (OUT/'round3_audit.json').write_text(json.dumps({'text_overlaps':overlaps,'texts':B,'baseline':str(SRC),'geometry':'Original Claude v4 coordinate system; physical canvas 260 x 185 mm'},indent=2))
 for e in ['png','pdf','svg']:fig.savefig(OUT/f'graphical_abstract_round3.{e}',dpi=250,facecolor=fig.get_facecolor())
 plt.close(fig)
 print(json.dumps({'overlaps':overlaps},ensure_ascii=False))
ns['export']=export
ns['_graphical_abstract']()
