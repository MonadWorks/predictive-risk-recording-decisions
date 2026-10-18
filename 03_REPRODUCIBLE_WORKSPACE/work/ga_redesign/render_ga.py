from pathlib import Path
import os,csv,json,hashlib
ROOT=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026')
os.environ['MPLBACKEND']='Agg';os.environ['MPLCONFIGDIR']=str(ROOT/'work/ga_redesign/mpl')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,FancyArrowPatch
from matplotlib import font_manager as fm
from matplotlib.text import Text
OUT=ROOT/'outputs/graphical_abstract_redesign'; DATA=ROOT/'work/evidence/ICBR2026_v4_pack/05_data_and_code'
for p in (ROOT/'outputs/pastel_figure_suite/fonts').glob('*.ttf'):fm.fontManager.addfont(str(p))
for n in ['Times New Roman','Times New Roman Italic','Times New Roman Bold']:
 p=Path('/System/Library/Fonts/Supplemental')/(n+'.ttf')
 if p.exists():fm.fontManager.addfont(str(p))
plt.rcParams.update({'font.family':'BentonSans','pdf.fonttype':42,'svg.fonttype':'none','mathtext.fontset':'custom','mathtext.rm':'Times New Roman','mathtext.it':'Times New Roman:italic','axes.unicode_minus':True,'axes.linewidth':.5})
def rows(name):return list(csv.DictReader((DATA/name).open()))
M=json.loads((DATA/'fig1_data/manifest.json').read_text());J=np.zeros((12,12))
for r in rows('fig1_data/weights.csv'):J[int(r['postsynaptic_node']),int(r['presynaptic_node'])]=float(r['weight'])
R=rows('fig1_data_extra/heldout_response.csv');time=np.array([float(r['time_model_units']) for r in R]);delta=np.array([float(r['difference_rate_au']) for r in R]);st=np.array([float(r['stimulus_input']) for r in R])
assert abs(.05*delta.sum()-M['q_csv'])<1e-14
agree=rows('source_data/holdout_design_agreement.csv')
counts=[(sum(r['objective']==o and r['identical']=='True' for r in agree),sum(r['objective']==o for r in agree)) for o in ['single_response','three_responses']];assert counts==[(82,120),(26,40)]
effects=[r for r in rows('source_data/holdout_paired_effects.csv') if r['primary']=='True' and r['metric']=='mse'];assert len(effects)==2
effects.sort(key=lambda r:'vector' in r['contrast'])
score=json.loads((DATA/'source_data/forecast_summary.json').read_text())['primary'];S=[score[k] for k in ['score_difference','score_difference_ci_low','score_difference_ci_high']]
ext=[r for r in rows('source_data/n100_paired_effects.csv') if r['metric']=='mse' and r['contrast'] in ['ensemble_scalar - local_scalar','ensemble_vector - local_vector']];assert len(ext)==8
fav=sum(float(r['relative_mse_ci_high'])<0 for r in ext);assert fav==4
INK='#272430';MUTED='#615D68';ROSE='#BD5E86';PALE='#F1CFDE';PLUM='#66516E';AMBER='#D5A02C';GRAY='#C8C1CB';RULE='#DCD7DF'
W,H=260,200
fig=plt.figure(figsize=(W/25.4,H/25.4),facecolor='white',dpi=160);base=fig.add_axes([0,0,1,1]);base.set(xlim=(0,W),ylim=(0,H));base.axis('off')
texts=[]
def T(x,y,s,size=8,weight='normal',color=INK,ha='left',family='BentonSans',**kw):
 t=base.text(x,y,s,fontsize=size,fontweight=weight,color=color,ha=ha,va='center',fontfamily=family,linespacing=1.15,**kw);texts.append(t);return t
def line(p,c=MUTED,lw=.65):base.plot(*zip(*p),color=c,lw=lw,zorder=1)
def arrow(p,q,c=MUTED,lw=.8):base.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=7,lw=lw,color=c,shrinkA=0,shrinkB=0))
def axes(x,y,w,h):
 a=fig.add_axes([x/W,y/H,w/W,h/H]);a.set_facecolor('none');return a
T(8,185,'Predictive Risk and Recording Decisions',18,family='Times New Roman')
T(8,175,'in Partially Observed Neural Networks',18,family='Times New Roman')
T(252,181,'SIMULATION STUDY',7.8,color=MUTED,ha='right')
# Original v4 circular network, exact weights, same node placement.
T(8,159,'Limited recordings',10.5,'bold')
T(8,152,'Known connectivity; uncertain gains and biases',7.8,color=MUTED)
cx,cy,rad=40,123,23
ang=np.pi/2-2*np.pi*np.arange(12)/12;pos=np.c_[cx+rad*np.cos(ang),cy+rad*np.sin(ang)]
for i in range(12):
 for j in range(12):
  if i!=j and J[i,j]!=0:
   base.add_patch(FancyArrowPatch(pos[j],pos[i],connectionstyle='arc3,rad=.14',arrowstyle='-',lw=.55,color=ROSE if J[i,j]>0 else PLUM,alpha=.12+.42*abs(J[i,j])/abs(J).max(),shrinkA=4,shrinkB=4,zorder=0))
