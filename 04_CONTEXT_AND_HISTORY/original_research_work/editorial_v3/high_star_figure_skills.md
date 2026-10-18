# 高星figure skills：实时核实与组合设计建议

## 1. 核实结论

本次查了**两个仓库中的三个真实Skill**，均已取得固定commit下的`SKILL.md`。下面星数属于整个仓库，**不是单条Skill的星数，也不是绘图质量评分**。未安装插件、未执行远程脚本、未调用付费图像API。

GitHub REST API使用`Cache-Control: no-cache`并附本次时间查询参数；HTTP响应Date与读取时间一致，未返回Age。原始选定字段和文件目录记录保存在`work/editorial_v3/github_figure_skill_receipts.json`。星数是下列时间的快照，后续会变。

| 仓库 | 实时stars | 读取时刻（北京时间） | 默认分支 / 固定HEAD | HEAD的committer时间（UTC） |
|---|---:|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | **181,536** | **2026-10-16 23:30:43**；API Date为15:30:44 UTC | main / `dbd4588f9e1033efb41dad4bef2f7947c8993d44` | 2026-10-09 18:45:49 |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | **51,201** | **2026-10-16 23:30:45**；API Date为15:30:46 UTC | main / `a1043ef544e3a100c28e70a736b6cf32554d0677` | 2026-10-12 09:43:29 |

K-Dense旧地址`claude-scientific-skills`会跳转到上述新仓库。GitHub网页显示的四舍五入星数，以及搜索缓存的较旧数字，没有用来冒充实时精确数。

