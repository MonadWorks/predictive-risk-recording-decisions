from pathlib import Path
import importlib.util,json
p=Path('work/evidence/ICBR2026_v4_pack/03_figures/style/palette_check.py');s=importlib.util.spec_from_file_location('palette',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
colors={'single_response':'#B73E70','shared_response':'#D99AB3','forecast':'#87385F','neutral':'#C9C5C8','negative_weight':'#413A43'}
r={}
for k,v in colors.items():
 a=m.rgb(v);r[k]={'hex':v,'contrast_white':m.contrast(a,m.rgb('#FFFFFF')),'Lstar':float(m.lab(a)[0])}
pairs={}
for a,b in [('single_response','shared_response'),('shared_response','neutral'),('negative_weight','single_response')]:
 x,y=m.rgb(colors[a]),m.rgb(colors[b]);pairs[a+' vs '+b]={'normal_deltaE76':m.dE(x,y),'simulated_deltaE76':{v:m.dE(m.sim(x,v),m.sim(y,v)) for v in m.M}}
Path('outputs/pink_figure_suite/palette_checks.json').write_text(json.dumps({'colors':r,'pairs':pairs,'interpretation':'Descriptive metrics, not universal pass thresholds. Light marks need shape/outline/labels; all text remains dark.'},indent=2))
print(json.dumps(pairs,indent=2))
