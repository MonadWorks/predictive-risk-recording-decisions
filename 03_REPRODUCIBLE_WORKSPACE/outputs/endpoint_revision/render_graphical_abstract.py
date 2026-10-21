"""Graphical abstract in the collaborator's refined scientific-figure style.

The only quantitative panels show held-out MSE across the validation networks
and the prespecified internal-range comparison. Diagram geometry is schematic.
"""
from pathlib import Path
import argparse,json,shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle,FancyArrowPatch
from matplotlib.text import Text
from matplotlib.ticker import NullLocator,LogLocator,FuncFormatter
from figure_style import setup,PAPER,PANEL,INK,MUTED,RULE,ROSE,PLUM,GOLD,GREY,LIGHT_GREY

HERE=Path(__file__).resolve().parent
RESEARCH=HERE.parents[1]/'work/recording_extensions'
TITLE='Predictive risk and recording decisions in partially observed neural networks'
KEY_FINDING='Record endpoints for prediction; target the remaining internal information.'


def evidence():
    v=json.loads((RESEARCH/'round2/analysis/validation_summary.json').read_text())
    r=json.loads((RESEARCH/'round5/analysis/summary.json').read_text())
    return v,r['primary']['profile_width_squared/combination5_vs_random5']


def main(out,sync=False):
    setup(plt);validation,internal=evidence();h=132
    fig=plt.figure(figsize=(180/25.4,h/25.4))
    base=fig.add_axes([0,0,1,1]);base.set(xlim=(0,180),ylim=(0,h));base.set_axis_off()
    def txt(x,y,s,size=6.5,weight='normal',color=INK,ha='left',va='baseline',**kw):
        return base.text(x,y,s,fontsize=size,fontweight=weight,color=color,ha=ha,va=va,linespacing=1.3,**kw)
    def header(x,y,letter,title):
        txt(x,y,letter,8,'bold');txt(x+5,y,title,7,'bold')
    def arrow(a,b,color=MUTED,lw=.65,scale=5):
        base.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=scale,color=color,lw=lw))
    def node(x,y,label='',recorded=False,stim=False,r=1.8):
        base.add_patch(Circle((x,y),r,facecolor=ROSE if recorded else PAPER,
                              edgecolor=GOLD if stim else (ROSE if recorded else GREY),lw=1.1 if stim else .6,zorder=4))
        if stim:base.add_patch(Circle((x,y),r+.8,facecolor='none',edgecolor=GOLD,lw=.65,zorder=4))
        if label:txt(x,y,label,5.8,color=INK if stim else (PAPER if recorded else MUTED),ha='center',va='center',zorder=5)
    txt(4,125,TITLE,9,'bold')
    txt(4,119,'Five calibration recordings | Held-out stimulus response | Known connectivity, uncertain gains',6.5,color=MUTED)
    base.plot([4,176],[115,115],color=RULE,lw=.6)
    header(4,108,'a','Record the stimulus and readouts')
    header(94,108,'b','Improve response prediction')

    # Fixed, legible schematic: a stimulus enters the recurrent network and
    # three readouts report the response. Pink marks the five calibration sites.
    internal_xy=[(28,96),(28,87),(28,78),(41,100),(41,91),(41,82),(41,73),(55,96),(55,87),(55,78)]
    positions=[(12,87),*internal_xy,(73,98),(73,87),(73,76)]
    edges=[(0,1),(0,2),(0,3),(1,4),(1,5),(2,5),(2,6),(3,6),(3,7),
           (4,8),(5,8),(5,9),(6,9),(6,10),(7,10),(8,11),(9,12),(10,13),
           (9,5),(6,2),(10,6),(8,5)]
    for a,b in edges:
        p=np.array(positions[a]);q=np.array(positions[b]);u=(q-p)/np.linalg.norm(q-p)
        arrow(p+2*u,q-2*u,color=LIGHT_GREY,lw=.5,scale=3)
    node(12,87,'S',True,True,r=2.4)
    for j,(x,y) in enumerate(internal_xy):node(x,y,'+' if j==3 else '',recorded=j==3,r=2.1 if j==3 else 1.5)
    for x,y in positions[-3:]:node(x,y,'R',True,r=2.4)
    arrow((5,87),(8.3,87),color=GOLD,scale=5)
    txt(7,66,'1 stimulus + 3 readouts + 1 additional site',6.3)
    txt(7,61,'100-unit network (schematic)',6,color=MUTED)
    arrow((85,86),(93,86),color=MUTED,scale=6)

    # Raw independent validation networks, with arithmetic means. No metric
    # cards: the prediction benefit is visible in the comparison itself.
    ax=fig.add_axes([110/180,72/h,62/180,28/h])
    rng=np.random.default_rng(31)
    for j,(policy,color) in enumerate([('neither',GREY),('both',ROSE)]):
        vals=np.asarray(validation['network_means'][policy])
        ax.scatter(j+rng.uniform(-.13,.13,len(vals)),vals,s=8,color=color,alpha=.65,zorder=2)
        ax.plot([j-.20,j+.20],[vals.mean()]*2,color=INK,lw=1,zorder=3)
    ax.set(yscale='log',xticks=[0,1],xticklabels=['Ordinary sites','Both endpoints'],ylabel='Response MSE',xlim=(-.55,1.55))
    ax.yaxis.set_major_locator(LogLocator(base=10,numticks=3));ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x,pos:r'$10^{'+str(int(round(np.log10(x))))+'}$'));ax.tick_params(pad=2)
    ax.yaxis.labelpad=3
    txt(94,59,'Endpoint observations improve held-out prediction.',6.3)
    txt(94,55,'40 independent networks; bars show means.',6,color=MUTED)

    header(4,47,'c','Locate the information mechanism')
    header(94,47,'d','Use the remaining recording')
    for x,label,color in [(9,'Input',ROSE),(33,'Recurrent',PLUM),(57,'Readout',ROSE)]:
        base.add_patch(Rectangle((x,35),20,7,facecolor=PANEL if color==ROSE else PAPER,edgecolor=RULE,lw=.6))
        txt(x+10,38.5,label,6.5,'bold',color=color,ha='center',va='center')
    arrow((29.3,38.5),(32.5,38.5));arrow((53.3,38.5),(56.5,38.5))
    # The nonlinear response identity splits stimulus entry, recurrence and
    # readout; endpoint observations principally contract entry/readout errors.
    txt(9,29,'Exact finite-response factorization',6,color=MUTED)
    txt(9,22,'Endpoint observations constrain stimulus entry\nand readout, narrowing compatible responses.',6.4,va='center')
    txt(9,12.2,'Recurrent gain combinations retain additional information.',5.9,color=MUTED)

    # Four retained endpoints plus a selected fifth site, followed by the
    # prespecified range comparison with its adjusted interval.
    for j,x in enumerate([102,111,120,129]):node(x,39,'S' if j==0 else 'R',True,j==0,r=2)
    txt(141,39,'+',7,color=MUTED,ha='center',va='center')
    node(156,39,'5',True,r=2.4)
    txt(94,31,'Retain endpoints; target recurrent combinations.',6.2)
    ax2=fig.add_axes([116/180,17/h,55/180,8/h])
    ratio=1+internal['change_pct']/100;lo,hi=1+np.asarray(internal['ci_family_three'])/100
    ax2.axvline(1,color=MUTED,lw=.6,ls=(0,(3,3)))
    ax2.errorbar(ratio,0,xerr=[[ratio-lo],[hi-ratio]],fmt='o',color=ROSE,ms=3.5,lw=1,capsize=2)
    ax2.set(xlim=(.5,1.05),ylim=(-1,1),yticks=[],xticks=[.5,.75,1])
    ax2.spines['left'].set_visible(False);ax2.tick_params(axis='x',pad=1,length=2)
    txt(94,21,'Width² along\none internal\ndirection',6,va='center')
    txt(116,9.7,'Targeted / random fifth site; adjusted interval',5.8,color=MUTED)

    base.plot([4,176],[7.5,7.5],color=RULE,lw=.6)
    txt(4,2.7,KEY_FINDING,7,'bold')
    fig.canvas.draw()
    # Validate the manually placed editorial text against the physical canvas.
    renderer=fig.canvas.get_renderer()
    for t in base.texts:
        b=t.get_window_extent(renderer)
        assert b.x0>=0 and b.y0>=0 and b.x1<=fig.bbox.width and b.y1<=fig.bbox.height,t.get_text()
    out.mkdir(parents=True,exist_ok=True)
    for suffix in ('pdf','png','svg'):fig.savefig(out/f'graphical_abstract.{suffix}',dpi=300,bbox_inches=None)
    svg=out/'graphical_abstract.svg';svg.write_text('\n'.join(x.rstrip() for x in svg.read_text().splitlines())+'\n')
    copy=f'''# Graphical abstract

{TITLE}

Five calibration recordings predict a held-out stimulus response in simulated networks with known connectivity and uncertain gains.

- **a. Recording allocation.** The schematic shows one stimulus site, three readouts and one additional recording in a 100-unit network. Pink nodes are recorded; the stimulus is outlined in gold.
- **b. Prediction.** All forty independent endpoint-validation networks are shown. Points are held-out response MSEs and bars are arithmetic means for ordinary-site and joint-endpoint recording, each with five recordings.
- **c. Mechanism.** The exact finite-response factorization separates input, recurrent propagation and readout. Endpoint observations principally contract input and readout errors and narrow compatible responses. Recurrent gain combinations retain additional information.
- **d. Additional recording.** Four endpoints are retained and a fifth site is selected to constrain recurrent combinations. The plotted ratio of mean squared feasible width along one prespecified internal direction is {ratio:.6f}, relative to a random fifth site. The interval [{lo:.6f}, {hi:.6f}] adjusts for the three prespecified comparisons in forty new networks. The dashed line denotes equal range width.

{KEY_FINDING}
'''
    if sync:
        current=HERE.parents[2]/'01_READ_CURRENT'
        for suffix in ('pdf','png','svg'):shutil.copy2(out/f'graphical_abstract.{suffix}',current/f'graphical_abstract.{suffix}')
        (current/'graphical_abstract_copy.md').write_text(copy)
        (current/'graphical_abstract_text.txt').write_text('\n'.join(t.get_text() for t in fig.findobj(Text) if t.get_visible() and t.get_text())+'\n')
    plt.close(fig)
    print('Graphical abstract uses complete validation networks and the frozen internal-range comparison.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=HERE);p.add_argument('--sync',action='store_true')
    a=p.parse_args();main(a.out,a.sync)
