from pathlib import Path
import json,hashlib,shutil,re
ROOT=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026');O=ROOT/'outputs/ICBR2026_研究协作交接_2026-10-18';R=O/'03_REPRODUCIBLE_WORKSPACE'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pdf=ROOT/'outputs/paper_v4_pastel/06_latex/biomed/build/main.pdf'
for name in ['paper_v4_biomed_refined.pdf','paper_v4_biomed.pdf','paper_v4_biomed_build.pdf']:shutil.copy2(pdf,ROOT/'outputs'/name)
for name in ['all_figures_pastel.pdf','all_figures_overview.png']:shutil.copy2(ROOT/'outputs/pastel_figure_suite'/name,ROOT/'outputs/paper_v4_pastel/03_figures'/name)
receipt=json.loads((ROOT/'outputs/supplementary_legend_revision_receipt.json').read_text());receipt.update(paper_pdf_sha256=sha(pdf),footer_row_pitch_mm=2.7,visual_review='Final full PDF pages 19–21 rendered; S2 and S4 full pages and common footer visually reviewed. No cropped legend or overlapping explanations detected.')
(ROOT/'outputs/supplementary_legend_revision_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
# Refresh every previously copied artifact against its own source after the last figure edit.
p=O/'05_AUDIT/copy_provenance.json';prov=json.loads(p.read_text());kept=[]
for row in prov['copied']:
 src=Path(row['source']);dst=O/row['destination']
 if not dst.exists():continue
 if src.is_file() and sha(src)!=sha(dst):shutil.copy2(src,dst)
 row['sha256']=sha(src);row['bytes']=src.stat().st_size;kept.append(row)
prov['copied']=kept
# New receipt and source audit from this last revision.
for src,dst in [(ROOT/'outputs/supplementary_legend_revision_receipt.json',O/'05_AUDIT/supplementary_legend_revision_receipt.json'),(ROOT/'outputs/supplementary_legend_revision.md',O/'05_AUDIT/supplementary_legend_revision.md')]:
 shutil.copy2(src,dst);prov['copied'].append({'source':str(src),'destination':str(dst.relative_to(O)),'sha256':sha(src),'bytes':src.stat().st_size,'role':'last requested supplementary legend revision'})
shutil.copytree(ROOT/'work/supp_legend_final',R/'work/supp_legend_final',dirs_exist_ok=True)
for n in ['geometry_before.json','geometry_after.json']:shutil.copy2(ROOT/'work/supp_legend_final'/n,O/'05_AUDIT'/n)
# Explicit current snapshots; older historical integrity manifests remain untouched.
for folder in [R/'outputs/pastel_figure_suite',R/'outputs/paper_v4_pastel']:
 values={str(f.relative_to(folder)):sha(f) for f in folder.rglob('*') if f.is_file() and f.name!='CURRENT_SHA256SUMS.json'}
 (folder/'CURRENT_SHA256SUMS.json').write_text(json.dumps(values,indent=2)+'\n')
a=json.loads((O/'05_AUDIT/current_alignment.json').read_text());a['current_pdf_matches_editorial_receipt']=False;a['editorial_pdf_receipt_status']='historical: superseded by final supplementary legend revision';a['current_pdf_matches_latest_supplement_revision']=sha(O/'01_READ_CURRENT/paper_current.pdf')==receipt['paper_pdf_sha256'];a['current_pdf_sha256']=sha(O/'01_READ_CURRENT/paper_current.pdf');a['legend_data_geometry_identical']=json.loads((O/'05_AUDIT/geometry_before.json').read_text())==json.loads((O/'05_AUDIT/geometry_after.json').read_text());assert a['current_pdf_matches_latest_supplement_revision'] and a['legend_data_geometry_identical']
(O/'05_AUDIT/current_alignment.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');p.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n')
# Stable workspace navigation; preserve all old timelines and files.
(ROOT/'README.md').write_text('''# ICBR 2026 当前工作区\n\n工作区：/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026。历史原件在 work/evidence，未移动或改写冻结研究。\n\n- 合作者交接入口：outputs/ICBR2026_研究协作交接_2026-10-18/00_START_HERE.md\n- 当前全文：outputs/paper_v4_biomed_refined.pdf（最后更新 S2/S3/S4 图例，22 页）\n- 当前正文：outputs/paper_v4_pastel/02_paper/paper_v4.md\n- 当前图组及源码：outputs/pastel_figure_suite/\n- 当前图形摘要：outputs/graphical_abstract/graphical_abstract.pdf（v4 版式，最后轴标题上移已撤销）\n- 冻结研究：work/evidence/outputs/research_v2/\n- 当前一致性与版本关系：交接入口同目录的 01_研究主线与版本审计.md\n\n旧图组、旧 GA、原始接续审计和导读保留为历史；不可因名字里出现 v5/v6 就判定比当前稿更新。没有投稿或上传。\n''')
(ROOT/'outputs/CURRENT.md').write_text('''# 当前正式入口\n\n论文：paper_v4_biomed_refined.pdf（22 页）\n正文：paper_v4_pastel/02_paper/paper_v4.md\nGA：graphical_abstract/graphical_abstract.pdf\n合作者交接：ICBR2026_研究协作交接_2026-10-18/00_START_HERE.md\n\n本轮 S2/S3/S4 图例修改以 supplementary_legend_revision_receipt.json 为准。旧 editorial_light_pass_receipt.json 的源码哈希仍对应当前正文，PDF 哈希是修改补充图之前的历史快照。\n''')
p=O/'02_重现与代码入口.md';s=p.read_text().replace('依赖主要为 NumPy / Matplotlib；','依赖主要为 NumPy / Matplotlib；合并图册的 work/make_pastel_atlas.py 另需 ReportLab、pypdf、Pillow；');p.write_text(s)
print('Refreshed current paper, figures, source snapshots, provenance and workspace navigation.')
