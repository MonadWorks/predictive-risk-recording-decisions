exec(open('work/ga_redesign/measure_copy.py').read().split('variants=')[0])
paras=[
'We cross response objectives with nominal and prior-averaged risk under a common budget and MAP fit. Identical recording sets and data then yield identical predictions; forecasts are tested separately on fixed predictions.',
'Primary error and forecast-score intervals include zero. In the exploratory 100-unit extension (8 independent networks), 4/8 unadjusted intervals exclude zero, all favouring prior averaging; one point estimate favours nominal.'
]
for para in paras:
 lines=[];line=''
 for word in para.split():
  test=(line+' '+word).strip();t=a.text(0,0,test,fontsize=8.2,fontfamily='BentonSans');w=t.get_window_extent(r).width/a.bbox.width*190;t.remove()
  if w>118.8:lines.append(line);line=word
  else:line=test
 lines.append(line);print(len(lines),lines)
