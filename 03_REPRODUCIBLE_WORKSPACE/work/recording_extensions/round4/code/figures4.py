"""Scientific figures from complete network-paired round-four summaries."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
HERE=Path(__file__).resolve().parent.parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.bbox':'tight'})
TEAL='#176b66';GREY='#7b8290';GOLD='#c38135';BLUE='#697da6'
def load(name):return json.loads((HERE/'analysis'/name).read_text())
def save(fig,name):
    for ext in ['png','pdf']:fig.savefig(HERE/'analysis'/f'{name}.{ext}',dpi=190)
    plt.close(fig)
def means(ax,vals,labels,colors,ylabel):
    rng=np.random.default_rng(381);n=len(vals[0]);ids=rng.integers(n,size=(10000,n))
    for i,v in enumerate(vals):
        v=np.asarray(v);ci=np.percentile(v[ids].mean(1),[2.5,97.5]);mean=v.mean()
        ax.scatter(i+rng.uniform(-.14,.14,n),v,s=13,alpha=.45,color=colors[i])
        ax.plot([i,i],ci,color='black',lw=1.3);ax.scatter([i],[mean],marker='D',s=24,c='black',zorder=5)
    ax.set_xticks(range(len(vals)),labels);ax.set_yscale('log');ax.set_ylabel(ylabel);ax.grid(axis='y',alpha=.15)
def ratio(ax,r,y,color=TEAL,filled=True,ci='ci95',label=None):
    v=1+r['change_pct']/100;lo,hi=1+np.asarray(r[ci])/100
    ax.plot([lo,hi],[y,y],color=color,lw=1.5)
    ax.plot([lo,lo],[y-.045,y+.045],color=color,lw=1)
    ax.plot([hi,hi],[y-.045,y+.045],color=color,lw=1)
    ax.scatter([v],[y],s=35,edgecolor=color,facecolor=color if filled else 'white',zorder=5,label=label)
def ratio_axis(ax,labels,xlabel):
    ax.axvline(1,color='#888888',ls='--',lw=1);ax.set_xscale('log');ax.set_yticks(range(len(labels)),labels);ax.invert_yaxis();ax.set_xlabel(xlabel);ax.grid(axis='x',alpha=.12);ax.margins(y=.18)
def main(phase="all"):
    if phase in ('all','mechanism'):
        o=load('oracle_data_fit_audit_summary.json');v=load('mechanism_validation_summary.json')
        fig,axs=plt.subplots(1,2,figsize=(12,4.7));fig.subplots_adjust(wspace=.42,bottom=.22)
        keys=['ordinary4','ordinary8','recurrence4','endpoints4','endpoint_ordinary8','endpoints_recurrence8']
        means(axs[0],[o['metrics'][k] for k in keys],['Ordinary\n4','Ordinary\n8','Recurrent\n4','Endpoint\n4','Ends +\nordinary','Ends +\nrecurrent'],[GREY,GREY,GOLD,BLUE,GREY,TEAL],'Held-out response MSE')
        axs[0].tick_params(axis='x',labelsize=9)
        axs[0].set_title('a   Known gain combinations, then refitting',loc='left',fontweight='bold')
        for i,k in enumerate(['input','recurrence','readout']):ratio(axs[1],v['component_comparisons'][k],i,[GOLD,BLUE,TEAL][i])
        ratio_axis(axs[1],['Input factor','Recurrent factor','Readout factor'],'Contribution ratio: endpoint / ordinary recording')
        axs[1].set_title('b   Finite-response error decomposition',loc='left',fontweight='bold')
        fig.text(.01,.015,'40 new paired networks. a: identical five ordinary observations; dots are networks, diamonds are means with 95% intervals.\nb: exact three-factor Shapley decomposition of fitted-to-true response differences; intervals resample networks.',fontsize=9,color='#444444')
        save(fig,'parameter_mechanism')
    if phase in ('all','robustness'):
        r=load('robustness_summary.json')
        keys=['matched_rank2','augmented_rank6','random_rank6','connectivity_error','initial_state_error','positive_gain']
        labels=['Matched rank two','Rank six: augmented','Rank six: independent','Connectivity error','Initial-state error','Positive gains']
        fig,ax=plt.subplots(figsize=(10.5,5.1));fig.subplots_adjust(left=.25,bottom=.21)
        for i,k in enumerate(keys):
            ratio(ax,r[k]['comparison'],i-.10,TEAL,True,label='Pointwise 95%' if i==0 else None)
            ratio(ax,r[k]['comparison'],i+.10,GREY,False,ci='ci_bonferroni_six',label='Six-comparison interval' if i==0 else None)
        ratio_axis(ax,labels,'Response MSE ratio: joint endpoint / ordinary recording')
        ax.set_title('Endpoint allocation across structural and model perturbations',loc='left',fontweight='bold');ax.legend(frameon=False,fontsize=9,loc='upper right')
        fig.text(.015,.025,'40 independent base seeds, paired across all six conditions; five recordings in every allocation.\nStructural variants are not counted as independent replicates. Dashed line: equal mean MSE.',fontsize=9,color='#444444')
        save(fig,'structure_robustness')
    if phase in ('all','allocation'):
        a=load('allocation_summary.json');fig,axs=plt.subplots(1,2,figsize=(12,5.2));fig.subplots_adjust(wspace=.60,bottom=.23)
        keys=['ensemble_greedy','endpoint_joint','nominal_greedy','stimulus_first','random_all']
        labels=['Ensemble greedy','Endpoint-only search','Nominal greedy','Stimulus first','Random sites']
        for i,k in enumerate(keys):ratio(axs[0],a['comparisons']['endpoint_pair_vs_'+k],i,TEAL)
        ratio_axis(axs[0],labels,'Response MSE ratio: pair-seeded / comparator');axs[0].set_title('a   Average over six budget/precision settings',loc='left',fontweight='bold',fontsize=10)
        labels=[]
        for i,(k,d) in enumerate(a['strata'].items()):
            b,p=k.split('_',1);labels.append(b+' sites / '+{'uniform':'equal noise','stimulus_noisy':'noisy stimulus','readouts_noisy':'noisy readouts'}[p])
            for pol,offset,color,filled,label in [('ensemble_greedy',-.1,TEAL,True,'Versus ensemble greedy'),('endpoint_joint',.1,GOLD,False,'Versus endpoint-only search')]:
                ratio(axs[1],d['comparisons']['endpoint_pair_vs_'+pol],i+offset,color,filled,label=label if i==0 else None)
        ratio_axis(axs[1],labels,'Response MSE ratio: pair-seeded / comparator');axs[1].set_title('b   Each setting retained separately',loc='left',fontweight='bold',fontsize=10)
        axs[1].xaxis.set_major_locator(ticker.FixedLocator([.8,1.,1.25,1.6,2.]))
        axs[1].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x,pos:f'{x:g}'))
        axs[1].xaxis.set_minor_formatter(ticker.NullFormatter())
        axs[1].legend(frameon=False,fontsize=8,loc='best')
        fig.text(.015,.015,'40 independent networks, six paired settings per network; network-level bootstrap 95% intervals.\nThe primary comparison averages within each network first. All policies share observations and nine-start fitting for identical sets.',fontsize=9,color='#444444');save(fig,'limited_budget')
    if phase in ('all','controls'):
        v=load('mechanism_validation_summary.json')
        fig,axs=plt.subplots(1,2,figsize=(12,5.1));fig.subplots_adjust(wspace=.55,bottom=.28)
        rng=np.random.default_rng(458)
        for j,p in enumerate(['neither','both']):
            for i,k in enumerate(['endpoint','endpoint_recurrence','random8']):
                values=v['gradient_fractions'][p][k];x=i+(j-.5)*.30
                axs[0].scatter(x+rng.uniform(-.05,.05,len(values)),values,color=[GREY,TEAL][j],s=10,alpha=.4)
                axs[0].plot([x-.07,x+.07],[np.median(values)]*2,color=[GREY,TEAL][j],lw=3,label=['Ordinary recordings','Endpoint recordings'][j] if i==0 else None)
        axs[0].set_xticks(range(3),['Four\nendpoints','Endpoint +\nrecurrent','Eight random\ncombinations']);axs[0].set_ylim(-.04,1.04);axs[0].set_ylabel('Fraction of local squared response sensitivity');axs[0].legend(frameon=False,fontsize=8,loc='upper center',bbox_to_anchor=(.5,-.19),ncol=2);axs[0].set_title('a   Local sensitivity projection',loc='left',fontweight='bold')
        labels=[]
        for i,(p,rms) in enumerate([(p,r) for p in ['neither','both'] for r in ['0.1','0.3']]):
            labels.append(('Ordinary' if p=='neither' else 'Endpoints')+' / RMS '+rms)
            for b,off,c,f,label in [('random8',-.1,TEAL,True,'Versus eight random constraints'),('endpoint',.1,GOLD,False,'Versus four endpoint constraints')]:
                ratio(axs[1],v['perturbation_comparisons'][f'{p}/{rms}/endpoint_recurrence_vs_{b}'],i+off,c,f,label=label if i==0 else None)
        ratio_axis(axs[1],labels,'Mean squared response change ratio');axs[1].set_title('b   Finite changes preserving combinations',loc='left',fontweight='bold');axs[1].legend(frameon=False,fontsize=8,loc='best')
        fig.text(.015,.015,'40 new networks. Dots: individual networks; bars in a: medians. b: paired 95% network-bootstrap intervals.\nParameter changes have equal norm in prior units; these controls preserve specified combinations, not the calibration fit.',fontsize=9,color='#444444');save(fig,'combination_controls')
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--phase',default='all',choices=['all','mechanism','robustness','allocation','controls']);main(ap.parse_args().phase)