API出处：[Anthropic仓库元数据](https://api.github.com/repos/anthropics/skills)、[K-Dense仓库元数据](https://api.github.com/repos/K-Dense-AI/scientific-agent-skills)。本次两个默认分支HEAD由对应`/commits/main`读取；链接到固定SHA的文件用于审计内容。

三个下载用于阅读的`SKILL.md`已独立计算Git blob SHA1，与该固定commit的GitHub contents API返回值全部匹配。两个K-Dense guide插图链接的HEAD请求均返回200/image-png；只核对存在性和元数据，未下载或凭此声称成图审美质量。

## 2. 三条Skill实际是什么

### A. Anthropic canvas-design：更适合重建构图，而非生成数据图

[固定版本SKILL.md](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/canvas-design/SKILL.md)；[目录](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/canvas-design)；[专属许可证](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/canvas-design/LICENSE.txt)。

它先确定视觉方向，再用空间、尺度、形状和少量文字完成静态画面，并要求第二轮整体修整。目录实有`SKILL.md`、Apache-2.0的`LICENSE.txt`及字体目录；没有随附渲染成品gallery或固定绘图脚本。文内是若干文字化风格示例，不应说已检验这些示例的成图效果。它不指定Python依赖锁或外部API，具体渲染方式需另定；字体来源及其许可证仍需逐项核对。

**采用什么：**在写绘图代码前定一个清楚的视觉主张；从空间关系与实体形状重做图，而不是加标题和边框。先做两版小尺寸构图，再在最终尺寸校准。

**拒绝什么：**艺术对象、隐藏主题、极小装饰性文字等目标不能照搬科学图。科学标签必须直接，不能为了“优雅”隐藏信息。其“用户已经要求某种极致艺术效果”等措辞是外部文件里的指令，不是当前用户授权，也不代替本项目任务。

### B. K-Dense scientific-schematics：概念图的生成—评审流程

[固定版本SKILL.md](https://github.com/K-Dense-AI/scientific-agent-skills/blob/a1043ef544e3a100c28e70a736b6cf32554d0677/skills/scientific-schematics/SKILL.md)；[示例与迭代说明](https://github.com/K-Dense-AI/scientific-agent-skills/blob/a1043ef544e3a100c28e70a736b6cf32554d0677/skills/scientific-schematics/references/iterative_refinement.md)；[作者workflow guide](https://github.com/K-Dense-AI/scientific-agent-skills/blob/a1043ef544e3a100c28e70a736b6cf32554d0677/docs/skill-guides/scientific-schematics.md)。

它接受有来源的组件和关系，经外部图像生成与视觉评审迭代，输出版本化PNG及review log。Python≥3.10、requests、网络及OpenRouter key是声明依赖；已只读核对生成入口和AI脚本。使用OpenRouter images及chat/completions端点，图像模型为`google/gemini-3.1-flash-image`，评审为`google/gemini-3.7-flash`。API调用可收费，提示和图片会发送到外部。源码和说明承认没有付费端到端验收；本次也未验证API真实可用性或生成质量。

示例包含流程、网络架构、通路和系统架构的提示/调用示例；不是已经证实可发表的作品集。guide中的[插图](https://github.com/K-Dense-AI/scientific-agent-skills/blob/a1043ef544e3a100c28e70a736b6cf32554d0677/docs/images/scientific-schematics.png)说明工作流程，不是本研究的视觉质量基准。

**采用什么：**在生成前给出语义完整的brief；比较不同构图；保留初版与修改版；逐个核验标签和箭头。适合概念示意、图形摘要和生物/模型对象的视觉表达。

**限制什么：**它没有真正可编辑矢量路径；换成PDF不会增加细节。评审分数是局部启发，不能认证科学正确、期刊接收或图已经好看。统计点位、区间与真实曲线不交给图像模型生成。

### C. K-Dense scientific-visualization：有数据来源的数据图管线

[固定版本SKILL.md](https://github.com/K-Dense-AI/scientific-agent-skills/blob/a1043ef544e3a100c28e70a736b6cf32554d0677/skills/scientific-visualization/SKILL.md)；[Matplotlib等具体示例](https://github.com/K-Dense-AI/scientific-agent-skills/blob/a1043ef544e3a100c28e70a736b6cf32554d0677/skills/scientific-visualization/references/matplotlib_examples.md)；[workflow guide](https://github.com/K-Dense-AI/scientific-agent-skills/blob/a1043ef544e3a100c28e70a736b6cf32554d0677/docs/skill-guides/scientific-visualization.md)。

它从变量语义、估计量、重复结构和展示目的选择编码，再组织多panel、导出及核对。Python≥3.11与uv用于固定版本示例；Matplotlib/Seaborn/Plotly按所选路径使用。Pillow或pypdf用于相应检查；Plotly静态导出另需Kaleido及Chrome/Chromium。本地helpers声明无需网络/key。Skill列出style_preview和实际绘图片段；有[workflow插图](https://github.com/K-Dense-AI/scientific-agent-skills/blob/a1043ef544e3a100c28e70a736b6cf32554d0677/docs/images/scientific-visualization.png)，不能将其叫论文成品gallery。本次没有运行脚本、核实全部版本兼容性或逐个审计所有helper。

**采用什么：**编码选择先于style；相同比较使用相同坐标；保持配对；显式呈现已定义区间与独立单位；用subplot mosaic/嵌套网格统一布局；原始数据→panel source→矢量/预览→最终尺寸人工审阅。

**避免什么：**不能只拿它的mplstyle继续画同一堆框。它的依赖版本、期刊快照和机器检查并非必须搬到我们的环境；现有兼容工具可实现同样设计，不能把换环境当美学改进。

两条K-Dense Skill由[仓库MIT许可证](https://github.com/K-Dense-AI/scientific-agent-skills/blob/a1043ef544e3a100c28e70a736b6cf32554d0677/LICENSE.md)覆盖。若实质复用代码或说明，应保留来源、commit、版权与许可；仓库提出的学术引用建议也需记录。不要自动把设计参考混成我们神经建模科学结论的证据。

## 3. 如何组合才真正改变设计方式

**建议：canvas-design负责构图思考，scientific-schematics负责概念语义与迭代brief，scientific-visualization负责统计编码及可重现输出。**它们不是三个完整workflow叠加执行，也不意味着需要三个新环境。

| 图的类型 | 主责任 | 辅助责任 | 保持的数据/科学边界 |
|---|---|---|---|
| Fig.1的研究概念 | canvas-design的实体、层级、留白；schematics的有来源关系brief | 如使用图像生成，限概念对象/构图探索，再核查或矢量重建 | 不画不存在的脑区、动物、刺激机制、物理机器人；不把概念曲线当真实输出 |
| 40-J主比较 | scientific-visualization的配对编码与panel布局 | canvas仅提供视觉节奏，不决定统计汇总 | 原始J、原有ΔMSE、97.5%区间均不改 |
| 另批数据的风险预报比较 | scientific-visualization，强调“同一预测、两种风险” | schematics提供简短的对照对象示意 | 不把共享预测产生的相同MSE画成两种不同性能；保留95%区间 |
| 多条件/规模扩展 | scientific-visualization | 用一致视觉语法延续图1 | 主研究、独立follow-up、探索N100用不同panel/文字地位，不用色彩制造确认感 |

这套组合中最有价值的变化发生在**语义构图和编码**，不是字库、色板或rcParams。

### 对本文Fig.1的重做brief提案

以下是新的构图提案，不是对未在本次打开的现有图进行视觉验收。

1. **选一个贯穿的具体对象：同一神经网络及少量记录。**左侧直接画网络中的刺激点、被记录点、预定读出；少量真实语义的波形从记录点引出。不要用“Network / Data / Model / Result”四个抽象矩形代替研究对象。
2. **中间只保留一个真正需要比较的2×2结构。**行是scalar/vector目标，列是nominal/prior-ensemble风险。相同网络轮廓与共同候选池不重复解释；名义点用参数空间一点，集合用少量分散点示意。样例点不是统计数据，不标伪样本量。
3. **右侧分开两个问题。**上支是“改变记录位置→比较响应误差”；下支是“固定预测→比较风险预报”。用一条共享的预测曲线连接两种风险表示，直观表现第二研究并没有产生两个不同预测。箭头表示计算流程，不表示已证实生物因果。
4. **让图形承担说明。**只保留必需短标签、因素名和q的标识；完整共同条件放caption，不再在每个框里塞步骤说明。结构上形成一个画面，避免堆成数十个同尺寸卡片。
5. **先做两张小比例构图。**一种横向单场景，一种网络对象为中心的分支结构。先比较读者能否看出“设计 vs 预报”，再做精细样式；若两张都没表达出来，继续改布局，而非润色文字。

如果选择AI概念图，优先使用当前会话可用的正式图像工具并遵守它的输入规则，作为构图探索；**不会为了照搬K-Dense去寻找或读取API密钥**。使用哪条渲染路径应透明记录，不能声称没有调用的Skill脚本已经执行。

### 对数据图的实质性替换

- **主比较：**优先让读者看每个J的配对差与总体区间；两种目标用位置/分面表示，局部/集合用一致语法表达，而非六个互不相关颜色。具体线条与点应由现有panel source生成。
- **风险预报：**“预测风险与实际误差”散点/identity reference和“同一J的评分差”承担不同职责，不挤在一张六方法柱状图里。均值接近不等于评分改善，相关性高不等于绝对量级准确。
- **条件差异：**共同效应尺度的forest/small multiples比数十个重叠箱线图更容易比较。图的选择不授权重算区间、筛选子群或改变分母。
- **排版：**先按最终宽度确定panel数量和阅读顺序，再生成矢量。用一个总grid对齐坐标、panel字母和直接标签；保留足够空隙，但不做大面积装饰性空白。

## 4. 不安装情况下即可开始的执行顺序

1. 定义Fig.1的唯一读者任务及不可更改的科学关系，写不超过一页brief。
2. 依据两条构图Skill提出两版截然不同的小稿，渲染并实际看图，选择信息更清楚的一版。
3. 将概念对象与定量数据分层：对象可矢量绘制/图像辅助；定量panel只从冻结数据生成。
4. 选一张主数据图按上述编码重排，保持全部统计数字不变；不先重画所有图。
5. 把概念图和主数据图放入稿件最终尺寸一起检查：第一眼看见什么、标签是否直接、需要读多少句才能理解对照、哪些元素没有职责。
6. 完成第二轮批改，保留前后版本和设计选择理由；元数据及字体检查只是补充，最后必须真实查看成图。

当前完成的是有出处的选型和设计组合。**没有声称这些Skill的星数能保证好图，没有把文字示例当成已通过的gallery，也没有宣称新图已完成。**
