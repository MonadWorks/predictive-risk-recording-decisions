from pathlib import Path
import shutil
root=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026');f=root/'outputs/graphical_abstract';src=f/'source';draft=root/'outputs/graphical_abstract_redesign'
s=(draft/'render_graphical_abstract.py').read_text().replace("ROOT=Path('/Users/dujiayi/Documents/Codex/2026-10-18/icbr-2026');OUT=ROOT/'outputs/graphical_abstract_redesign'", "ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/'rendered'\nOUT.mkdir(parents=True,exist_ok=True)")
for a,b in [("ROOT/'work/ga_redesign/mpl'","ROOT/'.cache/mpl'"),("ROOT/'outputs/pastel_figure_suite/fonts'","ROOT/'fonts'"),("ROOT/'work/evidence/ICBR2026_v4_pack/03_figures/render_v4.py'","ROOT/'baseline/03_figures/render_v4.py'"),("str(OUT/'optical_grid.py')","str(ROOT/'optical_grid.py')")]:s=s.replace(a,b)
(src/'render_graphical_abstract.py').write_text(s);shutil.copy2(draft/'optical_grid.py',src/'optical_grid.py')
p=src/'audit_graphical_abstract.py';s=p.read_text().replace("check(not layout['text_overlaps'],'no detected text overlaps')", "check(not layout['text_overlaps'],'no detected text overlaps');dy=layout['optical_grid'].get('body_translation_y',0)")
s=s.replace('if 39<y<107 and x>56:', 'if 39+dy<y<107+dy and x>56:').replace('37.5<=y and yy<=109.5','37.5+dy<=y and yy<=109.5+dy').replace("t['bbox'][0][1]<34.8", "t['bbox'][0][1]<34.8+dy").replace("t['bbox'][0][1]>=17.2 and t['bbox'][1][1]<=34.8", "t['bbox'][0][1]>=17.2+dy and t['bbox'][1][1]<=34.8+dy")
p.write_text(s)
p=f/'README.md';s=p.read_text().replace('archived version 2','archived version 3').replace('当前工作归档 v2；v1 ZIP 保留。','当前工作归档 v3；v1、v2 ZIP 保留。');p.write_text(s)
p=f/'CHANGELOG.md';s=p.read_text();p.write_text('''# v3 · 2026-10-18\n\n保留共同预算 / MAP 控制、相同记录和数据产生相同预测的机制，以及主要区间与探索性扩展的限定；四行、两组思路，仅短语加粗。标题至长横线收紧 1.2 原坐标单位；主体整体上移 2.0，标题两行间距不变。圆点与图例文字的横向距离保留；Response readout 文字单独下移 0.12 原坐标单位。\n\nv1、v2 ZIP 均保留。\n\n'''+s)
(f/'editorial_review_v3.md').write_text('''# v3 说明\n\n本轮不机械地逐句恢复，也不将原机制和结果全部替换为方法介绍。保留 Identical recording sets and data… 的机制；增加跨响应目标比较 nominal / prior-averaged risk、共同预算与 MAP 拟合，及固定预测的风险检验。保留区间包含零、8 个独立 100-unit rank-two 网络、4/8 setting-specific 未校正区间及一项反向点估计。\n\n短语 common budget and MAP fit 加粗，其余常规字重。四行按两个内容块组织。论文原 Introduction I2–I6、Results R1–R2、Box 1 和 Methods 对应这些方法事实；没有新增独创性、因果识别或生物验证声明。\n\n研究和风格参考及其使用范围见 editorial_review_v2.md。本轮按用户澄清保留圆点到文字的横向距离；Response readout 的文字另下移 0.12 原坐标单位。标题到横线及横线到主体更紧凑，主体整体上移，内部间距保持。\n''')
print('Prepared portable v3 sources.')
