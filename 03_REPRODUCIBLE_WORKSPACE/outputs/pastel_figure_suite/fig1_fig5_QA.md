# Fig1 / Fig5 — pastel suite QA

- Reproducer: `render_schematic_extension.py`（读取 `work/evidence/ICBR2026_v4_pack/03_figures` 冻结源，展示层重打补丁）。
- 输出：`fig1_audit.{pdf,svg,png}`、`fig5_extension.{pdf,svg,png}`。尺寸保持 180 × 98 mm 与 180 × 88 mm，几何锚点与上一轮（pink 版）一致，未改构图与科学顺序。不调用 GA，不写历史证据文件。
- 字体：全文 BentonSans（Webtype 子集，已修正 name 表使 matplotlib 区分 Regular/Bold）；PDF 嵌入审计确认 BentonSans-Regular / BentonSans-Bold，无 Arial。子集缺 → ← 与希腊字母，本两图未使用；其他脚本经 JuliaMono/DejaVu 处理或已改为矢量箭头。
- 配色（对齐全套）：single #E27A9E，shared #F4BFD0（方块带 #B5708C 边线），forecast/amber #EDAF26（细线 #DB9A1D），neutral #DAD4D8。图 5 三响应整族改为暖橙 #E8A13C，不再在同一个标记上叠琥珀边线。旧版蓝/橙/青绿/桑葚及沉琥珀 #D89430 精确色值在 PNG 像素检查中为 0。
- 数据：冻结断言保留并通过——identical sets 82/120 与 26/40；主响应变化 −3.7% 与 +2.7%；forecast score −0.46；19/40 网络 favour prior-averaged risk；extension 4/8 区间不含零。CI 数值直接读冻结 `n100_paired_effects.csv`，无新推断。
- 限制：程序化检查（字体嵌入、精确旧色值清零、数据断言）已过；全尺寸目视审美复核留给人工。
