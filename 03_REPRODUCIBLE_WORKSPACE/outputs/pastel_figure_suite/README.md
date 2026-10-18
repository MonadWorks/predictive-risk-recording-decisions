# 论文图组：粉嫩玫粉 + 向日葵琥珀（pastel suite）

2026-10-18。正文 Fig.1–5 与补充 Fig.S1–S5 共 10 张，全部按粉嫩色阶 + 相对的向日葵黄橙色系重绘。Graphical abstract 未改；历史图与论文原件未覆盖。上一轮 `pink_figure_suite` 保留可对照。

先看 `all_figures_pastel.pdf`（每图一页、矢量、含书签）或 `all_figures_overview.png`（导航缩略图）。每图另有 PDF / PNG / SVG。`paper_with_pastel_figures.md` 是换入新图链接并同步图注颜色描述的论文副本，不是重新编译的论文 PDF。

## 相对上一轮（pink 版）改了什么

- **配色整体粉嫩化**：主色从深玫粉 #B73E70 体系整体提亮为 #E27A9E / #F4BFD0 两级粉阶，文字与线保持深色对比；不再使用桑葚 #87385F。
- **引入向日葵琥珀作为相对色系**：原桑葚/青绿承担的 stimulus、ensemble forecast、改进量等角色，改用向日葵琥珀阶（面填 #EDAF26，细线 #DB9A1D），与粉色形成冷暖对比（绿色系被否）。旧蓝/橙/青绿/桑葚及上一版沉琥珀 #D89430 的精确色值在 10 张 PNG 中清零（`suite_verification.json`）。
- **字体整套换成 BentonSans**：来源为 kuali/www-theme-kuali 的 Webtype 子集（regular / bold / regular-italic，仓库无 plain bold-italic）。name 表原样无法区分字重，已在本机修正后注册。公式用 Times New Roman（mathtext），关键结果数值用 JuliaMono。所有 PDF 嵌入确认，无 Arial。
- **箭头矢量化**：BentonSans 子集缺 ← → 且 PDF 后端不做字体回退，S1 方向说明改为矢量箭头。

## 字体层级（180 mm 原图）

| 层级 | 字体 | 字号/字重 | 色值 |
|---|---|---|---|
| 面板字母 | BentonSans | 8 pt Bold | #2E2531 |
| 短标题 | BentonSans | 7 pt Bold | #2E2531 |
| 轴标签 | BentonSans | 7 pt Regular | #49424B |
| 类别标签 | BentonSans | 6.8–7 pt | #2E2531 |
| 刻度 | BentonSans | 6.3 pt Regular | #6B626D |
| 公式 | Times New Roman | 随上下文 | #2E2531 |
| 结果数值 | JuliaMono | 6.5 pt | #2E2531 |
| 次级说明 | BentonSans | 6 pt Regular | #7D7280 |

层级靠字号、字重、深浅与位置共同形成。BentonSans 为网页子集（缺希腊字母与箭头），涉及处已用 mathtext/矢量方案绕开；排入不同栏宽时需按实际尺寸复查。字体授权状态未在本机验证，投稿前请自行确认。

## 配色规则

- 玫粉 #E27A9E：单响应；浅粉 #F4BFD0：共享三响应（方块 + #B5708C 边线）；向日葵琥珀 #EDAF26 / #DB9A1D：刺激输入、ensemble forecast、改进条；图 5 三响应改用同族暖橙 #E8A13C（不在同一标记里混两种强调色）；中性灰 #DAD4D8 / #B9AEB7：相同集合与参照；图 4a nominal 风险用灰 #7D7280 空芯。
- 热图正负号：POS #C25E88，NEG #4E4350（深梅灰，靠明度与中点白分离，不用黄橙承担负号以免与琥珀角色混淆）。
- 色觉模拟（`palette_checks.json`）：玫粉 vs 浅粉 deutan ΔE≈17；浅粉 vs 中性灰 ΔE≈3（近），故保留圆/方、空/实与边线；琥珀 vs 玫粉各模拟下 ΔE≥12。不把模拟当合规认证。

## 验证与限制

- 10 张 PDF 全部 `pdffonts` 嵌入检查；fig3/4 附对齐网格证明图（`*_alignment.png`）。
- 数据断言沿用冻结包：fig2 q=2.43518×10⁻⁴ 等、fig3/4 数值与 19/40、64% 截断标识、S1 ties 与端点、S2–S4 2880 点、S5 144 点全部通过；未重算任何科学区间。
- 精确旧色值（蓝/橙/青绿/桑葚/深玫粉）在 10 张 PNG 中为 0 像素；新玫粉与琥珀在对应图中存在。
- 原始数据副本与 GA 字节核对未变。文本出界/重叠为程序化检查；全尺寸审美目视复核留给人工，这轮未做匿名审美评分。
- 凭证：`suite_verification.json`、`qa_receipt.json`、`palette_checks.json`、`fig1_fig5_QA.md`、`fig2_data_overview_QA.md`、`supplementary/QA.md`。

四个 `render_*.py` 为本机复跑入口（读取 `work/evidence` 冻结副本），字体在 `fonts/`。所有图保留矢量版本，便于下一轮只改局部。

## 2026-10-18c：本机修改复核后的精修

保留本机 BentonSans 字体、向日葵配色（其他图）、奇偶页统一页边距、首页版本说明移除及紧凑证据表。Fig1仅对示意风险/误差的两条bar使用浅粉+深粉；两条起点由115 mm移至109.5 mm，靠近标签。风险框与上方a框共享87 mm左边界。b/c点估计和区间分行，分别检查文字框是否越过面板边界及是否互相重叠，不再把字体嵌入检查冒充版式验证。

左下1/2改成独立的小号编号和等距注释，标题与正文共享12.5 mm左边界、编号x=9 mm；两段标题—正文距离均5.6 mm。表述分别说明“相同数据和确定性拟合→相同点预测”及“固定点预测后评价风险估计”。删除误导的“good forecast: v close to e²”，图内不再暗示风险应逐样本等于平方误差。c标题改Score difference，图注明确prior-averaged减nominal的平均评分差。

S5右侧改紧凑两列表格（12系统、144评估、8192次MC抽样），不是三组放大的陈列数字；保留嵌套单位和验证范围说明。S1–S4说明同步精简，未改数据点/区间。正文两个方法表列宽与内边距局部修复，消除了继承的5条Overfull警告。

新审计见 `fig1_layout_audit.json` 和 `refinement_audit.md`。之前PDF和Fig1在 `../revisions/before_fig1_refinement/` 快照保留。未更换Encode Sans Condensed，未改GA。