for i,(x,y) in enumerate(pos):
 if i in M['selected_nodes']:fill,edge,r=ROSE,'white',3.0
 elif i==M['stim']:fill,edge,r='white',AMBER,3.0
 elif i==M['readout']:fill,edge,r='white',PLUM,3.0
 else:fill,edge,r='#EBE8ED','#C6BFCC',2.45
 base.add_patch(Circle((x,y),r,fc=fill,ec=edge,lw=1.2 if i in [M['stim'],M['readout']] else .65,zorder=3))
T(cx,cy+1,'3 of 12',10,ha='center',family='Times New Roman')
T(cx,cy-4,'recorded',7.5,ha='center',color=MUTED)
T(49,146,'stimulus',7.5,color=MUTED);line([(44,145.8),(47.4,145.8)],AMBER)
T(69,108,'q',10,family='Times New Roman');line([(62.8,110.5),(66.5,108.5)],PLUM)
# inline legend with direct semantics, no broad rules
for x,y,fill,edge,label in [(10,94,ROSE,'white','recorded'),(40,94,'white',PLUM,'readout')]:
 base.add_patch(Circle((x,y),1.35,fc=fill,ec=edge,lw=1));T(x+3.4,y,label,7.5,color=MUTED)
T(8,88,'J5000 example; rose + / plum − connections',6.9,color=MUTED)
T(8,78,'Stimulus-response target',9.2,'bold')
a=axes(9,61,61,12);a.fill_between(time,delta*1e4,0,color=PALE);a.plot(time,delta*1e4,color=PLUM,lw=1);a.axvspan(1,2,color=AMBER,alpha=.13)
a.set_xlim(0,6);a.set_ylim(0,max(delta*1e4)*1.12);a.axis('off')
T(9,58,'0',6.8,color=MUTED);T(70,58,'6',6.8,color=MUTED,ha='right');T(40,58,'model time',6.8,color=MUTED,ha='center')
T(40,50,r'$q=\int [r_{\mathrm{stim}}(t)-r_{\mathrm{control}}(t)]\,dt$',9.1,ha='center',family='Times New Roman')
# recording designs - two criteria with small set glyphs, not boxes
T(90,159,'Recording design',10.5,'bold');T(90,152,'40 independent networks',7.8,color=MUTED)
for y,label,col in [(141,'Nominal',MUTED),(131,'Prior-averaged',ROSE)]:
 T(90,y,label,8.4,color=INK)
 for k in range(12):base.add_patch(Circle((129+k*2.7,y),.85,fc=ROSE if k in [6,8,11] else '#D7D1DA',ec='none'))
 arrow((121,y),(126,y))
T(145,124,'Identical-set illustration',6.8,ha='center',color=MUTED)
T(90,116,'Identical recording sets',8.4,'bold')
T(90,109,'82/120 single-response designs',8.1)
T(90,103,'26/40 shared designs',8.1)
T(90,94,'Response error after MAP fitting',9,'bold')
T(90,88,'Same recording budget, pool and estimator',7.2,color=MUTED)
def main_forest(y,r,label,col,marker):
 m,lo,hi=[100*float(r[k]) for k in ['relative_mse_difference','relative_mse_ci_low','relative_mse_ci_high']]
 a=axes(91,y,72,8);a.set_xlim(-22,16);a.set_ylim(-1,1);a.axvline(0,color='#918798',lw=.7,ls=(0,(2,2)))
 a.plot([lo,hi],[0,0],color=col,lw=1.7);a.plot([lo,lo],[-.23,.23],color=col,lw=.8);a.plot([hi,hi],[-.23,.23],color=col,lw=.8);a.plot(m,0,marker,ms=5,mfc=col,mec='white',mew=.65)
 a.axis('off');T(90,y+11,label,8.1,'bold');T(164,y-2.8,f'{m:+.1f}% [{lo:+.1f}, {hi:+.1f}]'.replace('-','−'),7.4,ha='right',family='JuliaMono')
 return m,lo,hi
main_forest(72,effects[0],'Single response',ROSE,'o');main_forest(52,effects[1],'Shared three-response',PLUM,'s')
T(90,44,'97.5% network-cluster CIs; zero shown dashed',6.9,color=MUTED)
# Independent forecast study
T(180,159,'Risk forecasts',10.5,'bold');T(180,152,'40 new independent networks',7.8,color=MUTED)
T(180,141,'Fixed recordings, data',8.5);T(180,135,'and point prediction',8.5)
for x,label,col,filled in [(190,'Nominal',MUTED,False),(232,'Prior-averaged',ROSE,True)]:
 base.add_patch(Circle((x,121),1.8,fc=col if filled else 'white',ec=col,lw=1))
 T(x,114,label,8.1,ha='center')
