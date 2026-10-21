"""Graphical abstract for the endpoint and internal-information manuscript.

All displayed effects are read from the frozen network summaries. Schematics
illustrate recording roles and the exact response factorization; quantitative
bars use ratios of aggregate means from those same summaries.
"""
from pathlib import Path
import argparse, json, shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle
from figure_style import PAPER, PANEL, INK, MUTED, RULE, ROSE, PINK, PLUM, GOLD, LIGHT_GREY

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]/'work/recording_extensions'
FONTS = HERE.parent/'graphical_abstract/source/fonts'
KEY_FINDING = 'Calibrate the endpoints, then target the remaining internal information.'
TITLE = 'Predictive risk and recording decisions'
SUBTITLE = 'in partially observed neural networks'


def load_evidence():
    endpoint = json.loads((RESEARCH/'round2/analysis/validation_summary.json').read_text())['comparisons']['both_vs_neither']
    ranges = json.loads((RESEARCH/'round3/analysis/profile_summary.json').read_text())
    internal = json.loads((RESEARCH/'round5/analysis/summary.json').read_text())
    width = ranges['comparisons']['both_vs_neither']['width2']
    extra = internal['primary']['profile_width_squared/combination5_vs_random5']
    return endpoint, width, extra


def main(out, sync=False):
    for path in FONTS.glob('*.ttf'):
        fm.fontManager.addfont(str(path))
    plt.rcParams.update({
        'font.family': 'BentonSans', 'font.size': 9, 'text.color': INK,
        'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
        'figure.facecolor': PAPER, 'savefig.facecolor': PAPER,
    })
    endpoint, width, extra = load_evidence()
    e = -endpoint['relative_change_percent']
    w = -width['change_pct']
    i = -extra['change_pct']
    eci = -np.array(endpoint['ci95_percent'][::-1])
    wci = -np.array(width['ci95'][::-1])
    ici = -np.array(extra['ci_family_three'][::-1])
    assert round(e,2)==98.13 and round(w,2)==99.08 and round(i,2)==27.15

    fig = plt.figure(figsize=(260/25.4,175/25.4))
    ax = fig.add_axes([0,0,1,1]); ax.set(xlim=(0,260),ylim=(0,175)); ax.set_axis_off()
    def text(x,y,s,size=9,color=INK,weight='normal',ha='left',va='center',**kwargs):
        return ax.text(x,y,s,fontsize=size,color=color,fontweight=weight,ha=ha,va=va,linespacing=1.35,**kwargs)
    def panel(x,y,w,h):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=1.7',facecolor=PANEL,edgecolor=RULE,lw=.7))
    def arrow(start,end,color=MUTED,lw=1.1,scale=8):
        ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=scale,lw=lw,color=color))
    def node(x,y,label='',face=PAPER,edge=RULE,r=2.2,recorded=False):
        if recorded:
            ax.add_patch(Circle((x,y),r+1.05,facecolor='none',edgecolor=PINK,lw=1.1))
        ax.add_patch(Circle((x,y),r,facecolor=face,edgecolor=edge,lw=.85,zorder=4))
        if label:text(x,y,label,size=7.5,ha='center',weight='bold',color=PAPER if face==PLUM else INK,zorder=5)
    def metric(cx,value,label):
        text(cx,66,f'{value:.2f}%',size=27,color=ROSE,weight='bold',ha='center')
        text(cx,54,label,size=9.3,ha='center',weight='bold')
    def relative_bars(x,y,ratio,first,second,bar_width=32):
        # Normalized aggregate metric; the control is exactly one.
        text(x,y,first,size=7.3,ha='right',color=MUTED)
        text(x,y-6,second,size=7.3,ha='right',color=MUTED)
        x0=x+2
        ax.add_patch(Rectangle((x0,y-1.4),bar_width,2.8,facecolor=LIGHT_GREY,edgecolor='none'))
        ax.add_patch(Rectangle((x0,y-7.4),bar_width*ratio,2.8,facecolor=ROSE,edgecolor='none'))
        text(x0+bar_width+1.4,y,'1.00',size=7,color=MUTED)
        text(x0+bar_width*ratio+1.4,y-6,f'{ratio:.3f}' if ratio<.1 else f'{ratio:.2f}',size=7,color=ROSE)

    text(8,162,TITLE,size=22,weight='bold')
    text(8,150,SUBTITLE,size=17)
    ax.plot([8,252],[142,142],color=RULE,lw=.7)
    text(8,135.5,'Five recordings to predict a held-out stimulus response',size=10.5,color=MUTED)

    for x in (8,91,174):panel(x,32,78,96)
    text(13,121,'1  Record both ends',size=11,weight='bold')
    text(96,121,'2  Explain the benefit',size=11,weight='bold')
    text(179,121,'3  Acquire internal information',size=10.2,weight='bold')

    # A schematic of a 100-unit network: selected endpoints plus one extra site.
    text(13,113.5,'1 stimulus + 3 readouts + 1 extra site',size=8.7)
    rng=np.random.default_rng(736)
    xy=np.c_[rng.uniform(27,62,17),rng.uniform(83,106,17)]
    endpoints=np.array([[18.,95.],[74.,105.],[74.,94.],[74.,83.],[44.,107.]])
    allxy=np.vstack([xy,endpoints])
    for k in range(38):
        a,b=rng.choice(len(allxy),2,replace=False)
        ax.plot(allxy[[a,b],0],allxy[[a,b],1],color=RULE,lw=.55,zorder=1)
    for x,y in xy:node(x,y,r=1.5,face='#EEE9EC',edge='#CCC3CC')
    for k,(x,y) in enumerate(endpoints):
        node(x,y,'S' if k==0 else ('R' if k<4 else '+'),
             face='#FFF3D6' if k==0 else (PLUM if k<4 else PAPER),
             edge=GOLD if k==0 else (PLUM if k<4 else ROSE),r=2.65,recorded=True)
    arrow((11.5,95),(14,95),color=GOLD)
    text(47,77,'100-unit network (schematic)',size=7.5,color=MUTED,ha='center')
    metric(47,e,'lower response prediction error')
    text(47,44,'vs five ordinary recording sites',size=8,ha='center',color=MUTED)
    text(47,37.5,f'40 new networks | 95% CI: {eci[0]:.2f}-{eci[1]:.2f}% reduction',size=7.1,ha='center',color=MUTED)

    # Exact input/propagation/readout identity, followed by the response-range result.
    text(96,113.5,'Exact finite-response factorization',size=8.7)
    for x,label,color in [(97,'Input',GOLD),(121,'Recurrent',MUTED),(145,'Readout',PLUM)]:
        ax.add_patch(FancyBboxPatch((x,100),18,8,boxstyle='round,pad=0,rounding_size=1',facecolor=PAPER,edgecolor=color,lw=.9))
        text(x+9,104,label,size=8,ha='center',color=color,weight='bold')
    arrow((115.5,104),(120,104));arrow((139.5,104),(144,104))
    text(130,94.5,'Largest error contraction at input and readout',size=7.9,ha='center',color=MUTED)
    relative_bars(118,85.5,1-w/100,'Ordinary','Endpoints',bar_width=31)
    metric(130,w,'smaller squared response-range width')
    text(130,44,'Responses compatible with the calibration fit',size=8,ha='center',color=MUTED)
    text(130,37.5,f'40 networks | 95% CI: {wci[0]:.2f}-{wci[1]:.2f}% reduction',size=7.1,ha='center',color=MUTED)

    # Keep endpoint observations and acquire information about recurrent combinations.
    text(179,113.5,'Keep four endpoints; choose the fifth site',size=8.7)
    for k,x in enumerate([184,196,208,220,241]):
        node(x,104,'S' if k==0 else ('R' if k<4 else '5'),
             face='#FFF3D6' if k==0 else (PLUM if k<4 else PINK),
             edge=GOLD if k==0 else (PLUM if k<4 else ROSE),r=2.7,recorded=k==4)
    text(230.5,104,'+',size=12,color=MUTED,ha='center')
    text(213,94.5,'Target four recurrent gain combinations',size=8,ha='center',color=MUTED)
    relative_bars(201,85.5,1-i/100,'Random fifth','Targeted fifth',bar_width=31)
    metric(213,i,'smaller squared internal-range width')
    text(213,44,'Along one prespecified internal direction',size=8,ha='center',color=MUTED)
    text(213,37.5,f'40 new networks | Adjusted CI: {ici[0]:.2f}-{ici[1]:.2f}%',size=7.1,ha='center',color=MUTED)

    panel(8,6,244,20)
    text(13,19,KEY_FINDING,size=12,color=ROSE,weight='bold')
    text(13,11.5,'Simulated networks with known connectivity and uncertain gains. Internal-range interval adjusted for three comparisons.',size=8.1,color=MUTED)

    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    # Every text element must remain on the canvas, including font-realized bounds.
    for t in ax.texts:
        box=t.get_window_extent(renderer)
        assert box.x0>=0 and box.y0>=0 and box.x1<=fig.bbox.width and box.y1<=fig.bbox.height,t.get_text()
    out.mkdir(parents=True,exist_ok=True)
    for suffix in ('pdf','png','svg'):
        fig.savefig(out/f'graphical_abstract.{suffix}',dpi=300,bbox_inches=None)
    svg=out/'graphical_abstract.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    copy=f'''# Graphical abstract

