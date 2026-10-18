# 论文前半的定向写作参照：三篇原始研究

核验：2026-10-16。选择依据是问题接近、论证可追踪、研究操作明确；没有据作者母语判断质量，也未查询或猜测当前影响因子。三篇已足够覆盖结构约束、有限记录、干预泛化，并且第三篇有**实际主文表格**，无需为“有表格”再引入不相干论文。

注意：这里分析论证功能，供独立写作；不复制原文段落、图形或语句节奏。以下“可借鉴”均为我们的写作建议。

## A. Beiran & Litwin-Kumar，Nature Neuroscience 2025

*Prediction of neural activity in connectome-constrained recurrent networks*，28:2561–2574。[正式原文与图索引](https://doi.org/10.1038/s41593-025-02080-4)，[正式作者稿](https://pmc.ncbi.nlm.nih.gov/articles/PMC12648571/)。必须引用正式版：早期预印本的图编号不同。

**叙事链：**结构—动力学关系→从活动反推连接的歧义→连接组可测但生理参数未知→固定J的teacher–student→区分活动预测与参数恢复→限定模型假设。它先定义“已知什么/未知什么”，再给方法，避免把所有脑建模混作一题。

**已核主图顺序：**1任务输出/内部动力学；2有限记录；3活动维度；4模型失配；5经验连接结构；6线性理论；7非线性损失；8记录位置选择。正式网页未列主文Table；不声称补充材料完全没有表。

**可借鉴：**以一项可检验区别组织全篇；用简化理论解释数值现象；记录误差和参数误差分开。**不可照搬：**最优记录位置、增益/偏置不确定性或失配稳健性已是该文成果；经验连接结构模型也不等于真实生物干预验证。

## B. Lappalainen et al.，Nature 2024

*Connectome-constrained networks predict neural activity across the fly visual system*，634:1132–1140。[正式原文](https://doi.org/10.1038/s41586-024-07939-3)，[作者模型](https://github.com/TuragaLab/flyvis)。

**叙事链：**连接可测而单细胞动力学不可全测→结构或任务各自不足以决定机制→结合连接、简化动力学和任务优化→对照已有神经实验→保留模型集合歧义与待验证预测。

**已核主图：**1模型/数据/任务；2神经调谐预测；3模型集合分群与实验建议；4运动计算机制。Extended Data Fig2有连接约束和细胞类型信息消融。全文网页未检得主文Table；补充七份数据文件不是七张主文表。

**可借鉴：**第一图把假设与验证对象连起来；每个约束通过独立消融证明必要性；集合差异可以产生下一步问题。**不可照搬：**我们的微型网络没有该文跨既有生理研究的验证，不能沿用其生物响应预测强度；不把所有好模型的意见差异包装成首次发现。

## C. Sourmpis et al.，eLife 2026

*Biologically informed cortical models predict optogenetic perturbations*，14:RP106827。[正式版本](https://doi.org/10.7554/eLife.106827.3)，[图表原页](https://elifesciences.org/articles/106827/figures)，[正式作者稿](https://pmc.ncbi.nlm.nih.gov/articles/PMC12810953/)。

**叙事链：**大规模记录可拟合→拟合像不像不足以验证机制→未见干预作为检验→生物约束/普通RNN及消融→模拟、行为效应与微刺激推演分层。

**已核主图：**1重建/检验框架；2模拟干预及消融；3真实行为效应；4微刺激与梯度；5假设闭环方案。**Table1确实存在**：方法为行，两个参考回路各分未干预/干预列，报trial-matching误差及区间。**Table2确实存在**：真实数据未干预trial-matching误差。其注释明确真实数据缺联合记录与刺激，不能计算同样的干预神经误差。

**可借鉴：**把拟合指标与用途指标并列，允许模型排名反转；表格明确不可测项。**不可照搬：**“拟合好≠干预好”和生物先验消融已做过；微刺激控制示范不能写成真实闭环结果。

## 对我们论文的具体启发

我们的主问题保持一句话：**固定结构和有限记录预算下，面向活动重建的观测设计，是否足以支持指定刺激响应的估计？**

三篇分别承担不同引用职责：A给出明确辨识设定和最强记录设计近邻；B说明结构、任务与生理验证不能互换；C要求用途相关的未见干预检验。不要把三篇都放在“已有研究很多，但仍然不足”的笼统句末。

### Introduction建议五段，每段只推进一步

1. **具体用途。** 神经接口的记录预算有限，而某些用途关心预先指定刺激对某读出的效应。此处不从AGI、算力或整个机器人产业起笔。
2. **已知进展。** 连接组约束减少结构不确定性，但生理参数仍未知；A已研究有限记录如何预测活动并选择记录位置。直接承认这层已解决。
3. **用途差别。** C证明未干预拟合与干预泛化可能不一致；B也保留任务相近但机制不同的模型解。由此提出问题，避免宣称这两篇“完全不考虑因果”。
4. **精确定义缺口。** 我们固定J、未知gain/bias、固定M/记录时长和刺激协议，仅改变观测设计的预测目标。一般目标导向设计已有方法谱系，应同时引用[Attia等原作](https://arxiv.org/abs/1802.06517)；不能宣称发明该思想。
5. **本文实际范围。** 给出两个设计目标、解释目标敏感方向与被动约束方向的关系，以独立非线性响应评估。只陈述已完成的推导/计算；未完成时用“we investigate/test”，不用“we establish/demonstrate”。

可直接作为段落定位的独立英文骨架（不是可替代证据的成稿）：

> Neural recording design is often evaluated by how well a model reconstructs activity outside the observed population. A neural interface may instead require an estimate of the response to a specified stimulation protocol. These objectives need not assign the same value to an observation. We ask when an activity-oriented recording set also supports this response estimate under a fixed measurement budget.

接下来的设定句应马上限定：known signed connectivity、uncertain neuronal gains and biases、fixed stimulation/readout、simulation-based evaluation。否则读者会自然理解成真实电极部署或跨动物验证。

### Related Work按“问题—区别”写，避免人物目录

**第一小节：Connectome-constrained inference under partial observation。** A是核心，B是具有真实神经响应比较的相关路线。说明固定突触权重与仅使用结构先验不是同一设定；我们不学J，也不声称复现真实神经活动。

**第二小节：Prediction under intervention。** C是核心。区分观测集合选择、刺激靶点选择、干预响应模型选择；我们的变量只有第一个。主动承认C已有拟合/干预分离这一科学警告，不能在贡献句里重述。

**第三小节：Goal-oriented experimental design。** 一般方法已成熟。我们的可能贡献须落在神经参数不确定性下的适用边界、排序代价和可实施准则的校准；若只是将现有公式换符号，无须包装成新方法。

每小节末只写一个具体区别：现有观测目标是什么；我们的目标是什么；保持哪些条件不变；用什么独立指标裁决。检索未见某组合，不足以写“first”。

## 我们真正需要的图与表：建议，非原文事实

| 载体 | 应承担的论证 | 最小内容 | 不应充当什么 |
|---|---|---|---|
| Fig1 | 读者看懂唯一问题 | 同J/同M/同数据预算，两类观测目标，一个封存的刺激响应评价 | 复杂机器人概念海报 |
| Fig2 | 命题可被推翻 | 简单分离案例＋应无差异的线性负对照 | 事后精选“最好看”的teacher |
| Fig3 | 不是个例 | 独立teachers/目标的活动误差与响应误差；配对效应与区间 | 只报选点所优化的代理风险 |
| Table1 | 防止比较条件漂移 | 方法/可用信息/观测预算/目标/是否oracle | 复制别人方法排名表但换数据 |
| Table2 | 展示用途相关比较 | 活动误差、响应误差、方向错误、校准；同一测试集合 | 把缺失真实验证填成0或“通过” |

可以学习eLife表格把不同评价条件并列的功能，但不必照搬其两参考回路的列结构；我们的配对单位是teacher/目标，而非它的动物或回路。表格若没有新的信息比较价值，不必为“像高水平论文”而强加。

## 写作前的两项核对

- **出处核对：**正式图号、真实Table1/2、模拟与真实检验粒度分别确认。Nature网页的“Supplementary Data”不能误称主文表；Sourmpis早稿与正式版不可随意混引。
- **主张核对：**每一句贡献能指向本研究一条推导或一项已运行结果。理论命题、小模型数值验证、经验结构模拟和真实动物验证是不同证据层；本文目前不能借参照论文的强证据替自己补层。
