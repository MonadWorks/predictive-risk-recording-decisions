"""Fig.1: fixed, non-selected illustrative case regenerated from frozen code.

No inference, experiment rerun, or image-generation model. Only the frozen
teacher trajectories/noise for J5000 broad truth0 noise0 are reconstructed.
"""
import csv,hashlib,importlib.util,json,os,sys
from pathlib import Path
import numpy as np
os.environ.setdefault('MPLBACKEND','Agg')
os.environ.setdefault('MPLCONFIGDIR','/tmp/icbr-data-overview-mpl')
os.environ.setdefault('NUMBA_CACHE_DIR','/tmp/icbr-data-overview-numba')
sys.dont_write_bytecode=True
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager,colors,ticker

OUT=Path(__file__).resolve().parent
PROJECT=next(p for p in OUT.parents if (p/'outputs/research_v2/holdout_run').exists())
RUN=PROJECT/'outputs/research_v2/holdout_run'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cfg=json.loads((RUN/'protocol.json').read_text())
assert cfg['network_ids'][0]==5000
source_hashes=json.loads((RUN/'source_hashes.json').read_text())
for name,digest in source_hashes.items():assert sha(RUN/'source_snapshot'/name)==digest
assert sha(RUN/'protocol.json')==(RUN/'protocol.sha256').read_text().strip()
source=RUN/'source_snapshot/models.py'
spec=importlib.util.spec_from_file_location('frozen_overview_models',source)
model_module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=model_module;spec.loader.exec_module(model_module)
cond=next(c for c in cfg['conditions']if c['name']=='broad')
case=model_module.public_case(5000,cfg,cond);m=case['model']
theta=model_module.generate_truth(case,cfg,cond,0)
designs=json.loads((RUN/'designs.json').read_text())
d=next(d for d in designs if d['network_id']==5000 and d['condition']=='broad' and d['pool']=='exclude_endpoints'
       and d['budget']==3 and d['method']=='local_scalar' and d['target']==0)
nodes=sorted(d['nodes'])
with (RUN/'results.csv').open(newline='')as f:
    row=next(r for r in csv.DictReader(f)if r['network_id']=='5000'and r['condition']=='broad'
      and r['pool']=='exclude_endpoints'and r['budget']=='3'and r['method']=='local_scalar'
      and r['truth_id']=='0'and r['noise_id']=='0'and r['target_id']=='0')
assert nodes==list(map(int,row['nodes'].split(';')))
readout=int(case['readouts'][0]);assert readout==int(row['readout'])
train,_=m.simulate(theta,case['train'])
stride=cfg['sample_stride'];sampled=train[:,::stride]
noise=model_module.seeded(cfg['noise_seed']+0,5000,0).normal(size=sampled.shape)
observed=sampled+cfg['noise_sd']*noise
rr,_=m.simulate(theta,case['intervention'])
delta=rr[1,:,readout]-rr[0,:,readout]
q=float(m.dt*np.sum(delta));q_from_api=float(m.responses(theta,case['intervention'])[0][readout])
assert np.isclose(q,float(row['q_true']),rtol=1e-12,atol=1e-16)
assert np.isclose(q,q_from_api,rtol=1e-12,atol=1e-16)
t=np.arange(cfg['steps'])*m.dt;ts=t[::stride]

def csvout(name,fields,rows):
    with (OUT/name).open('w',newline='')as f:
        w=csv.writer(f);w.writerow(fields);w.writerows(rows)
csvout('weights.csv',['postsynaptic_node','presynaptic_node','weight'],
       ([i,j,m.J[i,j]]for i in range(m.N)for j in range(m.N)))
csvout('calibration_observations.csv',['trial','time_model_units','node','latent_rate_au','noise_standard_normal','observed_rate_au'],
       ([k+1,ts[a],n,sampled[k,a,n],noise[k,a,n],observed[k,a,n]]for k in range(2)for a in range(len(ts))for n in nodes))
csvout('heldout_response.csv',['time_model_units','readout_node','stimulated_rate_au','control_rate_au','difference_rate_au','stimulus_input'],
       ([t[a],readout,rr[1,a,readout],rr[0,a,readout],delta[a],case['intervention'][1,a,case['stim']]]for a in range(len(t))))
