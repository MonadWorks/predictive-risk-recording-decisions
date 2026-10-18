from pathlib import Path
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pypdf import PdfReader,PdfWriter,Transformation
R=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026');O=R/'outputs/figure_revision_v6';OLD=R/'work/evidence/ICBR2026_v4_pack/03_figures'
items=[('Recording decisions',OLD/'fig2_recording_decisions_v5.pdf',O/'recording_decisions_revised.pdf',110),('Risk forecast layout',OLD/'fig3_risk_forecasts_v5.pdf',O/'risk_forecast_layout_study.pdf',100)]
w=PdfWriter()
def embed(page,path,x,y,width):
 p=PdfReader(path).pages[0];scale=width/float(p.mediabox.width);page.merge_transformed_page(p,Transformation().scale(scale).translate(x,y))
for title,old,new,h in items:
 b=BytesIO();c=canvas.Canvas(b,pagesize=(420*mm,297*mm));c.setFont('Helvetica',12);c.drawString(20*mm,281*mm,title+' | same physical width')
 for x,label in [(20,'Claude v5 baseline'),(220,'Local revision / study')]:c.setFont('Helvetica',10);c.drawString(x*mm,265*mm,label)
 c.setFont('Helvetica',9);c.drawString(20*mm,119*mm,'60% scale checks (108 mm wide)');c.showPage();c.save();p=PdfReader(b).pages[0]
 embed(p,old,20*mm,143*mm,180*mm);embed(p,new,220*mm,143*mm,180*mm)
 embed(p,old,20*mm,37*mm,108*mm);embed(p,new,220*mm,37*mm,108*mm)
 w.add_page(p)
with (O/'before_after_comparison.pdf').open('wb') as f:w.write(f)
# Actual manuscript working text block is 158 mm, not 180 mm.
w=PdfWriter()
captions=[
 ['Recording decisions and response error in simulated networks.','a, Each dot is one design: 120 single-response designs (3 per network) and 40 shared','designs (1 per network). Grey denotes the same recording set under both criteria.','b, Each coloured mark is a network-level MSE ratio; vertical jitter separates marks','and has no scientific units. Open markers aggregate exact zero ratios (13/40, 26/40).','c, Relative effect = 100 x (mean ensemble MSE / mean nominal MSE - 1), not the mean','of network percentage changes. Prespecified paired network-cluster 97.5% intervals','include zero. Known connectivity; N = 12; recording budget = 3; endpoints excluded.'],
 ['Risk forecasts for fixed predictions in 40 new simulated networks.','a, Each connected pair shares the same network and observed response MSE; only the','risk forecast changes. Ensemble denotes prior-averaged local risk. The identity line','is descriptive and does not test calibration. b, Network means of case scores','S(v,e) = log(v) + e^2/v; lower scores are better. Differences are ensemble minus nominal.','All 40 values are retained; the -11.67 bar is clipped at -3.4 and marked explicitly.','That network contributes about 64% of the SIGNED total difference (-18.23), not of','the absolute differences. c, Frozen mean difference and paired network-cluster 95%','interval; it includes zero. Shown values are rounded; exact source values are unchanged.']]
for (title,old,new,h),cap in zip(items,captions):
 b=BytesIO();c=canvas.Canvas(b,pagesize=(210*mm,297*mm));c.setFont('Helvetica',10);c.drawString(26*mm,280*mm,'Manuscript-size proof | figure width 158 mm')
 y=250*mm-(h*158/180)*mm
 c.setFont('Helvetica-Bold',9);c.drawString(26*mm,y-10*mm,cap[0]);c.setFont('Helvetica',8)
 for i,line in enumerate(cap[1:]):c.drawString(26*mm,y-(16+i*4)*mm,line)
 c.showPage();c.save();p=PdfReader(b).pages[0];embed(p,new,26*mm,y,158*mm);w.add_page(p)
with (O/'manuscript_size_proof.pdf').open('wb') as f:w.write(f)
print('Vector comparison and manuscript-size proof exported.')
