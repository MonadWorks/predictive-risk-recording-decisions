from pathlib import Path
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader,PdfWriter,Transformation
from PIL import Image,ImageDraw,ImageFont
import json,re
R=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026');O=R/'outputs/pastel_figure_suite'
BENTON=str(O/'fonts/benton-sans-regular.ttf');BENTON_B=str(O/'fonts/benton-sans-bold.ttf')
pdfmetrics.registerFont(TTFont('BentonSans',BENTON));pdfmetrics.registerFont(TTFont('BentonSans-Bold',BENTON_B))
items=[('Fig. 1 | Three-layer audit','fig1_audit'),('Fig. 2 | Connectivity, recordings and response','fig2_data_overview'),('Fig. 3 | Recording decisions and response error','fig3_recording_decisions'),('Fig. 4 | Risk forecasts on fixed predictions','fig4_risk_forecasts'),('Fig. 5 | Exploratory model-family extension','fig5_extension'),('Fig. S1 | Paired distributions','supplementary/figS1_complete_paired_distributions_pastel'),('Fig. S2 | Matched uncertainty','supplementary/figS2_matched_conditions_pastel'),('Fig. S3 | Broad uncertainty','supplementary/figS3_broad_conditions_pastel'),('Fig. S4 | Bias-shift uncertainty','supplementary/figS4_bias_shift_conditions_pastel'),('Fig. S5 | Linear positive control','supplementary/figS5_linear_positive_control_pastel')]
w=PdfWriter();inventory=[]
for title,stem in items:
 p=PdfReader(O/f'{stem}.pdf').pages[0];width,height=float(p.mediabox.width),float(p.mediabox.height)
 b=BytesIO();c=canvas.Canvas(b,pagesize=(210*mm,297*mm));c.setFont('BentonSans',9);c.setFillColorRGB(.18,.15,.19);c.drawString(15*mm,282*mm,title);c.setFont('BentonSans',6);c.setFillColorRGB(.49,.45,.50);c.drawString(15*mm,12*mm,'2026-10-18 | Pastel rose and sunflower suite | Original data retained | Graphical abstract excluded');c.showPage();c.save()
 page=PdfReader(b).pages[0];page.merge_transformed_page(p,Transformation().translate(15*mm,270*mm-height));w.add_page(page);w.add_outline_item(title,len(w.pages)-1)
 inventory.append({'title':title,'stem':stem,'width_mm':width/mm,'height_mm':height/mm})
with (O/'all_figures_pastel.pdf').open('wb') as f:w.write(f)
# Thumbnail overview is for navigation, not inspection of text.
font=ImageFont.truetype(BENTON,22)
gallery=Image.new('RGB',(1500,2350),'white');draw=ImageDraw.Draw(gallery)
for k,(title,stem) in enumerate(items):
 x=(k%2)*750;y=(k//2)*470
 draw.text((x+20,y+12),title,font=font,fill='#2E2531')
 im=Image.open(O/f'{stem}.png').convert('RGB');im.thumbnail((710,410));gallery.paste(im,(x+20+(710-im.width)//2,y+50))
gallery.save(O/'all_figures_overview.png')
(O/'figure_inventory.json').write_text(json.dumps(inventory,indent=2))
print('Updated figure atlas without regenerating manuscript text.')
