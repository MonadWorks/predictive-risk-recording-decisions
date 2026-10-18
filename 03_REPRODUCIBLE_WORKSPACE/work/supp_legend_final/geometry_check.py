from pathlib import Path
import json,hashlib,sys
import numpy as np
ROOT=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026');src=ROOT/'outputs/pastel_figure_suite/render_supplements.py'
phase=sys.argv[1];code=(ROOT/'work/supp_legend_final/before/render_supplements.py').read_text() if phase=='before' else src.read_text()
ns={'__file__':str(src),'__name__':'geometry_audit'};exec(compile(code,str(src),'exec'),ns)
records={}
def export(fig,stem,svg=True):
 data=[]
 for ax in fig.axes[1:]:
  data.append({'xlim':list(ax.get_xlim()),'ylim':list(ax.get_ylim()),'scales':[ax.get_xscale(),ax.get_yscale()],'points':[np.asarray(c.get_offsets()).tolist() for c in ax.collections],'lines':[{'x':np.asarray(l.get_xdata()).tolist(),'y':np.asarray(l.get_ydata()).tolist()} for l in ax.lines]})
 records[Path(stem).name]=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest();ns['plt'].close(fig)
ns['export']=export
metrics=ns['rows']('holdout_network_metrics.csv');summ=json.loads((ns['DATA']/'holdout_summary.json').read_text())['metric_summaries']
for n,(cond,hdr) in zip((2,3,4),[('matched','Matched uncertainty'),('broad','Broad uncertainty'),('bias_shift','Hidden bias shift')]):ns['figS_strata'](cond,hdr,n,metrics,summ)
(ROOT/f'work/supp_legend_final/geometry_{phase}.json').write_text(json.dumps(records,indent=2)+'\n')
if phase=='after':assert records==json.loads((ROOT/'work/supp_legend_final/geometry_before.json').read_text()),'Data geometry changed'
print(phase,records)
