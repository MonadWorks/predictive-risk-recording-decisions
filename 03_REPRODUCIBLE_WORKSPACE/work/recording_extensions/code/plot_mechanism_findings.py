"""Figures linking decision sensitivity and influential fitting failures."""
import csv,json,os
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'scratch/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    out=ROOT/'analysis'
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    with (out/'ranking_diagnostics.csv').open() as f:rank=list(csv.DictReader(f))
    look={(int(r['network_id']),float(r['prior_sd'])):float(r['nominal_ensemble_rank_correlation']) for r in rank}
    matrix=np.array([[look[nid,sd] for sd in [.3,.6,.9]] for nid in range(20000,20040)])
    rng=np.random.default_rng(20261018);ix=rng.integers(0,40,size=(10000,40));boot=matrix[ix].mean(axis=1)
    with (out/'teacher_objective_summary.csv').open() as f:summary=list(csv.DictReader(f))
    fig,axes=plt.subplots(1,2,figsize=(10.5,4.3))
    ax=axes[0]
    for row in matrix:ax.plot([.3,.6,.9],row,color='#B8B8B8',alpha=.38,lw=.7)
    mean=matrix.mean(axis=0);lo=np.quantile(boot,.025,axis=0);hi=np.quantile(boot,.975,axis=0)
    ax.errorbar([.3,.6,.9],mean,yerr=[mean-lo,hi-mean],color='#B14F77',marker='o',lw=2,capsize=3)
    ax.set(xlabel='Matched gain-prior SD',ylabel='Nominal / ensemble rank correlation',xticks=[.3,.6,.9],ylim=(-.02,1.03))
    ax.set_title('A  Candidate rankings diverge',loc='left',fontweight='bold')
    ax.text(.04,.04,'40 independent networks\nFirst greedy step; common candidate pool',transform=ax.transAxes,fontsize=8)
    ax=axes[1]
    for offset,method,label,color in [(-.17,'local_vector','Nominal','#777777'),(.17,'ensemble_vector','Ensemble','#B14F77')]:
        r=next(r for r in summary if r['condition']=='gain_sd_0.9' and r['budget']=='10' and r['method']==method)
        vals=[100*int(r['certified_suboptimal_fits'])/int(r['fits']),100*float(r['fraction_response_error_in_suboptimal_fits'])]
        bars=ax.bar(np.array([0,1])+offset,vals,width=.3,color=color,label=label)
        for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+1.5,f'{v:.1f}%',ha='center',fontsize=9)
    ax.set(xticks=[0,1],xticklabels=['Fits above teacher\nparameter objective','Their share of total\nsquared response error'],ylabel='Percent',ylim=(0,110))
    ax.set_title('B  Poor fits dominate the error tail',loc='left',fontweight='bold')
    ax.legend(frameon=False,loc='upper left',fontsize=9)
    ax.text(.035,.77,'Prior SD 0.9; 10 recordings\n160 fitted datasets per policy',transform=ax.transAxes,fontsize=8)
    fig.tight_layout()
    for ext in ['png','pdf']:fig.savefig(out/f'mechanism_findings.{ext}',dpi=300)
    plt.close(fig)
    records=json.loads((out/'fit_diagnosis/results.json').read_text())
    fig,axes=plt.subplots(1,3,figsize=(11.2,4.2),sharey=True)
    shapes=[('nominal','o',-.12,'Original start'),('best','D',0,'Lowest MAP objective of five starts'),('oracle','*',.12,'Teacher start (oracle)')]
    for ax,nid,sd,case_name in zip(axes,[20009,20014,20020],[.9,.6,.6],['Case A','Case B','Case C']):
        for x,method,color in [(0,'local_vector','#777777'),(1,'ensemble_vector','#B14F77')]:
            rs=[r for r in records if r['network_id']==nid and r['method']==method]
            orig=next(r for r in rs if r['start']=='nominal')
            best=min([r for r in rs if r['start']!='teacher_oracle'],key=lambda r:r['objective'])
            oracle=next(r for r in rs if r['start']=='teacher_oracle')
            vals=[orig['response_mse'],best['response_mse'],oracle['response_mse']]
            ax.plot([x-.12,x,x+.12],vals,color=color,lw=.9,alpha=.65)
            for (name,marker,offset,label),v in zip(shapes,vals):
                ax.scatter(x+offset,v,marker=marker,s=65 if marker=='*' else 35,
                           facecolor='white' if name=='nominal' else color,edgecolor=color,
                           label=label if x==0 and nid==20009 else None,zorder=3)
        ax.set(yscale='log',xticks=[0,1],xticklabels=['Nominal\nselection','Ensemble\nselection'],xlim=(-.4,1.4))
        ax.set_title(f'{case_name} | prior SD {sd}',loc='left',fontweight='bold')
    axes[0].set_ylabel('Three-response MSE for one fixed dataset')
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False,fontsize=8,bbox_to_anchor=(.5,-.01))
    fig.tight_layout(rect=(0,.06,1,1))
    for ext in ['png','pdf']:fig.savefig(out/f'fit_start_diagnosis.{ext}',dpi=300,bbox_inches='tight')
    plt.close(fig)


if __name__=='__main__':main()
