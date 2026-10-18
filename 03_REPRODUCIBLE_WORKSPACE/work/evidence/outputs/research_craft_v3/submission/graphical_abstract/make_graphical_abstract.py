"""One-page graphical abstract from frozen aggregate effect estimates only."""
import csv,hashlib,json,os,subprocess
from pathlib import Path
os.environ.setdefault('MPLBACKEND','Agg')
os.environ.setdefault('MPLCONFIGDIR','/tmp/icbr-ga-mpl-cache')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/icbr-ga-xdg-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch
from PIL import Image
import numpy as np
import xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parent
PACKAGE=OUT.parents[1]
sources=dict(decision=PACKAGE/'source_data/holdout_summary.json',
             forecast=PACKAGE/'source_data/forecast_summary.json')
study=json.loads(sources['decision'].read_text());follow=json.loads(sources['forecast'].read_text())
assert study['integrity']['complete'] and study['integrity']['evaluated_networks']==40
assert follow['independent_networks']==40 and follow['point_predictions_shared'] and follow['raw_mse_identical_for_forecasts']
assert follow['hypotheses_frozen_before_followup_outcomes'] and follow['first_study_primary_unchanged']
rows=[]
for method in ['scalar','vector']:
    r=next(x for x in study['primary_effects']if x['contrast']==f'ensemble_{method} - local_{method}')
    assert r['confidence_level']==.975 and r['networks']==40 and r['primary']
    rows.append(dict(test='recording_decision',endpoint='raw response MSE',comparison=f'{method} target',
      independent_networks=40,effect=r['effect'],ci_low=r['ci_low'],ci_high=r['ci_high'],
      confidence_level=.975,display_multiplier=1e5,source_key=f'primary_effects[{method}]'))
r=follow['primary'];assert r['confidence_level']==.95 and r['independent_networks']==40
rows.append(dict(test='fixed_prediction_risk_forecast',endpoint='MSE-consistent score',comparison='fixed local-scalar policy',
      independent_networks=40,effect=r['score_difference'],ci_low=r['score_difference_ci_low'],ci_high=r['score_difference_ci_high'],
      confidence_level=.95,display_multiplier=1.,source_key='primary.score_difference'))
with (OUT/'source_effects.csv').open('w',newline='')as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

arial=font_manager.findfont('Arial',fallback_to_default=False)
plt.rcParams.update({'font.family':'Arial','font.size':8.5,'axes.labelsize':8.5,'xtick.labelsize':8,
 'ytick.labelsize':8.5,'axes.linewidth':.65,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none',
 'mathtext.fontset':'custom','mathtext.rm':'Arial','mathtext.it':'Arial:italic','mathtext.bf':'Arial:bold',
 'figure.facecolor':'white','savefig.facecolor':'white','axes.spines.top':False,'axes.spines.right':False})
fig=plt.figure(figsize=(190/25.4,135/25.4))
ink='#172B3A';muted='#5B6871';blue='#0072B2';vermilion='#D55E00'
fig.text(.055,.955,'Does prior averaging help when neural recordings are limited?',fontsize=10,fontweight='bold',color=ink,va='top')
fig.text(.055,.912,'Two independent simulation studies with known connectivity',fontsize=9,color=muted,va='top')

for x,first,second in [(.18,'Known connectivity','Uncertain physiology'),(.50,'Limited recordings','Fixed recording budget'),(.82,'Stimulus response','Prespecified target')]:
    fig.text(x,.825,first,ha='center',fontsize=9,color=ink)
    fig.text(x,.787,second,ha='center',fontsize=8,color=muted)
pipeline_arrows=[]
for a,b in [(.326,.393),(.644,.710)]:
    arrow=FancyArrowPatch((a,.813),(b,.813),transform=fig.transFigure,arrowstyle='-|>',mutation_scale=9,linewidth=.8,color='#8A969F')
    fig.add_artist(arrow);pipeline_arrows.append((arrow,a,b))
fig.add_artist(plt.Line2D([.055,.945],[.734,.734],transform=fig.transFigure,color='#D6DDE2',linewidth=.6))
fig.text(.50,.754,'Broad matched uncertainty · M = 3 · endpoints excluded',ha='center',fontsize=8,color=muted)

fig.text(.055,.69,'A',fontsize=10,fontweight='bold',color=ink)
fig.text(.085,.69,'Recording decisions',fontsize=10,fontweight='bold',color=ink)
fig.text(.055,.65,'40 networks · two prespecified comparisons',fontsize=8.5,color=muted)
fig.text(.055,.612,'Different recording sets; actual response MSE',fontsize=8.5,color=ink)
fig.text(.055,.578,'97.5% paired network-cluster intervals',fontsize=8,color=muted)

