"""Publication-size views of frozen v2 analysis tables. No new inference.

Run from this package or any cwd. The renderer only reads bundled source_data.
The existing estimands, confidence limits, pairing and complete samples remain
unchanged. Source hashes, displayed values, physical sizes and text preflight
are saved with the figure outputs.
"""
from pathlib import Path
import csv,hashlib,json,os,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/mpl'))
os.environ.setdefault('XDG_CACHE_HOME',str(ROOT/'.cache/xdg'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle,FancyArrowPatch
from matplotlib.ticker import LogLocator,LogFormatterMathtext,MultipleLocator,NullLocator,NullFormatter
sys.path.insert(0,str(ROOT/'research-writing-figures/scripts'))
from figure_style import apply_style,size_mm,export,COLORS
apply_style()
DATA=ROOT/'source_data';OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
INK=COLORS['ink'];BLUE=COLORS['scalar'];ORANGE=COLORS['vector'];GREY=COLORS['reference']
MANIFEST={'input_files':{},'figures':{},'scientific_changes':False,
          'statistical_policy':'reuse frozen v2 network means and confidence limits; no new tests, filtering or bootstrap',
          'encoding':{'blue':'single response','vermilion':'three responses','open':'nominal method/forecast where individual methods are plotted','filled':'ensemble method/forecast where individual methods are plotted','paired_scatter':'one point contains both methods; colour indicates objective, axes indicate approximation'}}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):
    p=DATA/name;MANIFEST['input_files'][name]=sha(p)
    with p.open() as f:return list(csv.DictReader(f))
def number(r,k):return float(r[k])
def write(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def tag(fig,label,x,y):fig.text(x,y,label,fontweight='bold',fontsize=10,va='top')
def title(ax,text):ax.set_title(text,loc='left',pad=9)
def clean(ax):
    ax.tick_params(which='minor',length=1.5,width=.4)
    ax.set_axisbelow(True)
def identity(ax,lo,hi):
    ax.set_xscale('log');ax.set_yscale('log');ax.set_xlim(lo,hi);ax.set_ylim(lo,hi)
    ax.plot([lo,hi],[lo,hi],color='#8D969D',lw=.8,ls=(0,(3,3)),zorder=0)
    for a in [ax.xaxis,ax.yaxis]:
        a.set_major_locator(LogLocator(base=10,numticks=5));a.set_major_formatter(LogFormatterMathtext())
        a.set_minor_locator(NullLocator());a.set_minor_formatter(NullFormatter())
    clean(ax)
def finish(fig,name,meta):
    fig.canvas.draw();renderer=fig.canvas.get_renderer();width,height=fig.canvas.get_width_height()
    undrawn_tick_labels=set()
    for ax in fig.axes:
        for axis in (ax.xaxis,ax.yaxis):
            low,high=sorted(axis.get_view_interval())
            for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                if not low <= tick.get_loc() <= high:
                    undrawn_tick_labels.update((tick.label1,tick.label2))
    outside=[]
    for t in fig.findobj(matplotlib.text.Text):
        if not t.get_visible() or not t.get_text().strip() or t in undrawn_tick_labels:continue
        b=t.get_window_extent(renderer)
        if b.x0 < -1 or b.y0 < -1 or b.x1 > width+1 or b.y1 > height+1:
            outside.append(t.get_text())
    if outside:raise RuntimeError(f'{name}: text outside page: {outside}')
    export(fig,OUT/name)
    MANIFEST['figures'][name]=dict(meta,width_mm=round(fig.get_figwidth()*25.4,3),
        height_mm=round(fig.get_figheight()*25.4,3),text_bounds='PASS',
        output_sha256={ext:sha((OUT/name).with_suffix('.'+ext)) for ext in ['pdf','svg','png']})
    plt.close(fig)

def schematic():
    fig=plt.figure(figsize=size_mm(180,108));ax=fig.add_axes([0,0,1,1]);ax.set_axis_off();ax.set_xlim(0,1);ax.set_ylim(0,1)
    tag(fig,'a',.035,.96);fig.text(.085,.945,'Known model, limited measurements, independent response evaluation',fontsize=9)
    cols=[.135,.37,.605,.85]
    heads=['Design inputs','Recording set','Common inference','Response test']
    bodies=['Known J and prior\nCalibration input\nSpecified stimulus / readouts',
            'Greedy selection\nBudget M\nCommon feasible pool',
            'Observe selected nodes\nGaussian MAP\nPredict from fitted model',
            'Stimulus minus control\nIntegrated response q\nScore against hidden truth']
    for x,h,b in zip(cols,heads,bodies):
        ax.text(x,.83,h,ha='center',fontweight='bold',fontsize=8.5)
        ax.text(x,.735,b,ha='center',va='center',linespacing=1.5,fontsize=8)
    for x,y in zip(cols[:-1],cols[1:]):
        ax.add_patch(FancyArrowPatch((x+.079,.80),(y-.079,.80),arrowstyle='-|>',mutation_scale=10,color=GREY,lw=.8))
    ax.plot([.08,.94],[.635,.635],color=COLORS['grid'],lw=.7)
    tag(fig,'b',.035,.58);ax.text(.085,.565,'Two design factors',fontsize=9)
    x0,y0,w,h=.20,.13,.35,.32
    ax.text(x0+w*.25,y0+h+.055,'Single response',color=BLUE,ha='center',fontsize=8.5)
    ax.text(x0+w*.75,y0+h+.055,'Three responses',color=ORANGE,ha='center',fontsize=8.5)
    for row,approx in enumerate(['Nominal','Ensemble']):
        yy=y0+h*(.75-.5*row);ax.text(x0-.025,yy,approx,ha='right',va='center',fontsize=8.5)
        for col,color in enumerate([BLUE,ORANGE]):
            xx=x0+w*(.25+.5*col)
            ax.add_patch(Rectangle((x0+col*w/2,y0+(1-row)*h/2),w/2,h/2,facecolor='#F6F8F9',edgecolor='white',lw=2))
            ax.plot(xx-.025,yy,'o' if col==0 else 's',ms=5,mfc=color if row else 'white',mec=color,mew=1)
            ax.text(xx+.008,yy,[['LS','LV'],['ES','EV']][row][col],va='center',fontsize=9)
    tag(fig,'c',.615,.58);ax.text(.665,.565,'Two evaluation questions',fontsize=9)
    ax.text(.665,.435,'1  Recording decisions',fontweight='bold',fontsize=8.5)
    ax.text(.665,.365,'Change the selected data.\nCompare actual response MSE.',fontsize=8,linespacing=1.5)
    ax.text(.665,.25,'2  Risk forecasts',fontweight='bold',fontsize=8.5)
    ax.text(.665,.18,'Fix data and point predictions.\nCompare MSE-forecast scores.',fontsize=8,linespacing=1.5)
    finish(fig,'fig1_study_design',{'kind':'conceptual schematic; no empirical trajectory or biological apparatus depicted'})

def overview():
    """Reuse the separately reconstructed, audited fixed-instance vector figure.

    Reconstruction code and complete arrays are bundled in figure_redesign/
    data_overview; regeneration from the frozen simulator needs companion v2.
    This presentation-only entry point does not rerun the simulator or MAP fits.
    """
    folder=ROOT/'figure_redesign/data_overview'
    record=json.loads((folder/'manifest.json').read_text())
    assert record['q_abs_difference']==0 and record['network_id']==5000
    hashes={}
    for ext in ('pdf','svg','png'):
        name=f'fig1_data_overview.{ext}';source=folder/name
        assert sha(source)==record['output_sha256'][name]
        shutil.copyfile(source,OUT/name);hashes[ext]=sha(OUT/name)
    MANIFEST['figures']['fig1_data_overview']={
        'kind':'fixed illustrative simulated network; not a method-effect estimate',
        'independent_networks':1,'network_id':5000,'width_mm':180,'height_mm':80,
        'q_rebuilt':record['q_rebuilt'],'q_csv':record['q_csv'],
        'text_bounds':'separate rendered PNG and PDF inspection recorded in source manifest',
        'source_manifest_sha256':sha(folder/'manifest.json'),'output_sha256':hashes}

def primary(networks,effects):
    rows=[r for r in networks if r['condition']=='broad' and r['pool']=='exclude_endpoints' and r['budget']=='3']
    ids=sorted({int(r['network_id']) for r in rows});assert len(ids)==40
    lookup={(int(r['network_id']),r['method']):number(r,'mse') for r in rows}
    fig=plt.figure(figsize=size_mm(180,138))
    points=[]
    for i,(objective,local,ensemble,color) in enumerate([
        ('Single response','local_scalar','ensemble_scalar',BLUE),
        ('Three responses','local_vector','ensemble_vector',ORANGE)]):
        ax=fig.add_axes([.12+i*.49,.49,.32,.4174]);tag(fig,'ab'[i],.035+i*.49,.955)
        x=np.array([lookup[n,local] for n in ids]);y=np.array([lookup[n,ensemble] for n in ids])
        assert np.all(x>0) and np.all(y>0)
        ax.set_xscale('log');ax.set_xlim(1e-11,1e-2);ax.set_ylim(-1.65,1.65)
        ax.axhline(0,color='#8D969D',lw=.8,ls=(0,(3,3)),zorder=0)
        ratio=np.log2(y/x)
        ax.scatter(x,ratio,s=18,c=color,edgecolors='white',linewidths=.35,alpha=.85,zorder=2)
        ax.set_xlabel('Nominal design MSE (q²)');ax.set_ylabel(r'Within-network error ratio ($\log_2$ E/N)');title(ax,objective)
        ax.set_yticks([-1.5,-1,-.5,0,.5,1,1.5]);ax.set_xticks([1e-10,1e-7,1e-4]);ax.xaxis.set_major_formatter(LogFormatterMathtext())
        ax.xaxis.set_minor_locator(NullLocator());ax.xaxis.set_minor_formatter(NullFormatter())
        for n,xx,yy,rr in zip(ids,x,y,ratio):points.append(dict(network_id=n,objective=objective,nominal_mse=xx,ensemble_mse=yy,descriptive_log2_ratio=rr))
    tag(fig,'c',.035,.386)
    ax=fig.add_axes([.245,.14,.40,.18]);ax.axvline(0,color='#9AA2A8',lw=.8,ls=(0,(3,3)),zorder=0)
    chosen=[]
    for j,(contrast,color,lab) in enumerate([
        ('ensemble_scalar - local_scalar',BLUE,'Single response'),
        ('ensemble_vector - local_vector',ORANGE,'Three responses')]):
        es=[r for r in effects if r['condition']=='broad' and r['pool']=='exclude_endpoints' and r['budget']=='3' and r['contrast']==contrast and r['metric']=='mse']
        assert len(es)==1;e=es[0];assert e['primary']=='True' and number(e,'confidence_level')==.975
        vals=np.array([number(e,k) for k in ['effect','ci_low','ci_high']])*1e5
        a,b=contrast.split(' - ')
        assert np.isclose(vals[0]/1e5,np.mean([lookup[n,a]-lookup[n,b] for n in ids]),rtol=1e-12,atol=1e-14)
        yy=1-j;ax.plot(vals[1:], [yy,yy],color=color,lw=1.4)
        ax.plot(vals[0],yy,'o' if j==0 else 's',color=color,ms=4.5)
        ax.text(1.10,yy,f'{vals[0]:+.3f} [{vals[1]:+.3f}, {vals[2]:+.3f}]',transform=ax.get_yaxis_transform(),va='center',fontsize=8)
        chosen.append(e)
    ax.set_yticks([1,0],['Single response','Three responses']);ax.tick_params(axis='y',length=0,pad=8)
    ax.set_ylim(-.6,1.6);ax.set_xlim(-1.6,.8);ax.set_xticks([-1.5,-1,-.5,0,.5]);ax.set_xlabel(r'Mean MSE difference ($\times10^{-5}$ q$^2$)')
    ax.spines[['left','top','right']].set_visible(False)
    fig.text(.245,.365,'Ensemble minus nominal',fontsize=9)
    fig.text(.685,.365,'Estimate [97.5% CI]',fontsize=8)
    fig.text(.245,.047,'Lower values favour ensemble design',fontsize=8,color=GREY)
    write('fig2_network_pairs.csv',points);write('fig2_effects.csv',chosen)
    finish(fig,'fig2_recording_decisions',{'independent_networks':40,'paired_points_per_panel':40,'main_interval':.975,'all_points_retained':True,'display_only_diagnostic':'log2 of each network ensemble/nominal MSE, not the primary or aggregate relative estimand','x_log_limits':[1e-11,1e-2],'y_log2_ratio_limits':[-1.65,1.65]})

def forecasts(networks,summary):
    rows=[r for r in networks if r['condition']=='broad' and r['pool']=='exclude_endpoints' and r['budget']=='3' and r['recording_policy']=='local_scalar']
    rows=sorted(rows,key=lambda r:int(r['network_id']));assert len(rows)==40
    fig=plt.figure(figsize=size_mm(180,100));a=fig.add_axes([.12,.235,.35,.63]);a.set_box_aspect(1)
    tag(fig,'a',.035,.95);title(a,'Risk forecasts at the same recording set')
    actual=np.array([number(r,'raw_mse') for r in rows]);vn=np.array([number(r,'nominal_risk') for r in rows]);ve=np.array([number(r,'ensemble_risk') for r in rows])
    for x1,x2,y in zip(vn,ve,actual):a.plot([x1,x2],[y,y],color='#C5CCD1',lw=.6,zorder=0)
    a.scatter(vn,actual,s=15,facecolors='white',edgecolors=BLUE,lw=.8,label='Nominal',zorder=2)
    a.scatter(ve,actual,s=15,facecolors=BLUE,edgecolors='white',lw=.25,label='Ensemble',zorder=3)
    identity(a,3e-8,1e-2);a.set_xlabel('Forecast risk (q²)');a.set_ylabel('Actual response MSE (q²)')
    a.legend(loc='upper left',handletextpad=.2,borderpad=.1,labelspacing=.4,fontsize=7.5)
    b=fig.add_axes([.64,.57,.31,.29]);tag(fig,'b',.55,.95);title(b,'Complete network differences')
    diff=np.array([number(r,'score_difference') for r in rows]);jitter=np.random.default_rng(42).permutation(np.linspace(-.19,.19,len(rows)))
    b.axvline(0,color='#9AA2A8',lw=.8,ls=(0,(3,3)),zorder=0)
    b.scatter(diff,1+jitter,s=14,c=BLUE,edgecolors='white',lw=.3,alpha=.8)
    p=summary['primary'];effect=p['score_difference'];lo=p['score_difference_ci_low'];hi=p['score_difference_ci_high']
    assert np.isclose(diff.mean(),effect,rtol=1e-13,atol=1e-14)
    b.set_yticks([]);b.set_ylim(.55,1.45);b.set_xlim(-12.5,2)
    b.set_xticks([-12,-8,-4,0]);b.set_xlabel('Network mean score difference');b.spines[['left','right','top']].set_visible(False)
    c=fig.add_axes([.64,.235,.31,.16]);tag(fig,'c',.55,.43)
    c.axvline(0,color='#9AA2A8',lw=.8,ls=(0,(3,3)),zorder=0)
    c.errorbar(effect,0,xerr=[[effect-lo],[hi-effect]],fmt='D',color=INK,ms=4,capsize=3,capthick=.8,elinewidth=1.2)
    c.set_xlim(-1.3,.25);c.set_ylim(-.6,.6);c.set_yticks([]);c.set_xticks([-1,-.5,0]);c.set_xlabel('Population mean score difference')
    c.spines[['left','right','top']].set_visible(False)
    c.text(0,1.2,f'Mean {effect:+.3f}; 95% CI [{lo:+.3f}, {hi:+.3f}]',transform=c.transAxes,fontsize=7.5)
    write('fig3_networks.csv',rows)
    finish(fig,'fig3_risk_forecasts',{'independent_networks':40,'risk_points':80,'paired_score_points':40,'score_mean':effect,'score_ci95':[lo,hi],'same_point_predictions':True,'all_points_retained':True,'individual_distribution_x_limits':[-12.5,2],'population_interval_x_limits':[-1.3,.25],'different_scales_for_distinct_statistical_objects':True})

def extension(effects):
    fig=plt.figure(figsize=size_mm(180,112));chosen=[]
    order=[('all','5'),('all','10'),('exclude_endpoints','5'),('exclude_endpoints','10')]
    for j,(contrast,color,lab) in enumerate([
        ('ensemble_scalar - local_scalar',BLUE,'Single-response objective'),
        ('ensemble_vector - local_vector',ORANGE,'Three-response objective')]):
        ax=fig.add_axes([.20+j*.43,.24,.33,.59]);tag(fig,'ab'[j],.035+j*.50,.945);title(ax,lab)
        ax.axvline(0,color='#9AA2A8',lw=.8,ls=(0,(3,3)),zorder=0)
        for k,(pool,m) in enumerate(order):
            rs=[r for r in effects if r['pool']==pool and r['budget']==m and r['contrast']==contrast and r['metric']=='mse'];assert len(rs)==1
            r=rs[0];assert r['primary']=='False' and number(r,'confidence_level')==.95
            v=np.array([number(r,q) for q in ['relative_mse_difference','relative_mse_ci_low','relative_mse_ci_high']])*100
            yy=3-k;ax.plot(v[1:],[yy,yy],color=color,lw=1.25);ax.plot(v[0],yy,'o' if j==0 else 's',color=color,ms=4)
            chosen.append(r)
        ax.set_ylim(-.55,3.6);ax.set_xlim(-110,220);ax.set_xticks([-100,0,100,200])
        labels=['All sites · M=5','All sites · M=10','No endpoints · M=5','No endpoints · M=10']
        ax.set_yticks([3,2,1,0],labels if j==0 else ['']*4);ax.tick_params(axis='y',length=0,pad=6)
        ax.set_xlabel('Relative mean MSE change (%)');ax.spines[['left','top','right']].set_visible(False)
    fig.text(.20,.075,'Exploratory: 8 independent networks; pointwise 95% cluster intervals',fontsize=8,color=GREY)
    write('fig4_effects.csv',chosen)
    finish(fig,'fig4_model_extension',{'independent_networks':8,'contrasts':8,'exploratory':True,'interval':.95,'shared_x_limits':[-110,220],'all_intervals_retained':True})

def tails(rows):
    fig=plt.figure(figsize=size_mm(180,90));points=[]
    for j,(contrast,color,lab) in enumerate([
        ('ensemble_scalar - local_scalar',BLUE,'Single response'),
        ('ensemble_vector - local_vector',ORANGE,'Three responses')]):
        rs=[r for r in rows if r['contrast']==contrast];assert len(rs)==40
        x=np.sort([number(r,'paired_mse_difference')*1e5 for r in rs]);y=np.arange(1,41)/40
        ax=fig.add_axes([.12+j*.49,.23,.34,.61]);tag(fig,'ab'[j],.035+j*.49,.95);title(ax,lab)
        ax.axvline(0,color='#9AA2A8',lw=.8,ls=(0,(3,3)));ax.step(x,y,where='post',color=color,lw=1.2)
        ax.scatter(x,y,s=6,color=color);ax.set_ylim(0,1.03);ax.set_xlabel(r'Paired MSE difference ($\times10^{-5}$ q$^2$)');ax.set_ylabel('Fraction of networks')
        points.extend(rs)
    write('figS1_paired_differences.csv',points)
    finish(fig,'figS1_complete_paired_distributions',{'independent_networks':40,'points_each':40,'complete_tails_retained':True,'display_transform':'paired MSE difference × 1e5; scientific estimand unchanged'})

def strata(networks,summary):
    labels=['LS','ES','LV','EV','Activity','Random'];methods=['local_scalar','ensemble_scalar','local_vector','ensemble_vector','local_activity','random']
    summaries=summary['metric_summaries']
    for cidx,(condition,header) in enumerate([('matched','Matched uncertainty'),('broad','Broad uncertainty'),('bias_shift','Hidden bias shift')]):
        fig=plt.figure(figsize=size_mm(180,142))
        for panel,(pool,budget) in enumerate([('all','3'),('exclude_endpoints','3'),('all','6'),('exclude_endpoints','6')]):
            ax=fig.add_axes([.12+(panel%2)*.49,.60-(panel//2)*.46,.34,.28])
            tag(fig,'abcd'[panel],.035+(panel%2)*.49,.955-(panel//2)*.46)
            title(ax,f'{"All sites" if pool=="all" else "Endpoints excluded"} · M={budget}')
            for m,method in enumerate(methods):
                rr=sorted([r for r in networks if r['condition']==condition and r['pool']==pool and r['budget']==budget and r['method']==method],key=lambda r:int(r['network_id']))
                assert len(rr)==40
                values=np.array([number(r,'mse') for r in rr]);assert np.all(values>0)
                color=BLUE if 'scalar' in method else ORANGE if 'vector' in method else GREY
                marker='o' if 'scalar' in method else 's' if 'vector' in method else '^' if method=='local_activity' else 'x'
                xpos=m+np.random.default_rng(42).permutation(np.linspace(-.16,.16,40))
                filled=method.startswith('ensemble')
                if marker=='x':ax.scatter(xpos,values,s=9,c=color,marker=marker,lw=.5,alpha=.5)
                else:ax.scatter(xpos,values,s=9,facecolors=color if filled else 'white',edgecolors=color,lw=.5,marker=marker,alpha=.6)
                ss=[r for r in summaries if r['condition']==condition and r['pool']==pool and str(r['budget'])==budget and r['method']==method];assert len(ss)==1
                s=ss[0];ax.plot([m,m],[s['mse_ci95_low'],s['mse_ci95_high']],color=INK,lw=.85,zorder=5)
                ax.plot([m-.16,m+.16],[s['mse'],s['mse']],color=INK,lw=1.1,zorder=6)
            ax.set_yscale('log');ax.set_ylim(1e-15,1e-2);ax.set_xlim(-.5,5.5)
            ax.set_xticks(range(6),labels,rotation=30,ha='right');ax.set_ylabel('Response MSE (q²)')
            ax.set_yticks([1e-14,1e-10,1e-6,1e-2]);ax.yaxis.set_major_formatter(LogFormatterMathtext());ax.yaxis.set_minor_locator(NullLocator());ax.yaxis.set_minor_formatter(NullFormatter())
        finish(fig,f'figS{cidx+2}_{condition}_conditions',{'condition':condition,'independent_networks':40,'points_per_method_panel':40,'pointwise_interval':.95,'panels':4,'shared_log_limits':[1e-15,1e-2],'all_points_retained':True,'panel_title_context':header})

def positive_control(rows):
    fig=plt.figure(figsize=size_mm(90,88));ax=fig.add_axes([.23,.23,.69,.66]);
    x=np.array([number(r,'analytic_map_mse') for r in rows]);y=np.array([number(r,'actual_mc_map_mse') for r in rows])
    ax.plot([0,1],[0,1],color='#9AA2A8',lw=.8,ls=(0,(3,3)),zorder=0)
    ax.scatter(x,y,s=10,facecolors='white',edgecolors=INK,lw=.55,alpha=.6)
    ax.set_xlim(0,1);ax.set_ylim(0,1);ax.set_box_aspect(1)
    ax.set_xlabel('Analytic MAP MSE');ax.set_ylabel('Monte Carlo MAP MSE');title(ax,'Linear-Gaussian positive control')
    finish(fig,'figS5_linear_positive_control',{'independent_systems':12,'target_design_evaluations':len(rows),'monte_carlo_draws_per_system':8192,'all_points_retained':True,'confidence_intervals':'none displayed'})

def main():
    n=read('holdout_network_metrics.csv');e=read('holdout_paired_effects.csv')
    fn=read('forecast_network_metrics.csv');ne=read('n100_paired_effects.csv');paired=read('holdout_primary_paired.csv');control=read('linear_control.csv')
    for name in ['holdout_summary.json','forecast_summary.json','n100_summary.json']:
        MANIFEST['input_files'][name]=sha(DATA/name)
    hs=json.loads((DATA/'holdout_summary.json').read_text());fs=json.loads((DATA/'forecast_summary.json').read_text())
    overview();primary(n,e);forecasts(fn,fs);extension(ne);tails(paired);strata(n,hs);positive_control(control)
    (OUT/'figure_manifest.json').write_text(json.dumps(MANIFEST,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'figures':len(MANIFEST['figures']),'source_data_unchanged':True,'new_statistical_tests':0,'out':str(OUT)},indent=2))

if __name__=='__main__':main()
