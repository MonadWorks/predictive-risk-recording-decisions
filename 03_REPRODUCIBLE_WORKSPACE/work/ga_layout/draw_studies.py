from pathlib import Path
import os,csv,json
os.environ['MPLBACKEND']='Agg'
ROOT=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026')
os.environ['MPLCONFIGDIR']=str(ROOT/'work/ga_layout/mpl')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,FancyArrowPatch,FancyBboxPatch,Rectangle
from matplotlib import font_manager as fm
from matplotlib.text import Text
for p in (ROOT/'outputs/pastel_figure_suite/fonts').glob('*.ttf'):fm.fontManager.addfont(str(p))
for n in ['Times New Roman','Times New Roman Italic']:
 p=Path('/System/Library/Fonts/Supplemental')/(n+'.ttf')
 if p.exists():fm.fontManager.addfont(str(p))
plt.rcParams.update({'font.family':'BentonSans','pdf.fonttype':42,'svg.fonttype':'none','mathtext.fontset':'custom','mathtext.rm':'Times New Roman','mathtext.it':'Times New Roman:italic'})
OUT=ROOT/'outputs/graphical_abstract_proposal';SRC=ROOT/'work/evidence/ICBR2026_v4_pack/05_data_and_code'
manifest=json.loads((SRC/'fig1_data/manifest.json').read_text())
weights=np.zeros((12,12))
for r in csv.DictReader((SRC/'fig1_data/weights.csv').open()):weights[int(r['postsynaptic_node']),int(r['presynaptic_node'])]=float(r['weight'])
W,H=240,170
INK='#2E2932';MUTED='#6D6871';RULE='#DFDDE1';ROSE='#C25E88';PALE='#F4DCE6';AMBER='#DB9A1D';PLUM='#66546C'
reports={}
for variant in ['neutral','soft_rose']:
 fig=plt.figure(figsize=(W/25.4,H/25.4),facecolor='white',dpi=150)
 ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,W),ylim=(0,H));ax.axis('off')
 texts=[]
 def T(x,y,s,size=8,weight='normal',color=INK,ha='left',family='BentonSans',**kw):
  t=ax.text(x,y,s,fontsize=size,fontweight=weight,color=color,ha=ha,va='center',fontfamily=family,linespacing=1.27,**kw);texts.append(t);return t
 def line(points,c=RULE,lw=.7,ls='-'):ax.plot(*zip(*points),color=c,lw=lw,ls=ls,zorder=1)
 def arrow(a,b,c=MUTED,lw=.85,style='-|>'):
  ax.add_patch(FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=7.5,lw=lw,color=c,shrinkA=0,shrinkB=0,zorder=2))
 def box(x,y,w,h,label,size=8,fill='#FAF9FA',edge=RULE):
  ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=1.5',facecolor=fill,edgecolor=edge,lw=.7,zorder=0))
  return T(x+w/2,y+h/2,label,size,ha='center')
 T(8,157,'Predictive risk and recording decisions',15,'bold')
 T(8,147.5,'Does prior averaging improve neural stimulus-response prediction?',9.2,color=MUTED)
 line([(8,140),(232,140)])
 # Context/network: preserve every signed nonzero connection from the old v4 source.
 T(8,132,'Known connectivity',9.4,'bold')
 T(8,126.8,'Uncertain neuronal physiology',7.7,color=MUTED)
 cx,cy,R=35,99.5,19.5
 angles=np.pi/2-2*np.pi*np.arange(12)/12
 pos=np.c_[cx+R*np.cos(angles),cy+R*np.sin(angles)]
 if variant=='soft_rose':ax.add_patch(Circle((cx,cy),25.7,fc='#FEF8FA',ec='none',zorder=-1))
 for i in range(12):
  for j in range(12):
   if i!=j and weights[i,j]!=0:
    alpha=.10+.32*abs(weights[i,j])/abs(weights).max()
    ax.add_patch(FancyArrowPatch(pos[j],pos[i],connectionstyle='arc3,rad=.14',arrowstyle='-',lw=.48,color=ROSE if weights[i,j]>0 else PLUM,alpha=alpha,shrinkA=4,shrinkB=4,zorder=0))
 for i,(x,y) in enumerate(pos):
  if i in manifest['selected_nodes']:fc,ec,r=ROSE,'white',2.7
  elif i==manifest['stim']:fc,ec,r='white',AMBER,2.7
  elif i==manifest['readout']:fc,ec,r='white',PLUM,2.7
  else:fc,ec,r='#E9E7EB','#C8C3CB',2.15
  ax.add_patch(Circle((x,y),r,fc=fc,ec=ec,lw=1.15 if i in [manifest['stim'],manifest['readout']] else .7,zorder=3))
 # Small external callouts with neutral leader lines.
 T(44,119,'stimulus',7.1,color=MUTED);line([(40,118),(38,118)],AMBER,.65)
 T(59,85.8,'q',9,family='Times New Roman');line([(55.5,87),(53.5,89)],PLUM,.65)
 T(35,99.5,'12 units',8,ha='center',color=MUTED)
 for y,fill,edge,label in [(72,ROSE,'white','3 recorded units'),(66.8,'white',AMBER,'stimulus'),(61.6,'white',PLUM,'unrecorded readout')]:
  ax.add_patch(Circle((10,y),1.25,fc=fill,ec=edge,lw=1))
  T(14,y,label,7.1,color=MUTED)
 T(8,55.5,'J5000: fixed example network',6.4,color=MUTED)
 T(8,51.7,'Connections: rose + / plum −',6.1,color=MUTED)
 # A: decision study, no arrow to independent forecast study.
 T(82,132,'Recording decisions',10,'bold')
 T(232,132,'40 independent networks',7.2,color=MUTED,ha='right')
 T(100,125,'Risk criterion',7,color=MUTED,ha='center')
 T(139.5,125,'Selected sites',7,color=MUTED,ha='center')
 box(82,113.5,36,9,'Nominal',7.6,fill='white')
 box(82,101,36,9,'Prior-averaged',7.6,fill='#FCF3F7' if variant=='soft_rose' else 'white',edge='#D6B2C2')
 # Same selected set is an explicit illustrative case, not aggregate data.
 for y,filled in [(118,[1,5,9]),(105.5,[1,5,9])]:
  for k in range(12):ax.add_patch(Circle((125+k*2.6,y),.8,fc=ROSE if k in filled else '#DCD8DF',ec='none'))
  arrow((118,y),(122.5,y))
  line([(155.5,y),(160.5,y)],MUTED,.8)
 line([(160.5,105.5),(160.5,118)],MUTED,.8);arrow((160.5,111.75),(166,111.75))
 box(166,103.25,26,17,'Common\nMAP fit',8)
 arrow((192,111.75),(201,111.75))
 box(201,103.25,31,17,'Response\nerror',8)
 T(139.5,97,'Illustrative identical sets',6.3,color=MUTED,ha='center')
 T(174,91.8,'Same recordings imply identical point predictions',7.1,color=MUTED,ha='center')
 # B
 T(82,82.5,'Risk forecasts',10,'bold')
 T(232,82.5,'40 new independent networks',7.2,color=MUTED,ha='right')
 box(82,58.5,70,17,'Fixed recordings, data\nand point prediction',8,fill='#F7F6F8')
 for y in [72.5,61.5]:
  line([(152,67),(157,67),(157,y)],MUTED,.75);arrow((157,y),(163,y))
 T(183,72.5,'Nominal risk',7.4,ha='center')
 T(183,61.5,'Prior-averaged risk',7.4,ha='center')
 for y in [72.5,61.5]:line([(201,y),(205,y)],MUTED,.75)
 line([(205,61.5),(205,72.5)],MUTED,.75);arrow((205,67),(210,67))
 box(210,58.5,22,17,'Forecast\nscore',7.7)
 # Evidence band, one continuum separated by rules rather than cards.
 line([(8,49),(232,49)])
 cols=[8,85,162]
 T(8,43.4,'Often the same recordings',8.4,'bold')
 T(85,43.4,'Mean-MSE change (%)',8.4,'bold')
 T(162,43.4,'Forecast score',8.4,'bold')
 T(8,36.3,'82/120 single-target designs',7.7)
 T(8,30.8,'26/40 shared designs',7.7)
 T(8,25.2,'Identical nominal / prior-averaged sets',6.5,color=MUTED)
 # Font-specific role: monospaced values, regular labels above.
 T(85,36.3,'−3.7% [−18.5, +12.1]',7.5,family='JuliaMono')
 T(85,30.8,'+2.7% [ −3.0, +11.5]',7.5,family='JuliaMono')
 T(85,25.2,'Single / shared objective · 97.5% CI',6.5,color=MUTED)
 T(162,36.3,'−0.46 [−1.16, +0.02]',7.5,family='JuliaMono')
 T(162,30.8,'95% CI · mean influenced by one network',6.5,color=MUTED)
 T(162,25.2,'All effects: prior-averaged minus nominal',6.5,color=MUTED)
 line([(78,26),(78,45)],RULE,.6);line([(155,26),(155,45)],RULE,.6)
 T(8,17,'Primary improvements remain uncertain; decisions and forecasts require separate evaluation.',8.5,'bold')
 line([(8,12),(232,12)],RULE,.65)
 T(8,7,'Jiayi Du & Shuaizhi Cheng · Equal contribution',6.8,color=MUTED)
 T(232,7,'Simulation study · known connectivity',6.8,color=MUTED,ha='right')
 fig.canvas.draw();rend=fig.canvas.get_renderer();bounds=[]
 for t in texts:
  b=t.get_window_extent(rend);xy=ax.transData.inverted().transform([[b.x0,b.y0],[b.x1,b.y1]])
  bounds.append(dict(text=t.get_text(),font=t.get_fontfamily(),weight=t.get_fontweight(),size_pt=t.get_fontsize(),bbox_mm=xy.tolist(),width_mm=float(xy[1,0]-xy[0,0])))
 overlaps=[]
 for i,a in enumerate(bounds):
  for b in bounds[i+1:]:
   x,y=a['bbox_mm'];u,v=b['bbox_mm']
   if min(y[0],v[0])-max(x[0],u[0])>.15 and min(y[1],v[1])-max(x[1],u[1])>.15:overlaps.append([a['text'],b['text']])
 off=[b['text'] for b in bounds if b['bbox_mm'][0][0]<0 or b['bbox_mm'][0][1]<0 or b['bbox_mm'][1][0]>W or b['bbox_mm'][1][1]>H]
 reports[variant]=dict(texts=bounds,text_overlaps=overlaps,off_canvas=off,network_id=manifest['network_id'],weight_entries_preserved=int(np.count_nonzero(weights)),width_mm=W,height_mm=H)
 for ext in ['pdf','svg','png']:fig.savefig(OUT/f'layout_{variant}.{ext}',dpi=240,facecolor='white')
 plt.close(fig)
(OUT/'layout_measurements.json').write_text(json.dumps(reports,indent=2))
print({k:{'overlaps':v['text_overlaps'],'off_canvas':v['off_canvas']} for k,v in reports.items()})