{TITLE}\n{SUBTITLE}

Five recordings to predict a held-out stimulus response.

1. Record both ends: one stimulus site, three readouts and one extra site. Response MSE is {e:.2f}% lower than with five ordinary recording sites in 40 independent validation networks (95% CI: {eci[0]:.2f}-{eci[1]:.2f}% reduction).

2. Explain the benefit: an exact finite-response factorization identifies input, recurrent propagation and readout. The largest error contraction occurs at input and readout. Joint endpoint recording reduces mean squared feasible response-range width by {w:.2f}% in 40 further networks (95% CI: {wci[0]:.2f}-{wci[1]:.2f}% reduction), under a common calibration-fit allowance.

3. Acquire internal information: retain the four endpoint recordings and select a fifth site for four recurrent gain combinations. Squared feasible width along one prespecified internal direction is {i:.2f}% lower than with a random fifth site in 40 new networks (three-comparison-adjusted interval: {ici[0]:.2f}-{ici[1]:.2f}% reduction).

{KEY_FINDING}

Simulated networks with known connectivity and uncertain gains. The network drawing is schematic. Bars show ratios of aggregate mean metrics, with the respective control normalized to one.
'''
    if sync:
        current=HERE.parents[2]/'01_READ_CURRENT'
        for suffix in ('pdf','png','svg'):shutil.copy2(out/f'graphical_abstract.{suffix}',current/f'graphical_abstract.{suffix}')
        (current/'graphical_abstract_copy.md').write_text(copy)
        (current/'graphical_abstract_text.txt').write_text('\n'.join(t.get_text() for t in ax.texts)+'\n')
    plt.close(fig)
    print('Graphical abstract effects:',e,w,i)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=HERE);p.add_argument('--sync',action='store_true')
    args=p.parse_args();main(args.out,args.sync)