np.savez_compressed(OUT/'source_arrays.npz',J=m.J,theta=theta,selected_nodes=nodes,readouts=case['readouts'],
    calibration_times=ts,calibration_latent_all=sampled,noise_standard_normal_all=noise,calibration_observed_all=observed,
    heldout_times=t,heldout_rates_all=rr,heldout_delta_readout=delta,q=q)

fontfile=font_manager.findfont('Arial',fallback_to_default=False)
plt.rcParams.update({'font.family':'Arial','font.size':8.5,'axes.labelsize':8.5,'axes.titlesize':9,
 'xtick.labelsize':8,'ytick.labelsize':8,'axes.linewidth':.65,'lines.linewidth':1.,'pdf.fonttype':42,
 'ps.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,
 'mathtext.fontset':'custom','mathtext.rm':'Arial','mathtext.it':'Arial:italic','mathtext.bf':'Arial:bold',
 'savefig.facecolor':'white','figure.facecolor':'white'})
fig=plt.figure(figsize=(180/25.4,80/25.4))
outer=fig.add_gridspec(1,3,width_ratios=[1.02,1.40,1.17],left=.065,right=.987,bottom=.215,top=.85,wspace=.50)
ax=fig.add_subplot(outer[0]);vmax=float(np.max(np.abs(m.J)))
edges=np.arange(m.N+1)-.5
im=ax.pcolormesh(edges,edges,m.J,cmap='RdBu_r',norm=colors.TwoSlopeNorm(0,-vmax,vmax),shading='flat',rasterized=False)
ax.set_aspect('equal')
ax.set_xlabel('Presynaptic node');ax.set_ylabel('Postsynaptic node')
ax.set_xticks([0,3,6,9,11]);ax.set_yticks([0,3,6,9,11])
node_colors=['#0072B2','#D55E00','#009E73']
for n,col in zip(nodes,node_colors):
    ax.plot(11.85,n,marker='<',markersize=4.2,color=col,clip_on=False)
ax.set_xlim(-.5,11.5);ax.set_ylim(11.5,-.5)
ax.set_anchor('N')
# Dedicated colorbar below the heatmap; marks stay in the true weight scale.
pos=ax.get_position();cax=fig.add_axes([pos.x0,pos.y0-.18,pos.width,.025])
cb=fig.colorbar(im,cax=cax,orientation='horizontal',ticks=[-vmax,0,vmax]);cb.outline.set_linewidth(.5)
cb.ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'));cb.ax.tick_params(length=2,pad=2,labelsize=8)
cb.set_label('Connection weight (a.u.)',labelpad=2,fontsize=8)
if cb.solids is not None:cb.solids.set_rasterized(False)

sub=outer[1].subgridspec(3,1,hspace=.16);axes=[]
for j,(n,col)in enumerate(zip(nodes,node_colors)):
    a=fig.add_subplot(sub[j],sharex=axes[0]if axes else None);axes.append(a)
    for k in range(2):
        # Concatenate trials without drawing across their boundary.
        xx=ts+k*cfg['steps']*m.dt
        a.plot(xx,observed[k,:,n],'-o',color=col,markersize=2.1,markeredgewidth=0,linewidth=.7)
    a.axvline(6,color='#B5BAC1',linewidth=.6,linestyle=(0,(2,2)))
    a.set_ylabel(f'N{n}',rotation=0,ha='right',va='center',labelpad=7,color=col,fontweight='bold')
    a.yaxis.set_major_locator(ticker.MaxNLocator(nbins=2));a.tick_params(length=2.5,pad=2)
    a.set_xlim(-.15,11.95)
    if j<2:a.tick_params(labelbottom=False)
    else:a.set_xticks([0,3,6,9,12]);a.set_xlabel('Calibration time (model units)',labelpad=3)
axes[0].text(.25,1.12,'Trial 1',transform=axes[0].transAxes,ha='center',fontsize=8,color='#4B5563')
axes[0].text(.75,1.12,'Trial 2',transform=axes[0].transAxes,ha='center',fontsize=8,color='#4B5563')

