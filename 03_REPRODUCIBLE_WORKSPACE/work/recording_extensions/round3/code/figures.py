from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                     'pdf.fonttype':42,'savefig.bbox':'tight'})
COLORS=['#7b8290','#176b66','#c38135','#9f4e48']

def means_panel(ax,values,labels,colors,title,ylabel):
    rng=np.random.default_rng(381);n=len(values[0]);ix=rng.integers(0,n,(10000,n))
    for i,v in enumerate(values):
        v=np.asarray(v);mean=v.mean();ci=np.percentile(v[ix].mean(1),[2.5,97.5])
        ax.scatter(i+rng.uniform(-.15,.15,n),v,color=colors[i],s=14,alpha=.45,zorder=2)
        ax.errorbar(i,mean,yerr=[[mean-ci[0]],[ci[1]-mean]],fmt='D',color='black',ms=5,capsize=4,zorder=5)
    ax.set_xticks(range(len(values)),labels);ax.set_yscale('log');ax.set_ylabel(ylabel);ax.set_title(title,loc='left',fontweight='bold')
    ax.grid(axis='y',which='major',alpha=.13)

def main():
    p=json.loads((HERE/'analysis/profile_summary.json').read_text());o=json.loads((HERE/'analysis/oracle_summary.json').read_text())
    labels=['Ordinary\nsites','Both\nends','Both ends\n4x noise','Both ends\n16x noise'];pol=p['policies']
    fig,axs=plt.subplots(2,2,figsize=(12,8.4));fig.subplots_adjust(wspace=.3,hspace=.5)
    means_panel(axs[0,0],[p['metrics'][x]['width2'] for x in pol],labels,COLORS,
                'a   Compatible models disagree less','Mean squared response-range width')
    means_panel(axs[0,1],[p['metrics'][x]['mse'] for x in pol],labels,COLORS,
                'b   Accuracy depends on recording precision','Held-out response MSE')
    a=np.asarray(p['metrics']['neither']['width2']);b=np.asarray(p['metrics']['both']['width2']);ax=axs[1,0]
    ax.scatter(a,b,s=24,c=COLORS[1],alpha=.8);limits=[min(a.min(),b.min())*.6,max(a.max(),b.max())*1.5]
    ax.plot(limits,limits,color='#777777',linestyle='--',linewidth=1);ax.set(xscale='log',yscale='log',xlim=limits,ylim=limits,
        xlabel='Range width squared: ordinary sites',ylabel='Range width squared: both ends')
    ax.set_title('c   Paired changes across 40 networks',loc='left',fontweight='bold')
    ops=['neither','known_random4','known_stim','known_readouts','known_both']
    means_panel(axs[1,1],[o['metrics'][x] for x in ops],['None','Four\nordinary','Stimulus\ngain','Readout\ngains','Both-end\ngains'],
        ['#7b8290','#a2a9b3','#c38135','#697da6','#176b66'],'d   Oracle gain knowledge, then refitting','Held-out response MSE')
    fig.suptitle('Endpoint information constrains intervention-response prediction',fontsize=15,y=1.01)
    fig.text(.01,-.02,'Dots: independent networks. Diamonds: arithmetic means and 95% bootstrap intervals.\nResponse ranges use a common MAP-objective allowance of 2; they are numerical feasible spans, not confidence intervals.',fontsize=9,color='#444444')
    for ext in ['png','pdf']:fig.savefig(HERE/f'analysis/mechanism_evidence.{ext}',dpi=180)
    plt.close(fig)
    m=json.loads((HERE/'analysis/method_summary.json').read_text())
    audit=json.loads((HERE/'analysis/method_fit_audit.json').read_text())
    keys=['ensemble_vs_local','prior_cov_vs_local','prior_cv_vs_local']
    names=['Prior-averaged local risk','Prior covariance criterion','Held-out prior criterion']
    fig,ax=plt.subplots(figsize=(10.5,5.2));fig.subplots_adjust(bottom=.25)
    for i,k in enumerate(keys):
        color=['#697da6','#8b7555','#176b66'][i]
        for summary,offset,filled in [(m,-.12,True),(audit,.12,False)]:
            r=summary['comparisons'][k];v=r['change_pct'];lo,hi=r['ci95']
            label=('Five common starts' if filled else 'Additional matched fitting') if i==0 else None
            ax.errorbar(v,i+offset,xerr=[[v-lo],[hi-v]],fmt='o',capsize=4,
                        color=color,markerfacecolor=color if filled else 'white',ms=7,label=label)
    ax.axvline(0,color='#777777',linestyle='--');ax.set_yticks(range(3),names);ax.invert_yaxis()
    ax.set_xlabel('Change in response MSE relative to nominal local selection (%)')
    ax.set_title('Indirect recordings: performance depends on fitting',loc='left',fontweight='bold')
    ax.set_xlim(-65,85);ax.margins(y=.3);ax.legend(frameon=False,fontsize=9,loc='upper right')
    fig.text(.01,.02,'40 independent networks; five recordings; endpoints excluded. Error bars: 95% network-bootstrap intervals.\nOpen markers include additional common starts for all policies on 11 flagged datasets; this check is retrospective.',fontsize=9,color='#444444')
    for ext in ['png','pdf']:fig.savefig(HERE/f'analysis/method_validation.{ext}',dpi=180)
    plt.close(fig)

if __name__=='__main__':main()