line([(190,117.8),(190,104),(211,104)]);line([(232,117.8),(232,104),(211,104)]);arrow((211,104),(211,99))
T(211,94,'MSE-forecast score',8.8,'bold',ha='center')
T(211,86,r'$\log v+e^2/v$',11,ha='center',family='Times New Roman')
T(211,78,'v: forecast MSE; e: response error',7.1,ha='center',color=MUTED)
a=axes(181,61,70,10);a.set_xlim(-1.4,.3);a.set_ylim(-1,1);a.axvline(0,color='#918798',lw=.7,ls=(0,(2,2)));m,lo,hi=S
a.plot([lo,hi],[0,0],color=PLUM,lw=1.8);a.plot([lo,lo],[-.22,.22],color=PLUM,lw=.8);a.plot([hi,hi],[-.22,.22],color=PLUM,lw=.8);a.plot(m,0,'D',ms=5,mfc=PLUM,mec='white',mew=.6);a.axis('off')
T(211,57,'−0.46 [−1.16, +0.02]',8,ha='center',family='JuliaMono')
T(211,51.5,'95% network-cluster CI',7.1,ha='center',color=MUTED)
T(211,45.5,'Mean influenced by one network',7.1,ha='center',color=MUTED)
# exploratory extension: all eight settings, shared axes, no giant percentage.
T(8,36,'100-unit rank-two extension',9.5,'bold')
T(8,29,'8 independent networks; exploratory',7.7)
T(8,22,'4/8 settings favour prior averaging;',7.8)
T(8,16,'one point estimate reverses sign.',7.8)
T(158,38,'Single response',7.7,'bold',ha='center');T(228,38,'Shared three-response',7.7,'bold',ha='center')
configs=[('all',5),('all',10),('exclude_endpoints',5),('exclude_endpoints',10)]
for i,(pool,budget) in enumerate(configs):T(130,32.5-i*5,f'{"All sites" if pool=="all" else "Excluded"}, {budget}',6.8,color=MUTED,ha='right')
for x,vector in [(136,False),(206,True)]:
 a=axes(x,14,46,21);a.set_xlim(-110,220);a.set_ylim(-.5,3.5);a.axvline(0,color='#918798',lw=.6,ls=(0,(2,2)))
 for i,(pool,budget) in enumerate(configs):
  rr=[r for r in ext if r['pool']==pool and int(r['budget'])==budget and ('vector' in r['contrast'])==vector]
  assert len(rr)==1,(pool,budget,vector)
  rr=rr[0];m,lo,hi=[100*float(rr[k]) for k in ['relative_mse_difference','relative_mse_ci_low','relative_mse_ci_high']];col=PLUM if vector else ROSE
  sig=hi<0 or lo>0;a.plot([lo,hi],[3-i]*2,color=col,lw=1);a.plot(m,3-i,'s' if vector else 'o',ms=3.2,mfc=col if sig else 'white',mec=col,mew=.7)
 a.axis('off')
T(252,9.8,'Mean-MSE change (%) · unadjusted 95% CIs',6.8,color=MUTED,ha='right')
T(8,5,'Jiayi Du & Shuaizhi Cheng · Equal contribution',6.8,color=MUTED)
# Role/scale labels replace a promotional conclusion strip.
T(163,166,'Prior-averaged minus nominal; negative favours prior averaging',7.0,color=MUTED,ha='right')
fig.canvas.draw();renderer=fig.canvas.get_renderer();B=[]
for t in fig.findobj(Text):
 if not t.get_visible() or not t.get_text().strip():continue
 b=t.get_window_extent(renderer);p=base.transData.inverted().transform([[b.x0,b.y0],[b.x1,b.y1]])
 B.append(dict(text=t.get_text(),bbox_mm=p.tolist(),size=t.get_fontsize(),font=t.get_fontfamily(),weight=t.get_fontweight()))
overlaps=[]
for i,a in enumerate(B):
 for b in B[i+1:]:
  p,q=a['bbox_mm'];r,s=b['bbox_mm']
  if min(q[0],s[0])-max(p[0],r[0])>.25 and min(q[1],s[1])-max(p[1],r[1])>.25:overlaps.append([a['text'],b['text']])
report={'canvas_mm':[W,H],'text_overlaps':overlaps,'text_off_canvas':[a['text'] for a in B if a['bbox_mm'][0][0]<0 or a['bbox_mm'][1][0]>W or a['bbox_mm'][0][1]<0 or a['bbox_mm'][1][1]>H],'texts':B,'recording_counts':counts,'extension_settings':len(ext),'favourable_extension_settings':fav,'network_id':M['network_id'],'q_verified':M['q_csv'],'source_sha256':{str(p.relative_to(DATA)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [DATA/'fig1_data/weights.csv',DATA/'fig1_data_extra/heldout_response.csv',DATA/'source_data/holdout_paired_effects.csv',DATA/'source_data/n100_paired_effects.csv']}}
(OUT/'round1_audit.json').write_text(json.dumps(report,indent=2))
for ext in ['png','pdf','svg']:fig.savefig(OUT/f'graphical_abstract_round1.{ext}',dpi=250,facecolor='white')
print(json.dumps({'overlaps':overlaps,'off_canvas':report['text_off_canvas']},ensure_ascii=False))
