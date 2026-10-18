"""Check frozen scientific claims and rendered geometry; no new estimation."""
from pathlib import Path
import csv,json,hashlib,subprocess,shutil
ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/'rendered';DATA=ROOT/'baseline/05_data_and_code/source_data'
def rows(name):return list(csv.DictReader((DATA/name).open()))
def check(test,description):
 if not test:raise AssertionError(description)
a=rows('holdout_design_agreement.csv')
counts={}
for objective,total,same in [('single_response',120,82),('three_responses',40,26)]:
 chosen=[r for r in a if r['objective']==objective];n=sum(r['identical']=='True' for r in chosen)
 check((len(chosen),n)==(total,same),'recording agreement')
 counts[objective]={'identical':n,'total':len(chosen)}
effects=[r for r in rows('holdout_paired_effects.csv') if r['primary']=='True' and r['metric']=='mse']
check(len(effects)==2,'two primary error comparisons')
for r in effects:check(float(r['ci_low'])<=0<=float(r['ci_high']),'primary error CI contains zero')
f=json.loads((DATA/'forecast_summary.json').read_text())['primary'];nets=rows('fig3_networks.csv');scores=[float(r['score_difference']) for r in nets]
check(len(nets)==40 and sum(v<0 for v in scores)==19,'forecast counts')
check(float(f['score_difference_ci_low'])<=0<=float(f['score_difference_ci_high']),'forecast-score CI contains zero')
share=min(scores)/sum(scores);check(round(100*share)==64,'single-network summed-score share')
check(abs(sum(scores)/40-f['score_difference'])<1e-10,'reported mean score')
ext=[r for r in rows('n100_paired_effects.csv') if r['metric']=='mse' and r['contrast'] in ['ensemble_scalar - local_scalar','ensemble_vector - local_vector']]
exclude=[r for r in ext if float(r['ci_low'])*float(r['ci_high'])>0]
check(len(ext)==8 and len(exclude)==4 and all(float(r['ci_high'])<0 for r in exclude),'exploratory 4 of 8 negative intervals')
check(all(int(r['networks'])==8 for r in ext) and sum(float(r['effect'])>0 for r in ext)==1,'extension sample size and reversal')
man=json.loads((ROOT/'baseline/05_data_and_code/fig1_data/manifest.json').read_text());check(man['budget']==3 and len(man['selected_nodes'])==3,'recording budget')
layout=json.loads((OUT/'current_audit.json').read_text());check(not layout['text_overlaps'],'no detected text overlaps');dy=layout['optical_grid'].get('body_translation_y',0)
for t in layout['texts']:
 (x,y),(xx,yy)=t['bbox'];check(0<=x and xx<=190 and 12.7<=y and yy<=135,'canvas text bounds')
 if 39+dy<y<107+dy and x>56:
  left=56.5+42*int((x-56.5)//42);check(left<=x and xx<=left+40 and 37.5+dy<=y and yy<=109.5+dy,'panel text bounds')
for l in layout['statistical_lines']:check(min(l['y'])>=min(l['ylim']) and max(l['y'])<=max(l['ylim']),'statistical marks not clipped')
xs=[v for l in layout['statistical_lines'] for v in l['x']]
expected=[100*float(r[k]) for r in effects for k in ['relative_mse_difference','relative_mse_ci_low','relative_mse_ci_high']]+[f[k] for k in ['score_difference','score_difference_ci_low','score_difference_ci_high']]
for v in expected:check(any(abs(v-x)<1e-10 for x in xs),'plotted statistical x coordinates match frozen data')
grid=layout['optical_grid']
for r in grid['equal_group_spacing'].values():
 if 'mode' not in r:check(max(r['actual_gaps'])-min(r['actual_gaps'])<1e-6,'equal within-panel group gaps')
check(.8<grid['score_inner_gaps'][0]<1.1,'score equation to symbol explanation clearance')
gaps=grid['axis_baseline_to_title_top_source_units'];check(max(gaps)-min(gaps)<1e-6,'equal axis-title gaps');check(all(abs(v-7.4)<1e-6 for v in gaps),'final axis-title clearance')
for k in ['number_description_to_dot_gap','percent_to_dot_gap']:
 check(max(grid[k])-min(grid[k])<1e-6,'equal statistic-to-dot clearance')
footer=[t for t in layout['texts'] if t['bbox'][0][0]>=56.5 and t['bbox'][0][1]<34.8+dy]
check(len(set(round(t['bbox'][0][1],5) for t in footer))==4,'footer has four text rows')
for t in footer:check(t['bbox'][0][0]>=59 and t['bbox'][1][0]<=178.3 and t['bbox'][0][1]>=17.2+dy and t['bbox'][1][1]<=34.8+dy,'footer inner bounds')
check('<image' not in (OUT/'graphical_abstract_current.svg').read_text(),'vector-only SVG')
font_check='not run: pdffonts unavailable'
if shutil.which('pdffonts'):
 font_check=subprocess.check_output(['pdffonts',str(OUT/'graphical_abstract_current.pdf')],text=True)
 check('Arial' not in font_check,'no Arial')
 for line in font_check.splitlines()[2:]:check(line.split()[-5:-2]==['yes','yes','yes'],'fonts embedded')
 (OUT/'pdf_fonts.txt').write_text(font_check)
facts={'status':'PASS','recording_agreement':counts,'response_error_primary':effects,'forecast_primary':f,'forecast_count_favour_prior_averaging':19,'forecast_networks':40,'single_network_fraction_of_summed_score_difference':share,'extension':{'networks':8,'settings':8,'intervals_excluding_zero':4,'all_exclusions_favour_prior_averaging':True,'positive_point_estimates':1,'exploratory':True,'intervals_unadjusted':True},'wording_review':'Primary error and forecast-score intervals include zero is a precise reference to the three primary confidence intervals; recording-agreement counts are descriptive. Known connectivity is simulated, not a claim of biological validation. q is integrated stimulated-minus-control response.','not_submitted':True}
(OUT/'semantic_fact_audit.json').write_text(json.dumps(facts,indent=2)+'\n')
files={}
for ext in ['pdf','png','svg']:
 p=OUT/f'graphical_abstract_current.{ext}';files[p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(OUT/'verification.json').write_text(json.dumps({'status':'PASS','files':files,'optical_grid':grid,'fonts_checked':shutil.which('pdffonts') is not None,'visual_review':'Root archive was reviewed from a Poppler-rendered PDF. New rerenders require visual review after changes.','scope':'Frozen-data consistency and presentation checks; not independent scientific replication or biological validation.'},indent=2)+'\n')
print('PASS: frozen facts, statistical x coordinates, text bounds, equal gaps, unclipped marks, vector SVG, available font checks.')
