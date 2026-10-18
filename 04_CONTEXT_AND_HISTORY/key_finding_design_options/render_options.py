from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.figure
from matplotlib.text import Text
from matplotlib.patches import FancyBboxPatch
from matplotlib.transforms import Bbox
R=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026')
SRC=R/'outputs/graphical_abstract/source/render_graphical_abstract.py';O=Path(__file__).resolve().parent
KEY='Better risk estimates do not necessarily make better recording decisions.'
original=matplotlib.figure.Figure.savefig
for mode in ['B']:
 done=[False]
 def save(fig,fname,*args,**kw):
  if done[0]:return
  done[0]=True
  base=fig.axes[0]
  if mode=='A':
   base.text(8,10.5,KEY,fontfamily='BentonSans',fontsize=11.5,fontweight='bold',color='#984775',va='center')
   crop=Bbox.from_extents(0,(4/135)*(185/25.4),260/25.4,185/25.4)
  elif mode=='B':
   for p in base.patches:
    if isinstance(p,FancyBboxPatch) and p.get_y()<40 and p.get_height()<30:
     p.set_y(p.get_y()-6.7);p.set_height(p.get_height()+6.7)
   left=[];right=[]
   for t in base.texts:
    x,y=t.get_position()
    if t.get_transform() is not base.transData or y>=40:continue
    if x<55:
     left.append(t)
     if t.get_text()=='Integrated stimulus response':
      t.set_fontweight('bold');t.set_fontsize(9.0);t.set_position((12.0,31.1));t.set_ha('left')
     elif t.get_text().startswith('$q='):t.set_y(24.9);t.set_fontsize(14.0)
     else:t.set_y(18.9);t.set_fontsize(11.2)
    elif x>58:
     right.append(t)
     v=t.get_text()
     if v.startswith('Primary error'):t.set_y(25.2)
     elif v.startswith('Exploratory 100-unit'):t.set_y(20.7)
     elif v.startswith('All four'):t.set_y(17.5)
     else:t.set_y(28.4)
   key=base.text(59,32.9,KEY,fontfamily='BentonSans',fontsize=9.3,fontweight='bold',color='#984775',va='center')
   right.append(key)
   # Optical centering uses realised ink bounds, including math ascenders/descenders.
   fig.canvas.draw();rr=fig.canvas.get_renderer()
   # Repack coloured math segments after font enlargement.
   parts=[t for t in left if t.get_text().startswith(('$\\Delta', '$r_', '$-r_'))]
   widths=[t.get_window_extent(rr).width/base.bbox.width*190 for t in parts]
   cursor=30.25-sum(widths)/2
   for t,w in zip(parts,widths):t.set_x(cursor);cursor+=w
   fig.canvas.draw();rr=fig.canvas.get_renderer()
   import json
   audit={}
   for group,label in [(left,'formula'),(right,'explanation')]:
    boxes=[t.get_window_extent(rr) for t in group]
    low=min(b.y0 for b in boxes);high=max(b.y1 for b in boxes)
    low,high=base.transData.inverted().transform([[0,low],[0,high]])[:,1]
    frame=next(p for p in base.patches if isinstance(p,FancyBboxPatch) and p.get_y()<20 and ((p.get_x()<55)==(label=='formula')))
    center=frame.get_y()+frame.get_height()/2
    shift=center-(low+high)/2
    for t in group:t.set_y(t.get_position()[1]+shift)
    audit[label]={'top_padding':frame.get_y()+frame.get_height()-(high+shift),'bottom_padding':low+shift-frame.get_y(),'body_line_pitch':3.2 if label=='explanation' else None,'paragraph_pitch':4.5 if label=='explanation' else None}
   # Shared heading baseline; match the lower ink padding while spacing math optically.
   heading=next(t for t in left if t.get_text()=='Integrated stimulus response')
   integral=next(t for t in left if t.get_text().startswith('$q='))
   heading.set_position((30.25,key.get_position()[1]));heading.set_ha('center')
   fig.canvas.draw();rr=fig.canvas.get_renderer()
   def bounds(group):
    bb=[t.get_window_extent(rr) for t in group]
    return base.transData.inverted().transform([[0,min(b.y0 for b in bb)],[0,max(b.y1 for b in bb)]])[:,1]
   frame=next(p for p in base.patches if isinstance(p,FancyBboxPatch) and p.get_y()<20 and p.get_x()<55)
   # Make the two equations one group: 2.0 units of clear ink space.
   ilow,ihigh=bounds([integral]);dlow,dhigh=bounds(parts)
   dy=ilow-1.2-dhigh
   for t in parts:t.set_y(t.get_position()[1]+dy)
   fig.canvas.draw();rr=fig.canvas.get_renderer()
   hlow,_=bounds([heading]);fl,fh=bounds([integral]+parts)
   # Heading-to-equation clearance is 1.5 times the inter-equation clearance.
   dy=hlow-4.2-fh
   for t in [integral]+parts:t.set_y(t.get_position()[1]+dy)
   fig.canvas.draw();rr=fig.canvas.get_renderer()
   lo,hi=bounds(left)
   audit['formula'].update(top_padding=frame.get_y()+frame.get_height()-hi,bottom_padding=lo-frame.get_y(),heading_baseline_aligned=True,title_alignment='center',title_pt=9,integral_pt=14,definition_pt=11.2,formula_ink_gap=1.2,title_to_formula_ink_gap=4.2)
   (O/'B_spacing_audit.json').write_text(json.dumps(audit,indent=2))
   crop=Bbox.from_extents(0,(7.25/135)*(185/25.4),260/25.4,185/25.4)
  else:
   for t in base.texts:
    if t.get_text()=='Predictive risk and recording decisions':
     t.set_text('Better risk estimates do not necessarily');t.set_fontsize(17.3)
    if t.get_text()=='in partially observed neural networks':
     t.set_text('make better recording decisions.');t.set_fontsize(17.3);t.set_fontweight('normal')
   crop=kw['bbox_inches']
  fig.canvas.draw();rr=fig.canvas.get_renderer()
  texts=[]
  for t in fig.findobj(Text):
   if t.get_visible() and t.get_text().strip():
    b=t.get_window_extent(rr);texts.append({'text':t.get_text(),'bounds':b.bounds})
  import json
  (O/f'{mode}_text_bounds.json').write_text(json.dumps(texts,indent=2))
  for ext in ['png','pdf','svg']:
   opts=dict(kw);opts['bbox_inches']=crop
   original(fig,O/f'option_{mode}.{ext}',*args,**opts)
 matplotlib.figure.Figure.savefig=save
 source=SRC.read_text().replace("OUT=ROOT.parent/'rendered'","OUT=Path("+repr(str(O/'work'))+")")
 exec(compile(source,str(SRC),'exec'),{'__file__':str(SRC),'__name__':'__main__'})
matplotlib.figure.Figure.savefig=original
