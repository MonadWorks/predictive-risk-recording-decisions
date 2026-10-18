from pathlib import Path
import json,subprocess
from PIL import Image
import numpy as np
R=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026');O=R/'outputs/pastel_figure_suite'
inv=json.loads((O/'figure_inventory.json').read_text());records=[]
legacy_rgb={'old_blue':[42,59,204],'old_orange':[220,79,30],'old_teal_line':[79,143,131],'old_teal_fill':[133,189,178],'old_teal_deep':[95,150,158],'old_mulberry':[135,56,95],'old_rose_deep':[183,62,112],'old_amber':[216,148,48]}
new_rgb={'pastel_rose':[226,122,158],'sunflower_amber':[237,175,38],'sunflower_amber_line':[219,154,29]}
for r in inv:
 p=O/r['stem'];fr=subprocess.run(['pdffonts',str(p.with_suffix('.pdf'))],capture_output=True,text=True,check=True)
 lines=fr.stdout.splitlines()[2:]
 assert all(' yes ' in line for line in lines),r['title']
 fonts=' '.join(line.split()[0] for line in lines)
 assert 'BentonSans' in fonts,r['title']
 a=np.array(Image.open(p.with_suffix('.png')).convert('RGB'))
 legacy={h:int(np.all(a==v,axis=2).sum()) for h,v in legacy_rgb.items()}
 assert all(n==0 for n in legacy.values()),(r['title'],legacy)
 present={h:int(np.all(a==v,axis=2).sum()) for h,v in new_rgb.items()}
 records.append({'figure':r['title'],'fonts':fonts,'legacy_exact_color_pixels':legacy,'new_palette_pixels':present})
# Figures that must carry each new data colour at least once.
by={r['figure']:r['new_palette_pixels'] for r in records}
assert by['Fig. 2 | Connectivity, recordings and response']['pastel_rose']>0
assert by['Fig. 2 | Connectivity, recordings and response']['sunflower_amber']>0
assert by['Fig. 4 | Risk forecasts on fixed predictions']['sunflower_amber']>0
assert by['Fig. 3 | Recording decisions and response error']['pastel_rose']>0
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
(O/'suite_verification.json').write_text(json.dumps({'figures':records,'copied_source_data':source,'graphical_abstract_unchanged':gas,'limits':'File/font/geometry and inherited numeric checks do not certify aesthetic superiority or scientific novelty. Colour checks are exact-value pixel counts, not gamut or perceptual proofs.'},indent=2))
print('10 figure PDFs: BentonSans embedded, legacy teal/blue/orange/mulberry pixels absent, new rose+amber present, frozen tables and GA unchanged.')