ac=fig.add_subplot(outer[2]);ac.axvspan(1,2,color='#E9EDF1',zorder=0)
ac.axhline(0,color='#AAB0B8',linewidth=.6)
scaled=delta*1e4
ac.fill_between(t,0,scaled,color='#496579',alpha=.16,linewidth=0)
ac.plot(t,scaled,color='#263F52',linewidth=1.15)
ac.set_xlabel('Held-out time (model units)');ac.set_ylabel(rf'Rate difference at N{readout} ($10^{{-4}}$ a.u.)',labelpad=4)
ac.set_xlim(0,6);ac.set_xticks([0,2,4,6]);ac.yaxis.set_major_locator(ticker.MaxNLocator(nbins=4))
ac.tick_params(length=3,pad=3)
ac.text(.04,.97,f'q = {q:.3e}\na.u. × model time',ha='left',va='top',transform=ac.transAxes,fontsize=8)

for letter,title,x in [('A','Known connectivity',outer[0].get_position(fig).x0),('B','Recorded rates (a.u.)',outer[1].get_position(fig).x0),('C','Stimulus response',outer[2].get_position(fig).x0)]:
    fig.text(x,.94,letter,fontsize=10,fontweight='bold',va='top')
    fig.text(x+.026,.94,title,fontsize=9,va='top')
for ext in ['pdf','svg','png']:
    fig.savefig(OUT/f'fig1_data_overview.{ext}',dpi=300,bbox_inches=None)
plt.close(fig)

caption=(f'Figure 1. Actual data from a prespecified illustrative simulated network. '
 f'(A) Signed known connectivity J for network 5000; columns are presynaptic and rows postsynaptic neurons. '
 f'Colored arrowheads mark the recorded rows N{nodes[0]}, N{nodes[1]}, and N{nodes[2]}, matching B. '
 f'(B) Noisy calibration observations at those three neurons in two calibration trials reset to the same known initial state, '
 f'concatenated for display; the dashed line at 6 marks the trial boundary, not continuous evolution across trials. '
 f'Points are the actual observations at stride {stride}, with Gaussian observation noise SD {cfg["noise_sd"]}; '
 f'lines only connect within-trial observations. (C) The teacher response at readout N{readout}: stimulated rate minus '
 f'the matched zero-input control. The shaded interval denotes the fixed input at N{case["stim"]} from model time 1 to 2. '
 f'The displayed q={q:.12g} a.u.×model time is dt times the sum of the frozen-model differences '
 f'(dt={m.dt}; 120 samples on [0,6)), rather than a newly computed trapezoidal integral. '
 f'The readout was not used as a calibration recording. Selection: broad condition, truth draw 0, noise draw 0, '
 f'target 0, exclude_endpoints pool, budget 3, local_scalar policy. This is the first frozen main-study network, '
 f'chosen by index before inspecting its effect. Independent n=1 illustrative network; '
 f'no uncertainty interval or between-method effect is inferred from this figure. All time and rate units are dimensionless model units.\n')
(OUT/'caption.md').write_text(caption)
manifest=dict(selection_rule='fixed first main-study J5000; no effect-based instance selection',
 network_id=5000,condition='broad',truth_id=0,noise_id=0,target_id=0,pool='exclude_endpoints',budget=3,
 method='local_scalar',selected_nodes=nodes,greedy_selection_order=d['nodes'],stim=int(case['stim']),readout=readout,
 independent_n=1,q_rebuilt=q,q_csv=float(row['q_true']),q_abs_difference=abs(q-float(row['q_true'])),
 noise_reconstruction='seeded(noise_seed+noise_id,network_id,truth_id).normal(shape=train[:,::sample_stride].shape)',
 source_snapshot_sha256=source_hashes,source_protocol_sha256=sha(RUN/'protocol.json'),source_designs_sha256=sha(RUN/'designs.json'),
 source_results_sha256=sha(RUN/'results.csv'),font_family='Arial',font_path=fontfile,width_mm=180,height_mm=80,
 display_transformations=['Calibration trials concatenated by adding 6 time units to trial 2, with no connecting segment across boundary',
 'Response panel rate differences multiplied by 1e4, explicitly labelled; q remains in original units',
 'Connectivity colormap uses symmetric limits around exact zero; no weight changes'],
 reconstruction_limit='Teacher/noise values reconstructed deterministically; no MAP refit, no biological data, n=1 illustrative case',
 matplotlib_version=matplotlib.__version__,numpy_version=np.__version__)
manifest['output_sha256']={p.name:sha(p)for p in OUT.iterdir()if p.is_file()and p.name!='manifest.json'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:manifest[k]for k in ['selected_nodes','stim','readout','q_rebuilt','q_csv','q_abs_difference','font_path','width_mm','height_mm']},indent=2))
