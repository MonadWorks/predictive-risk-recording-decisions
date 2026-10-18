"""Paper figures showing network-level variation, with no dropped networks."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent.parent
A=HERE/'analysis'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':200})
colors=['#9dabb8','#bd8e60','#9280ad','#3e827d']
policies=['neither','stim_only','readouts_only','both']
labels=['Neither\nendpoint','Stimulus\nonly','Three\nreadouts','Both\nends']

def save(fig,name):
    for suffix in ['png','pdf']:fig.savefig(A/f'{name}.{suffix}',bbox_inches='tight')
    plt.close(fig)

def endpoint_plot():
    d=json.loads((A/'endpoint_summary.json').read_text());v=json.loads((A/'validation_summary.json').read_text())
    geo=json.loads((A/'geometry.json').read_text())
    mech=json.loads((A/'mechanism_summary.json').read_text())
    fig,axes=plt.subplots(2,2,figsize=(11,8.3),layout='constrained')
    for ax,data,title in [(axes[0,0],d,'a  Allocation experiment · 40 networks'),(axes[0,1],v,'b  Independent validation · 40 new networks')]:
        rng=np.random.default_rng(31)
        for i,p in enumerate(policies):
            vals=np.array(data['network_means'][p]);ax.scatter(i+rng.uniform(-.13,.13,40),vals,s=16,color=colors[i],alpha=.6)
            ax.plot([i-.22,i+.22],[vals.mean()]*2,color='black',lw=2.3)
        ax.set(yscale='log',xticks=range(4),xticklabels=labels,ylabel='Held-out response MSE',title=title)
        ax.grid(axis='y',alpha=.15)
        c=data['comparisons']['both_vs_neither']
        ax.text(.02,.03,f"Both vs neither: {c['relative_change_percent']:.1f}%\n95% CI [{c['ci95_percent'][0]:.1f}, {c['ci95_percent'][1]:.1f}]%",transform=ax.transAxes,fontsize=9,bbox=dict(facecolor='white',edgecolor='none',alpha=.85))
    ax=axes[1,0];x=np.arange(2)
    for key,color,offset,label in [('first_cohort','#a9bfba',-.17,'First cohort'),('validation_cohort','#3e827d',.17,'Validation cohort')]:
        rr=[mech[key]['comparisons'][m] for m in ['response_mse','passive_mse']]
        vals=np.array([100+r['relative_change_percent'] for r in rr])
        lo=np.array([100+r['ci95_percent'][0] for r in rr]);hi=np.array([100+r['ci95_percent'][1] for r in rr])
        ax.bar(x+offset,vals,width=.32,color=color,label=label,yerr=[vals-lo,hi-vals],capsize=3)
    ax.axhline(100,lw=1,color='#777777',ls='--')
    ax.set(xticks=x,xticklabels=['Stimulus-response\nprediction','Other-input activity\nprediction'],ylabel='Both-end MSE / neither-end MSE (%)',ylim=(0,150),title='c  Benefit is specific to the intended prediction')
    ax.legend(frameon=False,fontsize=9,loc='upper left');ax.grid(axis='y',alpha=.15)
    ax=axes[1,1]
    for data,color,offset,label in [(d,'#a9bfba',-.12,'First cohort'),(v,'#3e827d',.12,'Validation cohort')]:
        for i,key in enumerate(['both_vs_neither','both_vs_stim_only','both_vs_readouts_only']):
            r=data['comparisons'][key];y=-r['relative_change_percent'];lo,hi=-np.array(r['ci95_percent'][::-1])
            ax.errorbar(y,i+offset,xerr=[[y-lo],[hi-y]],fmt='o',capsize=3,color=color,label=label if i==0 else None)
    ax.set(yticks=range(3),yticklabels=['vs neither','vs stimulus only','vs readouts only'],xlabel='MSE reduction from recording both ends (%)',xlim=(88,100),title='d  Joint coverage improves on either end alone')
    ax.legend(frameon=False,fontsize=9,loc='lower left');ax.grid(axis='x',alpha=.15)
    fig.suptitle('Endpoint calibration and prediction of an unseen stimulus response',fontsize=14)
    save(fig,'endpoint_evidence')

def fit_plot():
    d=json.loads((A/'fitting_summary.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(10,3.8),layout='constrained')
    for i,(k,label) in enumerate([('original','Original common start'),('best_of_five','Best of five starts')]):
        r=d[k];x=r['relative_change_percent'];lo,hi=r['ci95_percent']
        axes[0].errorbar(x,i,xerr=[[x-lo],[hi-x]],fmt='o',color=['#9280ad','#3e827d'][i],capsize=4)
    axes[0].axvline(0,lw=1,color='#999999',ls='--');axes[0].set(yticks=[0,1],yticklabels=['Original common start','Best of five starts'],xlabel='Ensemble vs nominal response MSE change (%)',title='a  Same recording sets; shared fitting rule')
    for p,c,label in [('local_vector','#9280ad','Nominal selection'),('ensemble_vector','#3e827d','Ensemble selection')]:
        x=d['network_means_nominal'][p];y=d['network_means_best'][p]
        axes[1].scatter(x,y,s=22,color=c,label=label,alpha=.7)
    lim=[min(axes[1].get_xlim()[0],axes[1].get_ylim()[0]),max(axes[1].get_xlim()[1],axes[1].get_ylim()[1])]
    vals=[*d['network_means_nominal']['local_vector'],*d['network_means_nominal']['ensemble_vector'],*d['network_means_best']['local_vector'],*d['network_means_best']['ensemble_vector']]
    lo,hi=min(vals)*.7,max(vals)*1.4
    axes[1].plot([lo,hi],[lo,hi],color='#999999',ls='--',lw=1)
    axes[1].set(xscale='log',yscale='log',xlim=(lo,hi),ylim=(lo,hi),xlabel='MSE from original start',ylabel='MSE from best of five starts',title='b  Each point is one network')
    axes[1].legend(frameon=False,fontsize=8)
    save(fig,'fitting_sensitivity')

if __name__=='__main__':endpoint_plot();fit_plot()
