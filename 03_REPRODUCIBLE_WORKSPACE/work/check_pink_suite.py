from pathlib import Path
import json,subprocess,hashlib
from PIL import Image
import numpy as np
R=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026');O=R/'outputs/pink_figure_suite'
inv=json.loads((O/'figure_inventory.json').read_text());records=[]
for r in inv:
 p=O/r['stem'];fr=subprocess.run(['pdffonts',str(p.with_suffix('.pdf'))],capture_output=True,text=True,check=True)
 assert all(' yes ' in line for line in fr.stdout.splitlines()[2:])
 a=np.array(Image.open(p.with_suffix('.png')).convert('RGB'));legacy={h:int(np.all(a==v,axis=2).sum()) for h,v in {'old_blue':[42,59,204],'old_orange':[220,79,30]}.items()}
 assert all(n==0 for n in legacy.values())
 records.append({'figure':r['title'],'fonts':fr.stdout,'legacy_exact_color_pixels':legacy})
source=[]
for p in (O/'source_data').iterdir():
 q=R/'work/evidence/ICBR2026_v4_pack/05_data_and_code/source_data'/p.name
 source.append({'name':p.name,'same_as_frozen':p.read_bytes()==q.read_bytes()})
assert all(r['same_as_frozen'] for r in source)
gas=[]
base=Path('/Users/dujiayi/Documents/Codex/2026-10-16/ic-1-range-2-3-agent/ICBR2026_v4_pack')
for p in base.rglob('graphical_abstract*'):
 if p.is_file():
  q=R/'work/evidence/ICBR2026_v4_pack'/p.relative_to(base)
  gas.append({'path':str(p.relative_to(base)),'unchanged':p.read_bytes()==q.read_bytes()})
assert all(x['unchanged'] for x in gas)
(O/'suite_verification.json').write_text(json.dumps({'figures':records,'copied_source_data':source,'graphical_abstract_unchanged':gas,'limits':'File/font/geometry and inherited numeric checks do not certify aesthetic superiority or scientific novelty.'},indent=2))
print('10 figure PDFs have embedded fonts; legacy exact blue/orange removed; frozen tables and GA unchanged.')
