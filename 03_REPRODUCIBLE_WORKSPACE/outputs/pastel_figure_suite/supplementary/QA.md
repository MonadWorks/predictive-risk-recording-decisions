# 补充图 S1–S5 — pastel suite QA

- Reproducer: `render_supplements.py`；输出 `supplementary/figS{1..5}_*_pastel.{pdf,svg,png}`。
- 数据断言全部通过：ECDF 80 个配对差（ties 13/26，端点 −16.23/6.27 与 −1.16/6.27）；条件分层 2880 个条件点（matched / broad / bias_shift × 4 panels × 6 policies × 40 networks）；线性对照 144 点 / 12 系统。区间与汇总直接读冻结 CSV/JSON，无重算。
- 字体：BentonSans 正文与轴文字；Times New Roman mathtext（$\times10^{-5}$、$10^{n}$ 刻度）；S1 端点数值与 S5 事实数字用 JuliaMono。全部嵌入，无 Arial。
- 箭头：BentonSans 子集无 ← → 且 PDF 后端不做字体回退，S1 轴下方向说明改为矢量箭头（annotate）+ 文字，避免缺字形。
- 配色：SCALAR 玫粉 / VECTOR 浅粉（方块带 #B5708C 边）/ FORECAST 琥珀 / GREY 中性；S5 散点填充 #FBEAF1、边线玫粉。旧 POS 蓝 #2B6A9E、NEG 橙 #C2663A 与旧青绿已全部替换。
- S2–S4 绘图区沿用上一轮收缩后的边距，无贴边。
- 限制：程序化断言已过；`STRICT=False` 下重叠仅打印不抛错，本轮无 OVERLAP 输出。全尺寸目视复核留给人工。
