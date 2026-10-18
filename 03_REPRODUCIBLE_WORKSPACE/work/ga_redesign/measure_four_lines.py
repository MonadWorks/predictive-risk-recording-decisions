exec(open('work/ga_redesign/measure_copy.py').read().split('variants=')[0])
lines=['Refining a risk criterion need not improve the prediction made from the selected recordings.','We crossed response objectives with nominal and prior-averaged risk under a common budget and MAP estimator.','This design separates task specialisation from uncertainty handling when comparing recording decisions and response error.','A separate study fixed data and point predictions to test risk forecasts independently of recording selection.']
for i,line in enumerate(lines):
 t=a.text(0,0,line,fontsize=8.2,fontfamily='BentonSans',fontweight='bold' if i==1 else 'normal');w=t.get_window_extent(r).width/a.bbox.width*190;print(i+1,round(w,2),line)
