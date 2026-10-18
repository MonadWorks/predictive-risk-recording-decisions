"""Local revision of Claude v5: retain encodings and frozen values.
Global millimetre anchors, not axes-relative panel-label coordinates.
No third-party plotting code copied; matplotlib + numpy only.
"""
from pathlib import Path
import os,csv,json,hashlib,shutil,subprocess
H=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(H/'.cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.text import Text
from matplotlib.ticker import NullLocator
import numpy as np
D=H/'source_data'; S=H.parent.parent/'work/evidence/ICBR2026_v4_pack/05_data_and_code/source_data'
for n in ['holdout_design_agreement.csv','holdout_paired_effects.csv','fig2_network_pairs.csv','fig3_networks.csv','forecast_summary.json']:
 if not (D/n).exists():shutil.copy2(S/n,D/n)
def rows(n):return list(csv.DictReader((D/n).open()))
INK='#20262D';MUTED='#59636E';GREY='#C7C9CC';SCALAR='#2A3BCC';VECTOR='#DC4F1E';FORECAST='#8A2F7A'
plt.rcParams.update({'font.family':'Arial','font.size':7,'axes.labelsize':7,'xtick.labelsize':6.5,'ytick.labelsize':6.5,'axes.linewidth':.6,'axes.spines.top':False,'axes.spines.right':False,'xtick.major.size':2.5,'ytick.major.size':2.5,'xtick.major.width':.6,'ytick.major.width':.6,'pdf.fonttype':42,'svg.fonttype':'none','mathtext.fontset':'custom','mathtext.rm':'Arial','mathtext.it':'Arial:italic','mathtext.bf':'Arial:bold','text.color':INK,'axes.labelcolor':INK,'axes.edgecolor':INK,'xtick.color':INK,'ytick.color':INK,'figure.facecolor':'white','savefig.facecolor':'white'})
QA={}
def canvas(height):
 f=plt.figure(figsize=(180/25.4,height/25.4));f._h=height;f._anchors=[];return f
def txt(f,x,y,s,size=7,weight='normal',**kw):
 t=f.text(x/180,y/f._h,s,fontsize=size,fontweight=weight,va=kw.pop('va','baseline'),**kw);t._manual=True;return t
def header(f,x,y,l,s):
 a=txt(f,x,y,l,8,'bold');b=txt(f,x+5,y,s,7)
 f._anchors.append({'letter':l,'letter_x_mm':x,'title_x_mm':x+5,'baseline_y_mm':y})
def ax(f,x,y,w,h):return f.add_axes([x/180,y/f._h,w/180,h/f._h])
def export(f,name):
 f.canvas.draw();ren=f.canvas.get_renderer(); manual=[t for t in f.findobj(Text) if getattr(t,'_manual',False)]; collisions=[]
 for i,t in enumerate(manual):
  bt=t.get_window_extent(ren)
  for u in manual[i+1:]:
   bu=u.get_window_extent(ren)
   if bt.overlaps(bu):collisions.append([t.get_text(),u.get_text()])
 assert not collisions,collisions
 alltext=[t for t in f.findobj(Text) if t.get_visible() and t.get_text()]
 outside=[]
 for t in alltext:
  b=t.get_window_extent(ren)
  if b.x0<0 or b.y0<0 or b.x1>f.bbox.width or b.y1>f.bbox.height:outside.append(t.get_text())
 assert not outside,outside
 allcollisions=[]
 for i,t in enumerate(alltext):
  bt=t.get_window_extent(ren)
  for u in alltext[i+1:]:
   bu=u.get_window_extent(ren)
   if bt.overlaps(bu):allcollisions.append([t.get_text(),u.get_text()])
 assert not allcollisions,allcollisions
 for ext in ['pdf','svg','png']:f.savefig(H/f'{name}.{ext}',dpi=300,bbox_inches=None)
 # Grid proof is separate from the scientific figure.
 for x in sorted(set(a['letter_x_mm'] for a in f._anchors)):
  f.add_artist(plt.Line2D([x/180,x/180],[0,1],transform=f.transFigure,color='#D47D9D',lw=.4,alpha=.6))
 for y in sorted(set(a['baseline_y_mm'] for a in f._anchors)):
  f.add_artist(plt.Line2D([0,1],[y/f._h,y/f._h],transform=f.transFigure,color='#D47D9D',lw=.4,alpha=.6))
 f.savefig(H/f'{name}_alignment.png',dpi=140)
 QA[name]={'panel_anchors':f._anchors,'axes_mm':[[round(v*k,4) for v,k in zip(a.get_position().bounds,[180,f._h,180,f._h])] for a in f.axes],'manual_text_collisions':collisions,'all_visible_text_collisions':allcollisions,'out_of_canvas_text':outside,'font_pt_range':[min(t.get_fontsize() for t in alltext),max(t.get_fontsize() for t in alltext)],'dimensions_mm':[180,f._h]}
 plt.close(f)
ag=rows('holdout_design_agreement.csv');pairs=rows('fig2_network_pairs.csv');ef={}
for r in rows('holdout_paired_effects.csv'):
 if r['primary']=='True' and r['metric']=='mse':ef['scalar' if 'scalar' in r['contrast'] else 'vector']=np.array([float(r[k])*100 for k in ['relative_mse_difference','relative_mse_ci_low','relative_mse_ci_high']])
assert np.allclose(ef['scalar'],[-3.74,-18.48,12.12],atol=.005) and np.allclose(ef['vector'],[2.69,-2.95,11.51],atol=.005)
assert len(pairs)==80 and sum(float(r['descriptive_log2_ratio'])==0 for r in pairs)==39
f=canvas(110); header(f,4,104,'a','Recording sets: nominal vs ensemble');header(f,94,104,'b','Network error (40 per objective)');header(f,4,43,'c','Primary comparisons (40 independent networks)')
# Preserve the unit dot arrays: 120 designs remain nested in 40 networks.
for top,n,same,obj,title,col in [(88,120,82,'single_response','Single-response designs',SCALAR),(58,40,26,'three_responses','Shared three-response designs',VECTOR)]:
 own=[r for r in ag if r['objective']==obj];assert len(own)==n and sum(r['identical']=='True' for r in own)==same
 txt(f,9,top+7,title);txt(f,9,top+3.3,f'{same}/{n} identical; {3 if n==120 else 1} design'+('s' if n==120 else '')+' per network',6)
 for k in range(n):
  row,cl=divmod(k,15);f.add_artist(Circle(((10+cl*2.55)/180,(top-row*2.55)/110),radius=.85/180,transform=f.transFigure,facecolor=GREY if k<same else col,edgecolor='none'))
# Figure-level circles need equal physical radii: use Ellipse rather than Circle figure aspect.
from matplotlib.patches import Ellipse
for patch in list(f.artists):
 if isinstance(patch,Circle):
  x,y=patch.center;fc=patch.get_facecolor();patch.remove();f.add_artist(Ellipse((x,y),1.7/180,1.7/110,transform=f.transFigure,facecolor=fc,edgecolor='none'))
f.add_artist(Ellipse((10/180,49/110),1.7/180,1.7/110,transform=f.transFigure,facecolor=GREY,edgecolor='none'))
txt(f,12,48.3,'Same set',6.5)
for x,c in [(34,SCALAR),(37,VECTOR)]:f.add_artist(Ellipse((x/180,49/110),1.7/180,1.7/110,transform=f.transFigure,facecolor=c,edgecolor='none'))
txt(f,39,48.3,'Changed set',6.5)
b=ax(f,110,68,65,27);rng=np.random.default_rng(7)
for k,(name,col,mk) in enumerate([('Three responses',VECTOR,'s'),('Single response',SCALAR,'o')]):
 v=np.array([float(r['descriptive_log2_ratio']) for r in pairs if r['objective']==name]);yy=k+rng.uniform(-.2,.2,len(v));same=v==0
 b.scatter(v[~same],yy[~same],s=15,marker=mk,c=col,edgecolor='white',linewidth=.4,zorder=3)
 b.scatter([0],[k],s=40,marker=mk,facecolor='white',edgecolor=MUTED,lw=.9,zorder=2)
 b.text(2.25,k,f'{sum(same)}/40 equal',ha='right',va='center',fontsize=6.5,color=INK)
b.axvline(0,color=MUTED,lw=.7,ls=(0,(3,3)),zorder=0)
b.set(xlim=(-.75,2.3),ylim=(-.6,1.6),xticks=[-.5,0,.5,1,1.5],yticks=[0,1],yticklabels=['Shared','Single'],xlabel='log$_2$(ensemble MSE / nominal MSE)')
b.spines['left'].set_visible(False);b.tick_params(axis='y',length=0)
txt(f,110,56,'Equal MSE: networks overlap at zero (open marker)',6)
# Explicit common rows for category, effect and numeric columns.
c=ax(f,44,14,79,22);c.axvline(0,color=MUTED,lw=.7,ls=(0,(3,3)))
c.set(xlim=(-22,16),ylim=(-.6,1.6),yticks=[],xticks=[-20,-10,0,10],xlabel='Relative mean-MSE change, ensemble vs nominal (%)')
c.spines['left'].set_visible(False)
for y,key,label,col,mk in [(1,'scalar','Single response',SCALAR,'o'),(0,'vector','Shared response',VECTOR,'s')]:
 m,lo,hi=ef[key];c.errorbar(m,y,xerr=[[m-lo],[hi-m]],fmt=mk,color=col,lw=1.1,ms=4,capsize=2)
 y_mm=14+(y+.6)/2.2*22
 txt(f,9,y_mm,label,7,va='center');txt(f,130,y_mm,f'{m:+.2f} [{lo:+.2f}, {hi:+.2f}]',6.5,va='center')
txt(f,130,38,'Estimate [97.5% CI]',6.5)
txt(f,130,14,'Both intervals include zero',6)
txt(f,9,38,'Paired network-cluster intervals',6)
export(f,'recording_decisions_revised')
# Second study: same pairs and score comparisons, a spanning two logical rows.
net=rows('fig3_networks.csv');fc=json.loads((D/'forecast_summary.json').read_text())['primary'];diff=np.array([float(r['score_difference']) for r in net]);assert len(net)==40 and sum(diff<0)==19
assert np.isclose(diff.mean(),fc['score_difference'])
f=canvas(100);header(f,4,94,'a','Forecast risk and actual MSE');header(f,94,94,'b','Network-level score differences');header(f,94,37,'c','Mean score difference')
a=ax(f,20,18,61,68);b=ax(f,108,56,67,30);c=ax(f,108,18,67,13)
for i,r in enumerate(net):
 n,e,m=[float(r[k]) for k in ['nominal_risk','ensemble_risk','raw_mse']]
 a.plot([n,e],[m,m],color=GREY,lw=.6,zorder=0)
 a.scatter(n,m,s=15,facecolor='white',edgecolor=FORECAST,lw=.8,label='Nominal' if i==0 else None,zorder=2)
 a.scatter(e,m,s=15,facecolor=FORECAST,edgecolor='white',lw=.35,label='Ensemble' if i==0 else None,zorder=3)
a.plot([3e-8,3e-2],[3e-8,3e-2],color=MUTED,lw=.7,ls=(0,(3,3)),zorder=0)
a.set(xscale='log',yscale='log',xlim=(3e-8,3e-2),ylim=(3e-8,3e-2),xlabel='Forecast risk (q²)',ylabel='Actual MSE (q²)')
for axis in [a.xaxis,a.yaxis]:axis.set_ticks([1e-7,1e-5,1e-3]);axis.set_minor_locator(NullLocator())
a.legend(loc='upper left',frameon=False,fontsize=6.5,handletextpad=.3)
a.text(.97,.04,'Below line: forecast exceeds MSE',transform=a.transAxes,fontsize=6,ha='right',va='bottom')
order=np.argsort(diff);yy=39-np.arange(40);clip=-3.4
b.barh(yy,np.maximum(diff[order],clip),height=.75,color=[FORECAST if v<0 else GREY for v in diff[order]])
b.axvline(0,color=MUTED,lw=.7,ls=(0,(3,3)))
for j in np.where(diff[order]<clip)[0]:
 for dx in [-3.17,-3.05]:b.plot([dx-.05,dx+.05],[yy[j]-.5,yy[j]+.5],color='white',lw=1.1)
 b.text(.12,yy[j],f'{diff[order][j]:.2f}*',fontsize=6,va='center')
b.set(xlim=(-3.6,1.6),ylim=(-1,41),xticks=[-3,-2,-1,0,1],yticks=[],xlabel='Ensemble − nominal score');b.spines['left'].set_visible(False)
txt(f,108,46,'40 networks: 19 lower; 21 higher.  *Clipped at −3.4.',6)
txt(f,108,43,'One network: 64% of net summed score difference.',6)
m,lo,hi=[fc[k] for k in ['score_difference','score_difference_ci_low','score_difference_ci_high']]
c.axvline(0,color=MUTED,lw=.7,ls=(0,(3,3)))
c.errorbar(m,0,xerr=[[m-lo],[hi-m]],fmt='D',color=INK,lw=1.1,capsize=2,ms=4)
c.set(xlim=(-1.3,.2),ylim=(-1,1),yticks=[],xticks=[-1.2,-.6,0],xlabel='Ensemble − nominal score');c.spines['left'].set_visible(False)
txt(f,108,34,f'{m:.2f} [{lo:.2f}, {hi:+.2f}], 95% network-cluster CI',6.5)
export(f,'risk_forecast_layout_study')
for name,q in QA.items():
 r=subprocess.run(['pdffonts',str(H/f'{name}.pdf')],capture_output=True,text=True,check=True);q['pdffonts']=r.stdout
 assert all(' yes ' in l for l in r.stdout.splitlines()[2:])
assert QA['recording_decisions_revised']['panel_anchors'][0]['letter_x_mm']==QA['recording_decisions_revised']['panel_anchors'][2]['letter_x_mm']
QA['data_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.iterdir()}
QA['limits']='Manual-text pair overlaps and canvas bounds checked; all data-point collisions require visual review. No statistical intervals recomputed.'
(H/'qa_receipt.json').write_text(json.dumps(QA,indent=2))
print('Rendered two revisions; geometry, frozen values and embedded fonts checked.')
