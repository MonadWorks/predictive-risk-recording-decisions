from PIL import Image
import numpy as np,json
from pathlib import Path
im=np.array(Image.open('outputs/graphical_abstract_redesign/graphical_abstract_current.png').convert('RGB'));sx=im.shape[1]/190;sy=185/25.4*300/135
res=[]
for label,y in [('Recorded node',52.5),('Stimulated node',48.1),('Response readout',43.7)]:
 row=(135-y)*sy;top=int(row-2*sy);bottom=int(row+2*sy)
 mark=im[top:bottom,int(7.7*sx):int(10.9*sx)];txt=im[top:bottom,int(12.3*sx):int(47*sx)]
 my=np.where((mark.min(axis=2)<200).any(axis=1))[0];ty=np.where((txt.max(axis=2)<140).any(axis=1))[0]
 assert len(my) and len(ty)
 mc=(my.min()+my.max())/2;tc=(ty.min()+ty.max())/2
 res.append({'label':label,'circle_ink_center_px':float(top+mc),'text_ink_center_px':float(top+tc),'difference_px':float(tc-mc)})
print(json.dumps(res,indent=2));Path('work/ga_redesign/legend_pixel_audit.json').write_text(json.dumps(res,indent=2)+'\n')
