"""Frozen-data figure redesign. Run with Python + numpy + matplotlib.
White canvas; Arial 7 pt; panel letters 8 pt; no inferred statistics.
Pink=single-response, slate=shared response; forecast criteria use fill/shape.
"""
from pathlib import Path
import os,csv,json,hashlib,shutil,subprocess
HERE=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(HERE/'.mpl-cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.text import Text
from matplotlib.ticker import LogLocator,NullLocator
SOURCE=HERE.parent.parent/'work/evidence/ICBR2026_v4_pack/05_data_and_code/source_data'
D=HERE/'source_data'
for name in ['holdout_design_agreement.csv','holdout_paired_effects.csv','fig2_network_pairs.csv','fig3_networks.csv','forecast_summary.json']:
 if not (D/name).exists():shutil.copy2(SOURCE/name,D/name)
def rows(name):return list(csv.DictReader((D/name).open()))
PINK='#B23A68'; SLATE='#344D67'; GRAY='#D3D5D8'; INK='#20242B'; MUTED='#616974'
plt.rcParams.update({'mathtext.fontset':'custom','mathtext.rm':'Arial','mathtext.it':'Arial:italic','mathtext.bf':'Arial:bold','font.family':'Arial','font.size':7,'axes.labelsize':7,'axes.titlesize':7,'xtick.labelsize':6.5,'ytick.labelsize':6.5,'axes.linewidth':.6,'axes.spines.top':False,'axes.spines.right':False,'xtick.major.width':.6,'ytick.major.width':.6,'xtick.major.size':3,'ytick.major.size':3,'text.color':INK,'axes.labelcolor':INK,'axes.edgecolor':INK,'xtick.color':INK,'ytick.color':INK,'pdf.fonttype':42,'svg.fonttype':'none','figure.facecolor':'white','savefig.facecolor':'white','lines.linewidth':.9})
qa={}
def panel(ax,letter,title):
 ax.text(-.12,1.08,letter,transform=ax.transAxes,fontsize=8,fontweight='bold',va='bottom')
 ax.set_title(title,loc='left',pad=8)
def save(fig,stem):
 fig.canvas.draw();renderer=fig.canvas.get_renderer();bad=[];sizes=[]
 for t in fig.findobj(Text):
  if not t.get_visible() or not t.get_text():continue
  b=t.get_window_extent(renderer);sizes.append(t.get_fontsize())
  if b.x0<-.5 or b.y0<-.5 or b.x1>fig.bbox.width+.5 or b.y1>fig.bbox.height+.5:bad.append(t.get_text())
 assert not bad,(stem,bad)
 for ext in ['png','pdf','svg']:fig.savefig(HERE/f'{stem}.{ext}',dpi=300)
 qa[stem]={'width_mm':180,'height_mm':fig.get_figheight()*25.4,'min_font_pt':min(sizes),'max_font_pt':max(sizes),'out_of_canvas_text':bad}
 plt.close(fig)
agree=rows('holdout_design_agreement.csv');pairs=rows('fig2_network_pairs.csv')
eff={}
for r in rows('holdout_paired_effects.csv'):
 if r['primary']=='True' and r['metric']=='mse':eff['Single response' if 'scalar' in r['contrast'] else 'Shared response']=np.array([float(r[k])*100 for k in ['relative_mse_difference','relative_mse_ci_low','relative_mse_ci_high']])
assert np.allclose(eff['Single response'],[-3.74,-18.48,12.12],atol=.005)
assert np.allclose(eff['Shared response'],[2.69,-2.95,11.51],atol=.005)
assert len(pairs)==80 and sum(float(r['descriptive_log2_ratio'])==0 for r in pairs)==39
fig=plt.figure(figsize=(180/25.4,105/25.4))
a=fig.add_axes([.16,.64,.27,.24]);b=fig.add_axes([.64,.64,.32,.24]);c=fig.add_axes([.23,.19,.59,.21])
panel(a,'a','Recording-set agreement');panel(b,'b','Network-level error ratios');panel(c,'c','Primary aggregate error contrasts')
for y,(obj,label,n,same,col,mk) in enumerate([('three_responses','Shared response',40,26,SLATE,'s'),('single_response','Single response',120,82,PINK,'o')]):
 own=[r for r in agree if r['objective']==obj];assert len(own)==n and sum(r['identical']=='True' for r in own)==same
 a.barh(y,100*same/n,height=.35,color=GRAY)
 a.barh(y,100*(n-same)/n,left=100*same/n,height=.35,color=col)
 a.text(100*same/n/2,y,f'{same}/{n}',ha='center',va='center',fontsize=6.5)
 a.text(100*same/n+100*(n-same)/n/2,y,f'{n-same}/{n}',ha='center',va='center',fontsize=6.5,color='white')
a.set(yticks=[0,1],yticklabels=['Shared response','Single response'],xlim=(0,100),ylim=(-.6,1.6),xticks=[0,50,100],xlabel='Recording designs (%)')
a.spines['left'].set_visible(False);a.tick_params(axis='y',length=0)
a.text(.0,-.62,'Grey: same set   Colour: changed set',transform=a.transAxes,fontsize=6.5)
for y,(name,col,mk) in enumerate([('Three responses',SLATE,'s'),('Single response',PINK,'o')]):
 vals=sorted(float(r['descriptive_log2_ratio']) for r in pairs if r['objective']==name)
 # deterministic stacking, not random jitter; exact zero multiplicities stay explicit
 buckets={}
 for x in vals:
  bucket=round(x/.075);buckets.setdefault(bucket,[]).append(x)
 for vv in buckets.values():
  yy=(np.arange(len(vv))-(len(vv)-1)/2)*.027+y
  b.scatter(vv,yy,s=11,c=col,marker=mk,edgecolors='white',linewidths=.35,zorder=3)
 b.text(1.85,y,f'{sum(x==0 for x in vals)}/40 = 0',ha='right',va='center',fontsize=6.2)
b.axvline(0,color=MUTED,lw=.7,ls=(0,(3,3)),zorder=0)
b.set(xlim=(-.7,1.95),ylim=(-.55,1.55),yticks=[0,1],yticklabels=['Shared','Single'],xticks=[-.5,0,.5,1,1.5],xlabel='log$_2$(ensemble MSE / nominal MSE)')
b.spines['left'].set_visible(False);b.tick_params(axis='y',length=0)
for y,(label,col,mk) in enumerate([('Shared response',SLATE,'s'),('Single response',PINK,'o')]):
 m,lo,hi=eff[label];c.errorbar(m,y,xerr=[[m-lo],[hi-m]],fmt=mk,color=col,ms=4,capsize=2,lw=1)
 c.text(16,y,f'{m:+.2f} [{lo:+.2f}, {hi:+.2f}]',va='center',fontsize=6.5)
c.axvline(0,color=MUTED,lw=.7,ls=(0,(3,3)),zorder=0)
c.set(yticks=[0,1],yticklabels=['Shared response','Single response'],xlim=(-22,31),ylim=(-.6,1.6),xticks=[-20,-10,0,10],xlabel='Relative change in aggregate MSE (%)')
c.spines['left'].set_visible(False);c.spines['bottom'].set_bounds(-20,12);c.tick_params(axis='y',length=0)
c.text(16,1.9,'Estimate [97.5% CI]',fontsize=6.5)
save(fig,'fig_recording_decisions_v6')
net=rows('fig3_networks.csv');fc=json.loads((D/'forecast_summary.json').read_text())['primary']
diffs=np.array([float(r['score_difference']) for r in net]);assert len(net)==40 and sum(diffs<0)==19
assert np.isclose(diffs.mean(),fc['score_difference'])
fig=plt.figure(figsize=(180/25.4,100/25.4));a=fig.add_axes([.10,.24,.34,.62]);b=fig.add_axes([.61,.45,.35,.41]);c=fig.add_axes([.61,.19,.35,.10])
panel(a,'a','Risk forecasts and observed error');panel(b,'b','Paired score differences');panel(c,'c','Mean difference (95% CI)')
for i,r in enumerate(net):
 x0,x1,y=[float(r[k]) for k in ['nominal_risk','ensemble_risk','raw_mse']]
 a.plot([x0,x1],[y,y],color='#B9BDC3',lw=.55,zorder=0)
 a.scatter(x0,y,s=15,marker='o',facecolor='white',edgecolor=INK,lw=.65,label='Nominal' if i==0 else None)
 a.scatter(x1,y,s=15,marker='D',facecolor=PINK,edgecolor='white',lw=.3,label='Prior-averaged' if i==0 else None)
a.plot([3e-8,3e-3],[3e-8,3e-3],color=MUTED,lw=.7,ls=(0,(3,3)),zorder=0)
a.set(xscale='log',yscale='log',xlim=(3e-8,3e-3),ylim=(3e-8,3e-3),xlabel='Forecast risk (q²)',ylabel='Observed MSE (q²)')
for axis in [a.xaxis,a.yaxis]:axis.set_ticks([1e-7,1e-6,1e-5,1e-4,1e-3]);axis.set_minor_locator(NullLocator())
a.legend(frameon=False,loc='upper left',fontsize=6.5,handletextpad=.4)
order=np.argsort(diffs);s=diffs[order]
b.hlines(np.arange(40),0,s,color=GRAY,lw=.65)
b.scatter(s,np.arange(40),s=9,c=[PINK if x<0 else SLATE for x in s],linewidths=0,zorder=3)
b.axvline(0,color=MUTED,lw=.7,ls=(0,(3,3)),zorder=0)
b.set(xlim=(-12.5,2),ylim=(-2,42),yticks=[0,19,39],yticklabels=['1','20','40'],xticks=[-12,-8,-4,0],xlabel='Ensemble − nominal score',ylabel='Network rank')
b.text(.02,.95,'19 lower; 21 higher',transform=b.transAxes,va='top',fontsize=6.5)
b.annotate(f'{s[0]:.2f}',xy=(s[0],0),xytext=(-10.5,8),arrowprops={'arrowstyle':'-','lw':.6,'color':INK},fontsize=6.5)
m,lo,hi=[fc[k] for k in ['score_difference','score_difference_ci_low','score_difference_ci_high']]
c.axvline(0,color=MUTED,lw=.7,ls=(0,(3,3)))
c.errorbar(m,0,xerr=[[m-lo],[hi-m]],fmt='D',color=INK,ms=4,capsize=2,lw=1)
c.set(xlim=(-1.3,.2),ylim=(-1,1),yticks=[],xticks=[-1.2,-.6,0],xlabel='Ensemble − nominal score')
c.spines['left'].set_visible(False)
c.text(.5,-1.48,f'{m:.3f} [{lo:.3f}, {hi:+.3f}]',ha='center',transform=c.transAxes,fontsize=6.5)
save(fig,'fig_risk_forecasts_v6_study')
for stem,record in qa.items():
 r=subprocess.run(['pdffonts',str(HERE/f'{stem}.pdf')],capture_output=True,text=True,check=True);record['pdffonts']=r.stdout
 assert 'Arial' in r.stdout and all(' yes ' in line for line in r.stdout.splitlines()[2:])
record={'checks':qa,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.glob('*')},'frozen_intervals_recomputed':False,'statistics_changed':False}
(HERE/'qa_receipt.json').write_text(json.dumps(record,indent=2))
print(json.dumps(qa,indent=2))
