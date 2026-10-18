from pathlib import Path
import importlib.util,json
p=Path('work/evidence/ICBR2026_v4_pack/03_figures/style/palette_check.py');s=importlib.util.spec_from_file_location('palette',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
colors={'single_response':'#E27A9E','shared_response':'#F4BFD0','forecast_sunflower':'#EDAF26','forecast_sunflower_line':'#DB9A1D','three_response_orange':'#E8A13C','neutral':'#DAD4D8','positive_weight':'#C25E88','negative_weight':'#4E4350'}
r={}
for k,v in colors.items():
 a=m.rgb(v);r[k]={'hex':v,'contrast_white':m.contrast(a,m.rgb('#FFFFFF')),'Lstar':float(m.lab(a)[0])}
pairs={}
for a,b in [('single_response','shared_response'),('shared_response','neutral'),('forecast_sunflower','single_response'),('positive_weight','negative_weight')]:
 x,y=m.rgb(colors[a]),m.rgb(colors[b]);pairs[a+' vs '+b]={'normal_deltaE76':m.dE(x,y),'simulated_deltaE76':{v:m.dE(m.sim(x,v),m.sim(y,v)) for v in m.M}}
Path('outputs/pastel_figure_suite/palette_checks.json').write_text(json.dumps({'colors':r,'pairs':pairs,'interpretation':'Descriptive metrics, not universal pass thresholds. Light pink and neutral remain close under some simulations, so shape/outline distinctions are retained; sunflower amber carries the complementary categorical role; all text remains dark ink.'},indent=2))
print(json.dumps(pairs,indent=2))
