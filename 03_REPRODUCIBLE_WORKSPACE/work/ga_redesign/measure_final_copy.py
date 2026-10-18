exec(open('work/ga_redesign/measure_copy.py').read().split('variants=')[0])
lines=['We compare single-response and shared designs under nominal and prior-averaged risk, using a common budget and MAP fit.','Identical recording sets and data then yield identical predictions; we test risk forecasts separately on fixed predictions.','Primary error and score intervals include zero. An exploratory extension used 8 independent 100-unit rank-two networks;','4/8 setting-specific intervals exclude zero (unadjusted), all favouring prior averaging; one point estimate favours nominal.']
for i,line in enumerate(lines):
 t=a.text(0,0,line,fontsize=8.2,fontfamily='BentonSans',fontweight='bold' if i==1 else 'normal');w=t.get_window_extent(r).width/a.bbox.width*190;print(i+1,round(w,2),line)
