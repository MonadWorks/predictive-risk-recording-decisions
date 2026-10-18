from pathlib import Path
import shutil,json
root=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026')
out=root/'outputs/graphical_abstract';src=out/'source';src.mkdir(parents=True,exist_ok=True)
for folder in ['03_figures','05_data_and_code/source_data','05_data_and_code/fig1_data']:
 (src/'baseline'/folder).mkdir(parents=True,exist_ok=True)
base=root/'work/evidence/ICBR2026_v4_pack'
shutil.copy2(base/'03_figures/render_v4.py',src/'baseline/03_figures/render_v4.py')
for folder in ['source_data','fig1_data']:
 shutil.copytree(base/'05_data_and_code'/folder,src/'baseline/05_data_and_code'/folder,dirs_exist_ok=True)
shutil.copytree(root/'outputs/pastel_figure_suite/fonts',src/'fonts',dirs_exist_ok=True)
for name in ['Times New Roman','Times New Roman Italic','Times New Roman Bold']:
 f=Path('/System/Library/Fonts/Supplemental')/(name+'.ttf')
 if f.exists():shutil.copyfile(f,src/'fonts'/f.name)
s=(root/'outputs/graphical_abstract_redesign/render_graphical_abstract.py').read_text()
s=s.replace("ROOT=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026');OUT=ROOT/'outputs/graphical_abstract_redesign'", "ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/'rendered'\nOUT.mkdir(parents=True,exist_ok=True)")
s=s.replace("ROOT/'work/ga_redesign/mpl'", "ROOT/'.cache/mpl'").replace("ROOT/'outputs/pastel_figure_suite/fonts'", "ROOT/'fonts'").replace("ROOT/'work/evidence/ICBR2026_v4_pack/03_figures/render_v4.py'", "ROOT/'baseline/03_figures/render_v4.py'").replace("str(OUT/'optical_grid.py')", "str(ROOT/'optical_grid.py')")
(src/'render_graphical_abstract.py').write_text(s)
shutil.copy2(root/'outputs/graphical_abstract_redesign/optical_grid.py',src/'optical_grid.py')
(out/'README.md').write_text('''# Graphical abstract — archived version 1\n\n2026-10-18，本轮确认版。论文题目：**Predictive Risk and Recording Decisions in Partially Observed Neural Networks**。\n\n- `graphical_abstract.pdf`：正式矢量 PDF。\n- `graphical_abstract.svg`：可编辑矢量资产。\n- `graphical_abstract.png`：300 dpi 预览。\n- `source/render_graphical_abstract.py`：渲染入口。\n- `source/optical_grid.py`：字体、布局、整组间距与对齐规则。\n- `source/baseline/`：保留的 Claude v4 原始绘图代码、冻结数据与网络实例。\n- `source/fonts/`：此次本机渲染使用的字体副本。\n- `semantic_fact_audit.json`、`verification.json`：数值、语义和排版核查。\n- `SHA256SUMS.json`：正式快照与源文件的校验值。\n\n## 后续修改和重渲染\n\n在此目录下运行：\n\n```sh\npython3 -m pip install -r source/requirements.txt\npython3 source/render_graphical_abstract.py\npython3 source/audit_graphical_abstract.py\n```\n\n新渲染输出到 `rendered/`，不会直接覆盖本目录的正式快照。审阅后再决定是否更新正式版本。脚本及所需数据使用相对路径，可整体移动目录。字体为原本本机使用的 BentonSans、Times New Roman 和 JuliaMono；不将字体描述为开源字体。\n\n本次只调整图形摘要的布局与一句结论措辞，没有重新估计结果，也没有投稿或上传。主论文正文 PDF 未因这次图形摘要归档而修改。\n''')
print(out)
