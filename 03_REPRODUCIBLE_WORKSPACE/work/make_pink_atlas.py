from pathlib import Path
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader,PdfWriter,Transformation
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,re,shutil
R=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026'); O=R/'outputs/pink_figure_suite'
pdfmetrics.registerFont(TTFont('Arial','/System/Library/Fonts/Supplemental/Arial.ttf'))
items=[('Fig. 1 | Three-layer audit','fig1_audit'),('Fig. 2 | Connectivity, recordings and response','fig2_data_overview'),('Fig. 3 | Recording decisions and response error','fig3_recording_decisions'),('Fig. 4 | Risk forecasts on fixed predictions','fig4_risk_forecasts'),('Fig. 5 | Exploratory model-family extension','fig5_extension'),('Fig. S1 | Paired distributions','supplementary/figS1_complete_paired_distributions_pink'),('Fig. S2 | Matched uncertainty','supplementary/figS2_matched_conditions_pink'),('Fig. S3 | Broad uncertainty','supplementary/figS3_broad_conditions_pink'),('Fig. S4 | Bias-shift uncertainty','supplementary/figS4_bias_shift_conditions_pink'),('Fig. S5 | Linear positive control','supplementary/figS5_linear_positive_control_pink')]
w=PdfWriter();inventory=[]
for title,stem in items:
 p=PdfReader(O/f'{stem}.pdf').pages[0];width,height=float(p.mediabox.width),float(p.mediabox.height)
 b=BytesIO();c=canvas.Canvas(b,pagesize=(210*mm,297*mm));c.setFont('Arial',9);c.setFillColorRGB(.15,.13,.16);c.drawString(15*mm,282*mm,title);c.setFont('Arial',6);c.setFillColorRGB(.46,.43,.47);c.drawString(15*mm,12*mm,'2026-10-18 | Pink figure suite | Original data retained | Graphical abstract excluded');c.showPage();c.save()
 page=PdfReader(b).pages[0];page.merge_transformed_page(p,Transformation().translate(15*mm,270*mm-height));w.add_page(page);w.add_outline_item(title,len(w.pages)-1)
 inventory.append({'title':title,'stem':stem,'width_mm':width/mm,'height_mm':height/mm})
with (O/'all_figures_pink.pdf').open('wb') as f:w.write(f)
# Thumbnail overview is for navigation, not inspection of text.
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
gallery=Image.new('RGB',(1500,2350),'white');draw=ImageDraw.Draw(gallery)
for k,(title,stem) in enumerate(items):
 x=(k%2)*750;y=(k//2)*470
 draw.text((x+20,y+12),title,font=font,fill='#27232B')
 im=Image.open(O/f'{stem}.png').convert('RGB');im.thumbnail((710,410));gallery.paste(im,(x+20+(710-im.width)//2,y+50))
gallery.save(O/'all_figures_overview.png')
# Manuscript copy: source data and claims untouched; links and changed visual captions synchronized.
s=(R/'work/evidence/ICBR2026_v4_pack/02_paper/paper_v4.md').read_text()
old=['fig_audit_schematic_v5','fig1_data_overview_v4','fig2_recording_decisions_v5','fig3_risk_forecasts_v5','fig4_model_extension_v4']
for a,(_,b) in zip(old,items[:5]):s=s.replace('../03_figures/'+a+'.png','./'+b+'.png')
for _,b in items[5:]:
 oldname=Path(b).name.replace('_pink','_v4')
 s=s.replace('../03_figures/supplementary_v4/'+oldname+'.png','./'+b+'.png')
s=s.replace('blue positive, orange negative weights','rose positive, dark grey-purple negative weights')
s=s.replace('open vermilion marker','open light-rose marker').replace('open plum marker','open mulberry marker')
s=s.replace('ensemble forecast (purple)','ensemble forecast (mulberry)')
s=s.replace('Panels b and c use different horizontal and vertical scales because individual differences and uncertainty about their mean are distinct statistical objects.','Panels b and c use different horizontal scales because individual differences and uncertainty about their mean are distinct statistical objects.')
s=s.replace('Step 1 asks','Panel a asks').replace('Step 2 compares','Panel b compares').replace('Step 3 fixes','Panel c fixes')
(O/'paper_with_pink_figures.md').write_text(s)
# Verify ten embedded links resolve.
refs=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',s);assert len(refs)==10
assert all((O/p).is_file() for p in refs)
(O/'figure_inventory.json').write_text(json.dumps(inventory,indent=2))
print('10 figures; vector atlas; overview; manuscript-link copy verified.')