fig.text(.56,.69,'B',fontsize=10,fontweight='bold',color=ink)
fig.text(.59,.69,'Risk forecasts',fontsize=10,fontweight='bold',color=ink)
fig.text(.56,.65,'40 new networks · one prespecified comparison',fontsize=8.5,color=muted)
fig.text(.56,.612,'Same data and point predictions',fontsize=8.5,color=ink)
fig.text(.56,.578,'95% paired network-cluster interval',fontsize=8,color=muted)

ax=fig.add_axes([.185,.305,.285,.205]);ax.axvline(0,color='#6F7E89',linewidth=.8,linestyle=(0,(3,2)))
for y,d,marker,col in [(1,rows[0],'o',blue),(0,rows[1],'s',vermilion)]:
    x=d['effect']*1e5;low=d['ci_low']*1e5;high=d['ci_high']*1e5
    ax.errorbar(x,y,xerr=[[x-low],[high-x]],fmt=marker,color=col,markersize=4.5,
       markeredgewidth=.7,elinewidth=1.2,capsize=3.5,capthick=.85,zorder=3)
ax.set_yticks([1,0],['Scalar target','Vector target']);ax.tick_params(axis='y',length=0,pad=5)
ax.set_ylim(-.65,1.65);ax.set_xlim(-1.65,.85);ax.set_xticks([-1.5,-.75,0,.75]);ax.spines['left'].set_visible(False)
ax.tick_params(axis='x',length=3,pad=3);ax.set_xlabel(r'Ensemble − nominal MSE ($q^2\times10^{-5}$)',labelpad=5)

bx=fig.add_axes([.685,.305,.26,.205]);bx.axvline(0,color='#6F7E89',linewidth=.8,linestyle=(0,(3,2)))
d=rows[2];x=d['effect'];low=d['ci_low'];high=d['ci_high']
bx.errorbar(x,.5,xerr=[[x-low],[high-x]],fmt='o',color=ink,markersize=4.5,
     markeredgewidth=.7,elinewidth=1.2,capsize=3.5,capthick=.85,zorder=3)
bx.set_yticks([.5],['Fixed policy']);bx.tick_params(axis='y',length=0,pad=5)
bx.set_ylim(-.65,1.65);bx.set_xlim(-1.3,.3);bx.set_xticks([-1.2,-.6,0]);bx.spines['left'].set_visible(False)
bx.tick_params(axis='x',length=3,pad=3);bx.set_xlabel('Ensemble − nominal score',labelpad=5)

fig.text(.055,.175,'Scalar: −0.259 [−1.471, 0.483]',fontsize=8.5,color=blue)
fig.text(.055,.137,'Vector:  0.192 [−0.115, 0.683]',fontsize=8.5,color=vermilion)
fig.text(.56,.175,'Score: −0.456 [−1.159, 0.024]',fontsize=8.5,color=ink)
fig.text(.56,.137,'MSE-forecast score: log(v) + e²/v',fontsize=8,color=muted)
fig.add_artist(plt.Line2D([.055,.945],[.123,.123],transform=fig.transFigure,color='#D6DDE2',linewidth=.6))
fig.text(.055,.075,'Primary comparisons did not establish a consistent ensemble advantage.',fontsize=9,fontweight='bold',color=ink)
fig.text(.055,.035,'Negative differences favor the ensemble in both panels.',fontsize=8,color=muted)

# Preserve the exact 115-mm evidence body and append a 20-mm author block.
body_scale=115/135;body_bottom=20/135
for a in fig.axes:
    p=a.get_position();a.set_position([p.x0,body_bottom+p.y0*body_scale,p.width,p.height*body_scale])
for txt in fig.texts:
    x,y=txt.get_position();txt.set_position((x,body_bottom+y*body_scale))
for artist in fig.artists:
    if isinstance(artist,plt.Line2D):artist.set_ydata([body_bottom+y*body_scale for y in artist.get_ydata()])
for arrow,a,b in pipeline_arrows:arrow.set_positions((a,body_bottom+.813*body_scale),(b,body_bottom+.813*body_scale))
fig.add_artist(plt.Line2D([.055,.945],[21.5/135,21.5/135],transform=fig.transFigure,color='#D6DDE2',linewidth=.6))
fig.text(.055,.122,r'Jiayi Du$^{1*\dagger}$ and Shuaizhi Cheng$^{2\dagger}$',fontsize=8.6,fontweight='bold',color=ink)
fig.text(.055,.092,r'$^{1}$ Stiftung Louisenlund, Germany',fontsize=8.2,color=ink)
fig.text(.055,.067,r'$^{2}$ Department of Computing, Harbin Institute of Technology, China',fontsize=8.2,color=ink)
fig.text(.055,.037,r'$^{\dagger}$ Equal contribution. * Correspondence: jiayi.du@mail.louisenlund.de',fontsize=8.2,color=muted)

