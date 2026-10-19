"""Independent confirmation and actual-recording information comparisons."""
from pathlib import Path
import json,sys
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(HERE.parent/'round4/code'))
from figures4 import plt,np,means,ratio,ratio_axis,TEAL,GREY,GOLD,BLUE


def main():
    d=json.loads((HERE/'analysis/summary.json').read_text())
    old=json.loads((HERE.parent/'round4/analysis/oracle_data_fit_audit_summary.json').read_text())
    plt.rcParams.update({'font.size':11})
    fig,axes=plt.subplots(2,2,figsize=(8.5,8.4))
    fig.subplots_adjust(left=.16,right=.98,top=.94,bottom=.13,wspace=.95,hspace=.85)
    prior=old['comparisons']['endpoints_recurrence8_vs_endpoint_ordinary8']
    fresh=d['primary']['response_mse/oracle_combinations_vs_oracle_ordinary']
    ratio(axes[0,0],prior,0,GREY)
    ratio(axes[0,0],fresh,1-.08,TEAL,label='95% interval')
    ratio(axes[0,0],fresh,1+.08,BLUE,False,ci='ci_family_three',label='Adjusted for 3 tests')
    ratio_axis(axes[0,0],['Earlier follow-up\n40 networks','Independent test\n40 networks'],
               'Response MSE ratio\nRecurrent / ordinary information')
    axes[0,0].set_title('a   Recurrent information',loc='left',fontweight='bold',fontsize=11)
    axes[0,0].legend(frameon=False,fontsize=9,loc='best')
    keys=['endpoints4','random5','combination5','response5']
    labels=['Endpoints\n4 sites','Random\n5 sites','Comb.\n5 sites','Response\n5 sites']
    colors=[GREY,GOLD,TEAL,BLUE]
    means(axes[0,1],[d['metrics']['response_mse'][k] for k in keys],labels,colors,'Held-out response MSE')
    axes[0,1].tick_params(axis='x',labelsize=9)
    axes[0,1].set_title('b   Calibration recordings',loc='left',fontweight='bold',fontsize=11)
    tests=[('profile_width_squared','Profile width squared'),('combination_mse','Combination\nestimation MSE'),
           ('response_mse','Response MSE')]
    for i,(metric,label) in enumerate(tests):
        key=f'{metric}/combination5_vs_random5'
        test=d['primary'].get(key,d['secondary'].get(key))
        ratio(axes[1,0],test,i-.08,TEAL)
        if key in d['primary']:
            ratio(axes[1,0],test,i+.08,BLUE,False,ci='ci_family_three')
    ratio_axis(axes[1,0],[x[1] for x in tests],'Ratio: combination-targeted\n/ random fifth site')
    axes[1,0].set_title('c   Targeted versus random',loc='left',fontweight='bold',fontsize=11)
    for i,(metric,label) in enumerate(tests):
        test=d['secondary'][f'{metric}/combination5_vs_response5']
        ratio(axes[1,1],test,i,TEAL)
    ratio_axis(axes[1,1],[x[1] for x in tests],'Ratio: combination-targeted\n/ response-targeted site')
    axes[1,1].set_title('d   Targeted versus response',loc='left',fontweight='bold',fontsize=11)
    for ext in ['png','pdf']:
        fig.savefig(HERE/'analysis'/f'recording_information.{ext}',dpi=190)
    plt.close(fig)


if __name__=='__main__':
    main()
