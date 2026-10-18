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
 # Keep the zero reference adjacent to data only; it must not cross annotations.
 if a.lines:
  zero=a.lines[0]
  if list(zero.get_xdata())==[0,0]:zero.remove()
 n=len(args[1]);pitch=kw.get('pitch',1.6)
 if n==2:
  for artist in list(a.lines):
   yy=list(artist.get_ydata())
   if yy:
    shift=.79 if sum(yy)/len(yy)>.8 else .1233333333
    artist.set_ydata([y+shift for y in yy])
  page=a.figure.axes[0]
  for t in a.texts:
   _,y=t.get_position();upper=y>1
   label=t.get_text() in ['Single response','Shared three-response']
   target=(90.5 if label else 85.5) if upper else (70.0 if label else 65.0)
   t.set_transform(page.transData);t.set_position((100,target))
 for i in range(n):
  y=([2.39,.1233333333][i] if n==2 else 0)
  a.plot([0,0],[y-.28,y+.28],color='#7D7280',lw=.75,ls=(0,(2,2)),zorder=0)
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
   'Do the two criteria choose\ndifferent data? (40 networks)':'Nominal vs prior-averaged local risk\n40 independent networks',
   'Actual response MSE after\nfitting (40 networks)':'Common MAP fit and budget\nSame 40 networks',
   'Same data and prediction\n(40 new networks)':'Fixed data and point prediction\n40 new independent networks',
   'Single target':'Single response',
   'Shared target':'Shared three-response',
   'Score difference':'MSE-forecast score difference',
   'WHAT THIS SHOWS':'PRIMARY AND EXPLORATORY FINDINGS',
   'How much prior averaging can help is capped by how often it changes the design. All three primary':'Identical recordings yield identical predictions under the common fit. Primary error and forecast-score intervals include zero.',
   'intervals include zero, so no stable gain is shown. The same three-step audit fits any criterion.':'In the 100-unit extension, 4 of 8 intervals exclude zero, all favouring prior averaging (8 networks; exploratory).',
   'Mean-MSE change vs nominal (%)':'Mean-MSE change vs nominal (%)',
   'Ensemble minus nominal score':'Prior-averaged minus nominal',
   'of 40 networks better,':'of 40 favour prior averaging;',
   '21 worse':'21 favour nominal',
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
    patch.set_x(56.5);patch.set_width(124.0);patch.set_y(17.2);patch.set_height(17.6);patch.set_facecolor('#F5F2F4');patch.set_edgecolor('#DED5DC');patch.set_linewidth(.65)
   else:patch.set_width(40.0);patch.set_facecolor('#FAF7F8');patch.set_edgecolor('#DED5DC');patch.set_linewidth(.6)
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
   t.set_text('Identical recording sets and data yield identical predictions under the common MAP fit.');t.set_position((59,31.1));t.set_fontsize(8.2);t.set_fontweight('normal');t.set_color('#2E2531')
  if v.startswith('Identical recordings yield'):
   t.set_text('Primary error and forecast-score intervals include zero.');t.set_position((59,28.2));t.set_fontsize(8.5);t.set_fontweight('bold')
  if v.startswith('In the 100-unit extension'):
   t.set_text('Exploratory 100-unit rank-two family (8 independent networks): 4/8 setting-specific 95% intervals exclude zero,');t.set_position((59,23.4));t.set_fontsize(8.2)
 # Font-realised minus signs: the supplied Benton subset lacks a usable minus glyph.
  # Keep all numerical strings in JuliaMono, matching the manuscript figure roles.
  if any(ch.isdigit() for ch in v) and (v.startswith(('+','−','-')) or v in ['−20','0','15','−1.2','−0.6','0.0']):
   t.set_fontfamily('JuliaMono');t.set_fontsize(8.0)
  if t.get_bbox_patch() is not None:t.get_bbox_patch().set_facecolor('#FAF7F8')
 # Rebuild the header and internal hierarchy on shared baselines.
  if v.startswith('Prior-averaged risk often leaves'):
   t.set_text('Predictive risk and recording decisions');t.set_position((8,128.7));t.set_fontsize(18.5);t.set_fontfamily('BentonSans');t.set_fontweight('bold')
  if v.startswith('Record 3 units to predict'):
   t.set_text('Nominal versus prior-averaged local risk for stimulus-response prediction');t.set_position((8,116.7));t.set_fontsize(9.2);t.set_fontweight('normal')
  if v=='known\nconnectivity':
   t.set_visible(False)
  if v.startswith('$q='):t.set_visible(False)
  # One row of closely paired keys leaves space for the target definition.
  if v=='recorded node (M = 3)':t.set_text('Recorded node');t.set_position((14.6,49.6));t.set_fontsize(8.6)
  if v=='stimulated node':t.set_text('Stimulated node');t.set_position((14.6,44.6));t.set_fontsize(8.6)
  if v.startswith('response readout'):t.set_text('Response readout (one shown)');t.set_position((14.6,39.6));t.set_fontsize(8.6)
  if v=='19':t.set_position((142,90.5))
  if v=='of 40 favour prior averaging;':t.set_position((151,91.7));t.set_fontsize(8.0)
  if v=='21 favour nominal':t.set_position((151,88.9));t.set_fontsize(8.0)
  if v=='Single response':t.set_color('#A34E79')
  if v=='MSE-forecast score difference':t.set_text('MSE-forecast score difference');t.set_color('#984775');t.set_fontsize(8.2);t.set_transform(base.transData);t.set_position((142,67.9))
  if v.startswith('−0.46'):
   t.set_transform(base.transData);t.set_position((142,63.5))
  # Numerical/statistical typography is separate from the body font.
  if t.get_color()=='#15202B':t.set_color('#2E2531')
  if v=='response readout':t.set_text('Response readout (one shown)')
 # Shared frame and legend grid, retaining the original circular network.
 for patch in base.patches:
  if isinstance(patch,Circle):
   x,y=patch.center
   if abs(patch.get_radius()-1.45)<.01:
    if abs(y-57.5)<.01:patch.center=(11.4,49.6)
    elif abs(y-53.1)<.01:patch.center=(11.4,44.6);patch.set_facecolor('#FFF6DD')
    elif abs(y-48.7)<.01:patch.center=(11.4,39.6)
   if abs(x-30)<.01 and abs(y-104)<.01:patch.set_facecolor('#FFF6DD')
 for line_ in base.lines:
  if list(line_.get_ydata())==[114.6,114.6]:line_.set_ydata([113.5,113.5])
 base.text(8,122.2,'in partially observed neural networks',fontsize=15.5,color='#2E2531',va='center',fontfamily='BentonSans')
 base.text(8,60.8,'12 simulated units · M=3',fontsize=8.6,color='#2E2531',fontweight='bold',va='center',fontfamily='BentonSans')
 base.text(8,56.8,'Known connectivity; uncertain physiology',fontsize=8.0,color='#655D69',va='center',fontfamily='BentonSans')
 base.text(142,77.1,'v: MSE forecast; e: response error',fontsize=7.3,color='#655D69',va='center',fontfamily='BentonSans')
 # New precision notes sit inside retained summary frame, not a footer stripe.
 base.text(51.2,75.5,'q',fontsize=10.5,color='#65566F',va='center',fontfamily='Times New Roman')
 base.add_patch(FancyBboxPatch((8,17.2),44.5,17.6,boxstyle='round,pad=0,rounding_size=1.1',facecolor='#FAF7F8',edgecolor='#DED5DC',lw=.6))
 base.text(10.4,31.5,'Integrated stimulus response',fontsize=8.5,color='#2E2531',fontweight='bold',va='center',fontfamily='BentonSans')
 base.text(30.25,26.2,r'$q=\int\Delta r(t)\,dt$',fontsize=11.5,color='#2E2531',va='center',ha='center',fontfamily='Times New Roman')
 # Typeset colour only on the stimulus term, using measured widths.
 segments=[(r'$\Delta r(t)=$','#2E2531'),(r'$r_{\mathrm{stim}}(t)$','#D4A239'),(r'$-r_{\mathrm{control}}(t)$','#2E2531')]
 temp=[base.text(0,21.0,st,fontsize=9.0,color=co,va='center',fontfamily='Times New Roman') for st,co in segments]
 fig.canvas.draw();renderer=fig.canvas.get_renderer()
 widths=[t.get_window_extent(renderer).width/base.bbox.width*190 for t in temp]
 cursor=30.25-sum(widths)/2
 for t,width in zip(temp,widths):t.set_x(cursor);cursor+=width
 base.text(142,81.8,r'$S(v,e)=\log v+e^2/v$',fontsize=11.5,color='#655D69',va='center',fontfamily='Times New Roman')
 base.text(142,73.1,'One network contributes 64%\nof the summed score difference',fontsize=7.4,color='#655D69',va='center',fontfamily='BentonSans',linespacing=1.2)
 base.text(8,53.3,'Blue: positive; orange: negative connections',fontsize=6.9,color='#655D69',va='center',fontfamily='BentonSans')
 base.text(59,20.5,'all favouring prior averaging. Intervals are unadjusted; one point estimate favours nominal.',fontsize=8.2,color='#655D69',va='center',fontfamily='BentonSans')
 optical=runpy.run_path(str(OUT/'optical_grid.py'))['optical_grid'](fig,base)
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
 statistical_lines=[{'x':list(map(float,line.get_xdata())),'y':list(map(float,line.get_ydata())),'ylim':list(a.get_ylim())} for a in fig.axes[1:] for line in a.lines]
 assert all(min(z['y'])>=min(z['ylim']) and max(z['y'])<=max(z['ylim']) for z in statistical_lines),'Statistical mark clipped by plot range'
 (OUT/'current_audit.json').write_text(json.dumps({'text_overlaps':overlaps,'statistical_lines':statistical_lines,'texts':B,'baseline':str(SRC),'geometry':'Original Claude v4 coordinate system; physical canvas 260 x 185 mm','optical_grid':optical},indent=2))
 from matplotlib.transforms import Bbox
 crop=Bbox.from_extents(0,(12.7/135)*(185/25.4),260/25.4,185/25.4)
 for e in ['png','pdf','svg']:fig.savefig(OUT/f'graphical_abstract_current.{e}',dpi=300,facecolor=fig.get_facecolor(),bbox_inches=crop)
 plt.close(fig)
 print(json.dumps({'overlaps':overlaps},ensure_ascii=False))
ns['export']=export
ns['_graphical_abstract']()