for ext in ['pdf','svg','png']:fig.savefig(OUT/f'graphical_abstract.{ext}',dpi=300,bbox_inches=None)
plt.close(fig)
caption=('Graphical abstract. Does prior averaging improve response-oriented neural recording design or the risk forecast of a fixed prediction? '
 'Both studies use simulated networks with known connectivity and uncertain neuronal physiology. A: 40 independent connection matrices; '
 'the prespecified broad-prior, endpoint-excluded, three-recording comparisons contrast ensemble with nominal-point risk designs, separately '
 'for scalar and common-vector targets. Broad matched uncertainty here means the broad prior and matching generated physiology, not the separate condition named matched. Effects are differences in actual raw response MSE, displayed in units of q^2 times 10^-5, '
 'with 97.5% paired network-cluster bootstrap intervals for the two-comparison family. B: 40 new independent networks; '
 'the prespecified comparison keeps the local-scalar recording policy, observed data and point predictions fixed and compares their risk forecasts '
 'using S(v,e)=log(max(v,1e-24))+e^2/max(v,1e-24), an MSE-functional consistent score. The 95% interval is for ensemble-minus-nominal score. '
 'The point predictions, and hence response MSE, are identical between the two forecasts. A and B have different endpoints, scales and confidence levels. '
 'Negative effects favor the ensemble; zero is shown in each panel and lies within all three primary intervals. '
 'Nested truth/noise/readout repetitions are averaged within network, not counted as independent n. '
 'These computational findings do not establish biological validation or a new design/score method. '
 'Authorship supplied by the user: Jiayi Du¹*† and Shuaizhi Cheng²†; ¹ Stiftung Louisenlund, Germany; '
 '² Department of Computing, Harbin Institute of Technology, China; † Equal contribution. '
 '* Correspondence: jiayi.du@mail.louisenlund.de.\n')
(OUT/'caption.md').write_text(caption)
pdf_fonts=subprocess.run(['/opt/homebrew/bin/pdffonts',str(OUT/'graphical_abstract.pdf')],capture_output=True,text=True,check=True).stdout
(OUT/'pdf_fonts.txt').write_text(pdf_fonts)
print(pdf_fonts)
svg=ET.parse(OUT/'graphical_abstract.svg').getroot();ns={'s':'http://www.w3.org/2000/svg'}
pix=np.asarray(Image.open(OUT/'graphical_abstract.png').convert('RGB'));yy,xx=np.where((pix<245).any(axis=2))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=dict(source_summary_sha256={k:sha(v)for k,v in sources.items()},source_summary_paths={k:str(v)for k,v in sources.items()},
 independent_networks_per_test=40,decision_confidence_level=.975,forecast_confidence_level=.95,
 effect_data=rows,display_transformations=['Decision effect and both interval endpoints multiplied by 100000; labelled x10^-5',
 'Forecast score difference unchanged; fixed original point predictions'],width_mm=190,height_mm=135,font_family='Arial',font_path=arial,
 user_supplied_authorship={'authors':'Jiayi Du¹*† and Shuaizhi Cheng²†','affiliation_1':'Stiftung Louisenlund, Germany',
 'affiliation_2':'Department of Computing, Harbin Institute of Technology, China','equal_contribution':'† Equal contribution.',
 'correspondence':'* Correspondence: jiayi.du@mail.louisenlund.de'},
 pdf_fonts_output=pdf_fonts,color_roles=dict(scalar=blue,vector=vermilion,forecast_score=ink),svg_embedded_images=len(svg.findall('.//s:image',ns)),svg_text_nodes=len(svg.findall('.//s:text',ns)),
 edge_padding_px=dict(left=int(xx.min()),right=int(pix.shape[1]-1-xx.max()),top=int(yy.min()),bottom=int(pix.shape[0]-1-yy.max())),
 prepared_only=True,submitted=False,visual_review='pending actual image inspection')
manifest['output_sha256']={p.name:sha(p)for p in OUT.iterdir()if p.is_file()and p.name!='manifest.json'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
assert all((OUT/f'graphical_abstract.{ext}').stat().st_size<10_000_000 for ext in ['pdf','svg','png'])
print(json.dumps({k:manifest[k]for k in ['width_mm','height_mm','svg_embedded_images','svg_text_nodes','edge_padding_px']},indent=2))
