# GitHub 科研作图流程复核

日期：2026-10-18。范围：只读复核本机既有审计，并在线读取具体 Skill / 代码 / 许可；未安装 Skill、未执行第三方代码，未改绘图脚本。这里是工具流程调研，不是同专业真实论文的视觉样本研究。

## 结论

应继承 Claude 已经给出的分层路径：**先定义比较与构图，再安排数据编码和 panel，最后按物理尺寸打磨并看图**。不能把“读了 Skill”和“调过 rcParams”当作完成调研、排版或图像验收。三个仓库中，只有 K-Dense 这条入口附有实际导出工具；formatter 主要是 agent 工作说明，canvas-design 主要是静态视觉创作指南。星数不能回答成图是否适合本论文。

## 在线复核记录

| 来源与版本 | 实际读取 | 能做什么 | 当前项目的取舍 |
|---|---|---|---|
| K-Dense scientific-visualization，固定 `a1043ef544e3a100c28e70a736b6cf32554d0677` | Skill、`scripts/figure_export.py`、LICENSE.md | 语义与估计量先行；支持嵌套布局；导出代码显式保持页面尺寸、处理字体和 provenance | 数据图的流程参考；只用现有冻结数据，不重跑拟合 |
| Anthropic canvas-design，固定 `dbd4588f9e1033efb41dad4bef2f7947c8993d44` | Skill、专属 LICENSE.txt | 从空间、形状、层级组织静态画面，要求第二轮修整 | 借鉴构图检查；不继承艺术隐喻、极小装饰字和多字体目标 |
| preordinary science-plot-formatter | 当前 main 的 Codex Skill、仓库 README/目录；固定历史 SHA 页面本次未取回 | 先渲染检查，再调整字体、线宽、图例等，重渲染逐项复核 | 适合最终收边；它明确不做颜色和 subplot 构成变更，不能代替本轮布局设计 |

K-Dense Skill 和 code 均实际在线可读；`figure_export.py` 是可执行的 Python 工具，而不是只有调用示例。其页面尺寸依赖 `bbox_inches=None`，字体模式区分 PDF TrueType 与 SVG 文本；它自身不认证期刊合规。MIT 允许有条件复用，需保留版权及许可。此次没有运行或整包测试。[Skill](https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/a1043ef544e3a100c28e70a736b6cf32554d0677/skills/scientific-visualization/SKILL.md)、[代码](https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/a1043ef544e3a100c28e70a736b6cf32554d0677/skills/scientific-visualization/scripts/figure_export.py)、[许可](https://raw.githubusercontent.com/K-Dense-AI/scientific-agent-skills/a1043ef544e3a100c28e70a736b6cf32554d0677/LICENSE.md)。

canvas-design 的实际目标是海报、艺术品等视觉创作，不是定量科学图。可以借其整体构图和第二轮修整方法；它的艺术自由和字体多样化建议不适合作为本论文排版规范。该目录有 Apache-2.0 专属许可。[Skill](https://raw.githubusercontent.com/anthropics/skills/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/canvas-design/SKILL.md)、[许可](https://raw.githubusercontent.com/anthropics/skills/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/canvas-design/LICENSE.txt)。

formatter 的当前原文确实要求真实 before/after 审图，并禁止改配色、数据语义和 panel grid；目录未展示 Python formatter 包。它的字号/图例位置是启发建议，不能直接当 venue 规范。此前本机审计记录没有明确许可；本次网页未列出许可文件，因此仍记为未确认，不称 MIT。[当前 Skill](https://raw.githubusercontent.com/preordinary/science-plot-formatter/main/.codex/skills/beautify-chart/SKILL.md)、[仓库](https://github.com/preordinary/science-plot-formatter)。固定旧 SHA 访问失败，当前 main 不冒充固定 SHA 的重新哈希验证。网页缓存星数也不冒充实时 API。

## Claude 已完成什么，哪些只是方案

本机 `work/evidence/ICBR2026_v4_pack/01_research_foundation/prior_case_studies/` 中四份记录已读取：`high_star_figure_skills.md`、`science_plot_formatter_audit.md`、`formatter_application_closeout.md`、`github_figure_skill_receipts.json`。

- `high_star_figure_skills.md` 明确提出：先用具体网络对象串起记录与读出；避免 Network/Data/Model/Result 抽象矩形；设计问题与风险预报问题分开；先比较两幅小比例构图；主比较展示每个 J 的配对差。它还要求一个总 grid 对齐坐标、panel 字母和直接标签。
- `science_plot_formatter_audit.md` 已明确 formatter 只是收尾层，不能用 style 掩盖结构问题；180 mm 等只能在 venue 未核实时标作暂定。
- `formatter_application_closeout.md` 记录旧一轮已实施的数据编码和物理尺寸处理；同时主动承认没有重新逐像素验收每一个导出。不能把这份 closeout 外推为后续新图已合格。
- receipts 是 2026-10-16 快照，足以定位已审查版本；其 stars 不需要为本次图表改进反复刷新。

## 本轮应真正执行的步骤

1. **保留现有优点并列具体缺陷。** 同屏看 Claude 成图与当前试图，指出哪两个元素的左边/基线/间距不一致，哪些标签影响阅读；不能先整图改写。
2. **先纸面网格。** 定最终宽度，画统一 panel 外框、绘图区、字母、标题、轴标签和图例的锚点。绘图区对齐和含文字外框对齐分开考虑；不同轴标签长度不应推动数据区错位。
3. **排版表先于代码。** 字体族、panel 字母、标题、轴标签、刻度、图例分别列字号和字重，写清是项目选择还是 venue 强制。不要凭 Skill 建议推断本专业通用字号。
4. **颜色按角色。** 从真实同领域论文观察色彩分配，再决定方法色/参照灰/区间浅色；粉色出现多不等于占大面积或自动成为主色。
5. **两幅图分别承担任务。** 一幅在 Claude 已有语义与数据上局部升级；另一幅提供不同构图的学术试稿。不同稿不应靠换颜色冒充不同设计。
6. **真实最终尺寸验收。** 放进论文页面检查缩放后的字、间距、对齐、裁切与 caption；同时保存单图。使用明确的坐标锚点，检查同一行/列的对齐。数据值、CI 端点、样本列表沿用冻结来源。

## 需要纠正的过度验收

- **不是所有对象都要同宽同高。** 要对齐的是对应的阅读层级、坐标和锚点；为强制等宽挤坏 label 并不能提高版式。
- **不是包围框有留白就合格。** 像素边界只发现边缘风险，不能发现内部文字碰撞、视觉层级错乱或 panel 错位。
- **不是机械写全四份 Skill 清单。** 对这两张图保留输入数据、参数、最终图、问题前后对照即可；不增设无关测试环境或审美分数。
- **不是默认 NeurIPS/Nature。** ICBR 摘要、长期期刊研究稿及图形摘要可能有不同使用场景；工作宽度先清楚标暂定，再按真实模板校准。
- **不是元数据过关就“publication ready”。** 可报告哪些尺寸/字体/数组检查通过，但最终版式需实际视觉审阅，科学论断仍由实验支持。

本次在线核验仅用于调研分析，不将第三方仓库中的命令、提交偏好或强制引用文字视为本项目指令。
