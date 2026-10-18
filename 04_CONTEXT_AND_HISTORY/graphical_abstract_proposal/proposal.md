# ICBR graphical abstract：内容与构图提案

2026-10-18。讨论稿，尚未制作或替换正式 GA。论文 PDF 已更新为作者选定的短标题。

## 推荐主旨

比较风险估计、记录决策和实际响应误差，是相互关联但不同的评价问题。主条件下，两准则常选择相同记录；主要误差和风险评分比较仍有不确定性。

候选引导句：Does prior averaging improve neural recording decisions and response prediction?
正文必须明确 nominal versus prior-averaged local risk；避免使用“refined”预设其更好。

## 三种构图方向

A（推荐）双路径叙事：左侧模拟网络与记录预算，中部两条独立评价路径，底部紧凑证据区。保留原科学链条，重新安排主次。
B 结果主导：少量上下文，三个主效应区间为中心。定量最直接，但与正文主图相似，容易成为缩小的结果海报。
C 旧版精修：保留三栏和已有布局，减字、统一字体配色并纠正语义。改动小，但仍缺乏一个占主导的科学视觉。

## A 的内容安排

1. 场景：简化真实模拟网络、刺激符号、隐藏读出与三个记录点。文字为 Known connectivity / uncertain physiology / record 3 of 12 units。不添加机器人、培养皿或湿实验照片，因为本文没有验证这些平台。
2. 路径 A（40 independent networks）：nominal / prior-averaged → compare recording sets → common MAP fitting → response error against hidden truth。相同集合汇合这一图形只表达条件关系，不能画成所有设计都相同。
3. 路径 B（40 new independent networks）：固定 recording set + data + point prediction → compare two MSE forecasts → score forecasts。与 A 并列，不从 A 的误差画时间箭头连到 B。不画预测分布或置信带，本文评分的是 MSE functional，不是完整预测分布。
4. 紧凑证据：记录一致计数 82/120 single-target designs 与 26/40 shared designs；误差变化 −3.7% [−18.5,+12.1] 与 +2.7% [−3.0,+11.5]，明确 97.5% CI；评分差 −0.46 [−1.16,+0.02]，明确 95% CI、prior-averaged minus nominal。保留一句 mean influenced by one network，避免单独放一个看似有利的负数。计数是设计，独立单位是网络；不要把 120 当成 120 个独立网络。
5. 结论：Recording agreement, response error and forecast accuracy require separate evaluation. 对本研究附上 Primary improvements remain uncertain. 最终文案应避免重复。
6. 边界：模拟研究、已知连接。100-unit 扩展不进入主视觉；若有空间，只用一行注明 exploratory / n=8 / condition-dependent，不能与主证据并列成已确认发现。

## 旧版保留与修正

保留：三步科学问题、两独立研究、共同 MAP 控制、真实冻结数据、点区间的统计语法、已有可编辑矢量绘图函数。v4 的网络结构和 v5 的分析流程各有可复用部分。
重排：减少三张等权大卡片、黑色结论横条、巨大编号、百分数字号、全量点阵；作者信息在提交版可缩为一行，署名信息不丢失，完整单位保留在 CMT 和摘要作者栏。
修正：v5 的风险 v 不应与原始误差 e 用同尺度横条比较；若比较对象是单次损失应为 e²，但单次 v≈e²也不是好预测的充分判据。最好改画风险评分流程。
修正：“收益被选点改变频率封顶”不是由一致计数推得的定量界限；少数不同设计可以有大效应。“refined risk”预设改善，改为 prior-averaged risk。“fits any criterion”超出实证范围，删除。
旧版 19/40 是评分更低的网络数，不是点预测更准，也不是独立证明校准改善；若空间不足，不把它作为巨大主数字。

## 视觉规范（设计建议，不是 ICBR 强制要求）

先做 3:2 横向矢量母版；检查真实缩小显示后再决定是否需要方形适配。白底为主，浅粉用于局部区分，深玫瑰用于重点，现有向日葵色只用于少量对比。灰色空心/彩色实心仍表示 nominal/prior-averaged；不要在同一图内改义。
BentonSans Bold 仅用于短标题和层级标题，Regular 用于说明；Times New Roman 限公式；JuliaMono 仅紧凑数值。说明不全加粗，正文用深墨色，次级注释用可读灰色。
建议图内核心英语文字约 90–130 词（初稿目标，不是投稿规则）；将所有结果区间保留所需的统计标签，不能为减字删掉比较方向或置信水平。
交付与审查：原创可编辑 SVG + 嵌入字体矢量 PDF + PNG；检查实际展示尺寸下的文字、对齐、色彩语义和数值；同时提供约 600 px 宽预览以判断层级。先看缩图是否读得出问题和两条路径，再看放大后数字是否可核对。

## 参考与证据

- ICBR 官方：需要 GA，只收 extended abstract，不要求完整论文；公开页面未给 GA 长宽比或字体规范。https://icbr2026.org/submission_guidelines.html
- Elsevier：简洁视觉摘要、明确阅读起终点、减少杂乱；网页同时给出不同风格的真实文章示例。其尺寸与字体条款不能当成 ICBR 要求。https://www.elsevier.com/researcher/author/tools-and-resources/graphical-abstract
- PLOS Computational Biology, Ten simple rules for designing graphical abstracts：先确定受众与主旨、统一图标、用清楚布局与颜色编码、必要时使用简化数据图、寻求反馈。https://doi.org/10.1371/journal.pcbi.1011789
- Cell Press 编辑建议：少文字、清楚视觉流程、区别于正文图；其“不含数据”风格不是 ICBR 的通用禁令。https://crosstalk.cell.com/blog/attract-readers-at-a-glance-with-your-graphical-abstract

本轮实际查看了本地 v3/v4/v5 PNG 与 Claude 会话中的旧图批评，读取上述公开指南。Ego Lite 启动受本机服务连接错误阻止，改用网页读取工具查阅；没有操作 CMT 或上传内容。
