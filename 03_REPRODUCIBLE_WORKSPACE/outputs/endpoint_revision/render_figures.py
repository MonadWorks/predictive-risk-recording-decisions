"""Apply the refined manuscript's physical layout to frozen result figures.

The original plotting functions supply every data point, mean and interval.
This layer changes only presentation and writes current manuscript assets.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.collections import PathCollection
from matplotlib.text import Text
from matplotlib.ticker import NullLocator,FixedLocator,LogLocator,FuncFormatter
from figure_style import setup,apply_palette,INK,MUTED,TICK,LABEL

HERE=Path(__file__).resolve().parent
RESEARCH=HERE.parents[1]/'work/recording_extensions'
# All coordinates in millimetres: axes rectangles and panel-title baselines.
LAYOUTS={
 'endpoint_evidence':(113,[(20,62,66,36),(110,62,66,36),(20,15,66,27),(120,15,56,27)],
  [(4,106,'a','Allocation experiment'),(94,106,'b','Independent validation'),(4,50,'c','Prediction specificity'),(94,50,'d','Joint coverage versus one end')]),
 'mechanism_evidence':(128,[(20,76,66,37),(110,76,66,37),(20,20,66,34),(110,20,66,34)],
  [(4,121,'a','Response ambiguity'),(94,121,'b','Recording precision'),(4,62,'c','Paired response ranges'),(94,62,'d','Gain information, then refitting')]),
 'parameter_mechanism':(82,[(19,25,67,40),(124,25,50,40)],
  [(4,75,'a','Parameter information, then refitting'),(94,75,'b','Finite-response error decomposition')]),
 'recording_information':(119,[(30,74,55,34),(113,74,61,34),(35,19,50,28),(124,19,50,28)],
  [(4,115,'a','Recurrent information'),(94,115,'b','Calibration recordings'),(4,55,'c','Targeted versus random'),(94,55,'d','Targeted versus response')]),
 'structure_robustness':(87,[(52,20,122,48)],[(4,80,'','Endpoint allocation across model variants')]),
 'fitting_sensitivity':(77,[(43,19,43,41),(114,19,60,41)],
  [(4,70,'a','Same recordings; shared fitting rule'),(94,70,'b','Each point is one network')]),
 'method_validation':(73,[(51,23,123,34)],[(4,66,'','Indirect recordings: fitting sensitivity')]),
 'limited_budget':(84,[(40,21,46,44),(130,21,44,44)],
  [(4,77,'a','Average across six settings'),(94,77,'b','Budget and recording precision')]),
 'combination_controls':(87,[(19,28,67,41),(129,28,45,41)],
  [(4,80,'a','Local sensitivity projection'),(94,80,'b','Finite changes preserving combinations')]),
}


def data_fingerprint(fig):
    """Hash scientific coordinates and limits, independent of page geometry."""
    h=hashlib.sha256()
    def add(x):
        if isinstance(x,np.ndarray):h.update(str((x.shape,x.dtype)).encode());h.update(x.tobytes())
        else:h.update(repr(x).encode())
    for ax in fig.axes:
        add((ax.get_xlim(),ax.get_ylim(),ax.get_xscale(),ax.get_yscale()))
        for a in ax.lines:
            add(np.asarray(a.get_xdata()));add(np.asarray(a.get_ydata()))
        for a in ax.collections:
            add(np.asarray(a.get_offsets()))
            # LineCollection paths contain interval ends; marker paths do not.
            if not isinstance(a,PathCollection):
                for p in a.get_paths():add(p.vertices);add(p.codes)
        for a in ax.patches:
            add(a.get_path().vertices)
            if hasattr(a,'get_bbox'):add(a.get_bbox().bounds)
    return h.hexdigest()


def log_ticks(axis,limits,ratio=False):
    lo,hi=sorted(limits)
    if ratio:
        ticks=[m*10.**k for k in range(-8,9) for m in (1,2,5) if lo<=m*10.**k<=hi]
        if 2<=len(ticks)<=6:
            axis.set_major_locator(FixedLocator(ticks));axis.set_major_formatter(FuncFormatter(lambda x,pos:f'{x:g}'))
        else:
            axis.set_major_locator(LogLocator(base=10,numticks=4));axis.set_major_formatter(FuncFormatter(lambda x,pos:r'$10^{'+str(int(round(np.log10(x))))+'}$'))
    else:
        axis.set_major_locator(LogLocator(base=10,numticks=4));axis.set_major_formatter(FuncFormatter(lambda x,pos:r'$10^{'+str(int(round(np.log10(x))))+'}$'))
    axis.set_minor_locator(NullLocator())


def reflow(fig,name):
    setup(plt)
    height,rects,headers=LAYOUTS[name]
    fig.set_layout_engine(None)
    fig.set_size_inches(180/25.4,height/25.4,forward=True)
    fig.set_facecolor('white')
    notes=[t.get_text() for t in fig.texts if t is not fig._suptitle]
    for t in list(fig.texts):t.remove()
    fig._suptitle=None
    for ax,rect in zip(fig.axes,rects):
        ax.set_position([rect[0]/180,rect[1]/height,rect[2]/180,rect[3]/height])
        for loc in ['left','center','right']:ax.set_title('',loc=loc)
        ax.grid(False,which='both');ax.set_facecolor('white')
        for side,spine in ax.spines.items():
            spine.set_visible(side in ('left','bottom'));spine.set_color(INK);spine.set_linewidth(.6)
        ax.tick_params(axis='both',which='major',labelsize=6.3,length=2.5,width=.6,pad=2,color=TICK,labelcolor=TICK)
        if ax.get_xscale()=='log':log_ticks(ax.xaxis,ax.get_xlim(),ratio='ratio' in ax.get_xlabel().lower())
        if ax.get_yscale()=='log':log_ticks(ax.yaxis,ax.get_ylim())
        ax.xaxis.labelpad=3;ax.yaxis.labelpad=3
        for label in (ax.xaxis.label,ax.yaxis.label):label.set_fontsize(7);label.set_color(LABEL)
        if ax.get_xscale()=='log' and ax.get_yscale()=='linear':
            ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
        for line in ax.lines:
            line.set_linewidth(min(1.2,max(.6,line.get_linewidth()*.65)))
            if line.get_marker() not in ('None',None,'',' '):
                line.set_markersize(min(4,max(2.2,line.get_markersize()*.65)))
                line.set_markeredgewidth(.6)
        for c in ax.collections:
            if isinstance(c,PathCollection):c.set_sizes(np.minimum(15,np.asarray(c.get_sizes())*.65))
            c.set_linewidths(np.minimum(1,np.asarray(c.get_linewidths())*.65))
        for t in ax.texts:t.set_fontsize(6.3)
        legend=ax.get_legend()
        if legend:
            handles,labels=ax.get_legend_handles_labels();loc=legend._loc
            legend.remove()
            ax.legend(handles,labels,loc=loc,frameon=False,fontsize=6,
                      markerscale=.75,handlelength=1.3,handletextpad=.5,labelspacing=.35,borderaxespad=.4)
    apply_palette(fig)
    for t in fig.findobj(Text):t.set_fontfamily('BentonSans');t.set_fontweight('normal')
    # Explicit axis wording keeps long labels readable at the reference size.
    if name=='endpoint_evidence':
        for ax in fig.axes[:2]:
            for t in list(ax.texts):t.remove()
        fig.axes[2].set_ylabel('MSE relative to ordinary sites (%)',fontsize=7)
        fig.axes[3].set_xlabel('MSE reduction with both ends (%)',fontsize=7)
        handles,labels=fig.axes[2].get_legend_handles_labels()
        for ax in fig.axes[2:]:ax.get_legend().remove()
        fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.54,0),ncol=2,frameon=False,fontsize=6,handlelength=1.5)
    if name=='mechanism_evidence':
        fig.axes[0].set_ylabel('Squared response-range width',fontsize=7)
        fig.axes[2].set_xlabel('Range width squared: ordinary sites',fontsize=7)
        fig.axes[2].set_ylabel('Range width squared: both ends',fontsize=7)
    if name=='parameter_mechanism':fig.axes[1].set_xlabel('Contribution ratio\nEndpoint / ordinary recording',fontsize=7)
    if name=='recording_information':
        legend=fig.axes[0].get_legend();handles,labels=fig.axes[0].get_legend_handles_labels()
        if legend:legend.remove()
        fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.54,0),ncol=2,frameon=False,fontsize=6,handletextpad=.4,columnspacing=2)
    if name=='limited_budget':
        for ax in fig.axes:ax.set_xlabel('Response MSE ratio\nPair-seeded / comparator',fontsize=7)
        fig.axes[1].xaxis.set_major_locator(FixedLocator([.8,1,1.25,1.6,2]))
        fig.axes[1].xaxis.set_major_formatter(FuncFormatter(lambda x,pos:f'{x:g}'))
        handles,labels=fig.axes[1].get_legend_handles_labels();fig.axes[1].get_legend().remove()
        fig.legend(handles,labels,loc='upper right',bbox_to_anchor=(174/180,73/height),frameon=False,fontsize=6,markerscale=.75,handletextpad=.3,borderaxespad=0)
    if name=='combination_controls':
        fig.axes[0].set_ylabel('Fraction of squared response sensitivity',fontsize=7)
        handles,labels=fig.axes[0].get_legend_handles_labels();fig.axes[0].get_legend().remove()
        fig.legend(handles,labels,loc='center',bbox_to_anchor=(48/180,15/height),ncol=2,frameon=False,fontsize=6,handlelength=1.5,columnspacing=1)
        handles,labels=fig.axes[1].get_legend_handles_labels();fig.axes[1].get_legend().remove()
        fig.legend(handles,labels,loc='upper right',bbox_to_anchor=(174/180,76/height),frameon=False,fontsize=6,markerscale=.75,handletextpad=.3,borderaxespad=0)
    if name=='structure_robustness':
        handles,labels=fig.axes[0].get_legend_handles_labels();fig.axes[0].get_legend().remove()
        fig.legend(handles,labels,loc='upper right',bbox_to_anchor=(174/180,73/height),frameon=False,fontsize=6,markerscale=.75,handletextpad=.3,borderaxespad=0)
    for x,y,letter,title in headers:
        if letter:fig.text(x/180,y/height,letter,fontsize=8,fontweight='bold',color=INK)
        fig.text((x+5 if letter else x)/180,y/height,title,fontsize=7,fontweight='bold',color=INK)
    # Keep the original methodological note, in the same physical footnote style.
    if notes:
        fig.text(4/180,5/height,'\n'.join(notes),fontsize=5.8,color=MUTED,linespacing=1.35,va='center')
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    outside=[]
    for t in fig.findobj(Text):
        if not t.get_visible() or not t.get_text():continue
        # Tick locators can retain invisible off-axis ticks beyond fixed limits.
        if any(t in ax.get_xticklabels()+ax.get_yticklabels() for ax in fig.axes):
            if t.get_clip_on():continue
        b=t.get_window_extent(renderer)
        if b.x0<-.5 or b.y0<-.5 or b.x1>fig.bbox.width+.5 or b.y1>fig.bbox.height+.5:outside.append(t.get_text())
    return {'dimensions_mm':[180,height],'out_of_canvas_text':outside}


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod;sys.path.insert(0,str(path.parent));spec.loader.exec_module(mod);return mod


def main(out,audit=None):
    out.mkdir(parents=True,exist_ok=True);original=Figure.savefig;checks={}
    def save(fig,path,*args,**kwargs):
        name=Path(path).stem
        if name not in LAYOUTS:raise ValueError('Unexpected figure: '+str(path))
        if not getattr(fig,'_refined_layout',False):
            before=data_fingerprint(fig);layout=reflow(fig,name);after=data_fingerprint(fig)
            assert before==after,'Scientific coordinates changed: '+name
            fig._refined_layout=True
            checks[name]={'scientific_data_unchanged':True,'data_sha256':before,**layout}
        kwargs.update(dpi=300,bbox_inches=None)
        original(fig,out/Path(path).name,*args,**kwargs)
    Figure.savefig=save
    try:
        r2=module('endpoint_round2_figures',RESEARCH/'round2/code/figures.py');r2.endpoint_plot();r2.fit_plot()
        r3=module('endpoint_round3_figures',RESEARCH/'round3/code/figures.py');r3.main()
        r4=module('figures4',RESEARCH/'round4/code/figures4.py');r4.main()
        r5=module('endpoint_round5_figures',RESEARCH/'round5/code/figures5.py');r5.main()
    finally:Figure.savefig=original;plt.close('all')
    assert set(checks)==set(LAYOUTS)
    assert all(not c['out_of_canvas_text'] for c in checks.values()),checks
    if audit:audit.write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=HERE/'figures');p.add_argument('--audit',type=Path)
    args=p.parse_args();main(args.out,args.audit)
