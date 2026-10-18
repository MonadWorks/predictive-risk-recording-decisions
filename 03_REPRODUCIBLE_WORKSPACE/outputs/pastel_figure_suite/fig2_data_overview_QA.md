# Fig2 (data overview) — pastel suite QA

- Reproducer: `render_data_overview.py`；输出 `fig2_data_overview.{pdf,svg,png}`（180 × 122 mm）。
- 冻结数据断言全部通过：J5000 权重 144 条、vmax 0.42、记录节点 [6,8,11]、stim/readout (0,4)、校准观测 180 行、持出响应 120 行、Δt=0.05、q = 2.43518 × 10⁻⁴ 与 manifest/paper 一致。
- 文本检查（STRICT）：无出界文本、无绘图区文本框重叠。
- 字体：正文 BentonSans（Regular/Bold 嵌入）；公式 Times New Roman（mathtext，嵌入）；色标与轴刻度继承 mm 锚点体系。无 Arial。
- 配色：热图 NEG #4E4350 → 白 → POS #C25E88，零点严格居中；记录点 SCALAR 玫粉、readout 环 shared 浅粉、stim 环 sunflower 琥珀 #EDAF26；刺激阶梯与响应曲线用同族细线 #DB9A1D（比面填略深，保证 1.1 pt 线可见）。旧蓝/橙/青绿精确值清零。
- 网格线换暖灰 #EFE6EB。积分说明与 q 数值文本位置未动。
- 限制：色觉模拟数值见 `palette_checks.json`；浅粉与中性灰在部分模拟下接近，圆/方与空/实区分保留。
