# 具体人物谱系与主文章承接层：2026-10-16更新

只读查新；未改outputs或先导代码，未运行下述计算。这里的“谱系”指明确的研究方法/科学问题传承，不意味着我们与作者有合作、导师关系，或他们参与ICBR。

## 1. Beiran / Litwin-Kumar：从结构—动力学关系，到有限记录下的预测

| 原作与人物 | 原作实际操作 | 我们可承接的一层 |
|---|---|---|
| Beiran、Dubreuil、Valente、Mastrogiuseppe、Ostojic，*Shaping Dynamics With Multiple Populations in Low-Rank Recurrent Networks*，Neural Computation 2021，[作者原稿](https://arxiv.org/abs/2007.02062)，[DOI](https://doi.org/10.1162/neco_a_01381) | 将连接秩与群体统计结构分开，推导低维集体动力学；群体数改变可实现的动力学形状 | 从“网络结构指标”转向明确动力学映射和参数方向；不能把低秩本身当新模型 |
| Zarin、Mark、Cardona、Litwin-Kumar、Doe，*A multilayer circuit architecture for the generation of distinct locomotor behaviors in Drosophila*，eLife 2019，[原文](https://doi.org/10.7554/eLife.51781)，[Litwin-Kumar实验室原作/代码目录](https://lk.zuckermaninstitute.columbia.edu/) | 经验幼虫运动网络连接与循环网络建模联系行为；不是任意随机图挂一个果蝇名字 | 后续用一张真实来源的固定结构作模型边界验证；结构来源不等于功能响应实测真值 |
| Beiran & Litwin-Kumar，*Prediction of neural activity in connectome-constrained recurrent networks*，Nature Neuroscience 2025，[原文](https://doi.org/10.1038/s41593-025-02080-4)，[作者代码](https://github.com/emebeiran/connconstr) | 固定J、未知神经元增益/偏置的teacher–student；有限记录、未记录活动、stiff/sloppy方向、模型失配及正式Fig8记录位置选择 | 严格继承其“已知结构＋生理参数不确定”的辨识设定，只改变最终需要预测的功能量；不重复“记录越多越好/最优节点/加噪” |

[Beiran本人研究说明](https://mbeiran.wordpress.com/research/)明确其博士阶段在Ostojic指导下研究低秩/群体动力学，之后在Litwin-Kumar组研究连接组如何约束功能。该网页个别论文题名仍是旧稿，不应替代正式出版物元数据。

**我们与会议的距离：**未发现Beiran或Litwin-Kumar列ICBR委员会/报告人。关系是问题上的：有限神经记录能否给生物接口提供可信功能预测。对主办方而言是计算支撑，尚无活体机器人证据。

## 2. Gerstner / Bellec / Sourmpis：先拟合神经—行为变异，再接受干预检验

| 原作与人物 | 原作实际操作 | 我们可承接的一层 |
|---|---|---|
| Sourmpis、Petersen、Gerstner、Bellec，*Trial matching: capturing variability with data-constrained spiking neural networks*，NeurIPS 2023，[会议原文](https://papers.neurips.cc/paper_files/paper/2023/hash/ec702dd6e83b2113a43614685a7e2ac6-Abstract-Conference.html) | 通过最优传输式trial matching约束模拟与记录试次分布，用脉冲网络同时解释六脑区活动与下颌运动变异 | 借用“评价不能只有平均PSTH/MSE”的科学标准；不必重建其大RSNN，更不能假称小率网络重现所有试次统计 |
| Sourmpis、Petersen、Gerstner、Bellec，*Biologically informed cortical models predict optogenetic perturbations*，eLife 2026，[正式DOI](https://doi.org/10.7554/eLife.106827.3)，[原文图表](https://elifesciences.org/articles/106827/figures) | 比较普通RNN和生物约束RNN对未见干预的泛化；拆解Dale法则、局部抑制、spiking等先验；真实检验使用区域抑制后的行为效应，细胞微刺激梯度示范在模型中进行 | 继承“模型的用途决定验证对象”：本题验证指定刺激响应，而非拿被动拟合充当功能保证；新增变量是**观测设计目标**，不是又比一次bioRNN vs sigmoid RNN |

**决定性更正：**该eLife正式Figures页Table2明确写：真实数据缺少joint recordings and stimulation，因此不能在干预试次上算与模拟相同的trial-matching指标。此前我们把这件事列为“待核风险”，现在已有作者明文证据。Esmaeili/Zenodo4720013不能承诺用于同单元刺激响应的外部验证；最多是群体/区域行为效应层的检验，而且缺少同脑实测J。不要为三层叙事硬加进去。

**我们与会议的距离：**未发现Gerstner、Bellec或Sourmpis为ICBR已公布人员。联系是读写接口方法上的，非组织联系；它们为研究设计设定标准，不提供接收背书。

## 3. 刘连庆 / 鲍进：真实生物接口和环路干预，是应用问题来源

该线按应用端合并，以下只列三项明确原作；不把讲座摘要冒充已完成实验。

| 原作与具体人物 | 实际研究操作 | 我们承接与不能承接的部分 |
|---|---|---|
| Wang、Lv、Tang、Wang、Liu、**Lianqing Liu**，*Biomimetic Visual Information Spatiotemporal Encoding Method for In Vitro Biological Neural Networks*，Biomimetics 2025，[原文](https://doi.org/10.3390/biomimetics10060359)，[作者代码入口](https://github.com/wangxingchen231/Biomimetic-Visual-Information-Spatiotemporal-Encoding-Method) | 图像转为时空电刺激；体外网络在HD-MEA上接受刺激并记录响应；比较训练前后识别/功能网络指标 | 明确接口“写什么、读哪里”的问题背景；本题只研究有限读出配置，不声称复现其培养/学习/图像识别。刘连庆列概念、监督、项目与资助贡献，不能说他一人完成全部实验 |
| Chen等、**Lianqing Liu**、Wenxue Wang，*Cyborg-swarm cooperation and game via affective-based brain–machine interface*，National Science Review 2026，[原文DOI](https://doi.org/10.1093/nsr/nwag313)，[PubMed作者与摘要](https://pubmed.ncbi.nlm.nih.gov/42368477/) | 小鼠杏仁核LFP频带特征形成恐惧状态触发信号，影响机器人团队控制模式；结合无线BMI和多智能体策略 | 说明神经信息的价值由控制端需求决定，不要求重建所有脑活动；但本题不研究情绪、LFP解码、群体策略或真实机器人，因此仅作动机，不能称方法直接改进此系统 |
| Chen、Hong等，**Jin Bao**、Ji Dai、Zhonghua Lu共同通讯，*Circuit-specific gene therapy reverses core symptoms in a primate Parkinson’s disease model*，Cell 2023，[原文DOI](https://doi.org/10.1016/j.cell.2023.10.004)，[中科院独立说明](https://www.cas.cn/syky/202311/t20231103_4984114.shtml) | 用特定病毒/启动子/化学遗传元件靶向基底节通路，在灵长类模型评估运动表型 | 提供“指定通路响应比全局活动相似更贴功能目标”的实例；与我们的率网络/观测设计距离仍很大，不是仿真可证明的疗法、也不是电极选点论文 |

**与ICBR的真实连接：**[官网委员会](https://icbr2026.org/Committee.html)列刘连庆为大会共同主席；[嘉宾页](https://icbr2026.org/InvitedSpeakers.html)列其生命—非生命融合报告。鲍进是用户所附宣传图公布报告人，题为生物脑网络架构与灵活行为；她的研究方向可由[国科大主页](https://people.ucas.ac.cn/~Jin_Bao_Lab)独立核实。当前可抓官网嘉宾正文未列鲍进，不升级为已确认最终排程。

**推导应写成：**上述团队面对实际活体读写和功能调控→我们的一个前置计算问题是有限观测如何配置以可靠估计预定响应。**不应写成：**我们继承了其生物实验或直接满足他们的审稿要求。

## 4. 主题的近邻是否已经直接做过

窄题设定：已知固定有符号J；未知非线性gain/bias；固定M与观测时长；只比较activity-oriented与goal-response-oriented记录设计。不是学J，不是选最优刺激，不是无限预算模型辨识。

**本轮未检得把这五项同时固定为主问题的直接原作，但这不是新颖性证明。** 已有近邻覆盖很深：

1. **Beiran2025**已最优选记录点，且做增益/偏置不确定性；我们只能研究目标改变后的记录设计代价，不能宣称提出有限记录选点。
2. **Sourmpis2026**已比较被动拟合与干预泛化，并演示微刺激功能效应；“相关不等于因果”不足以作为贡献。
3. **Attia等2018 GOODE**，[原作](https://arxiv.org/abs/1802.06517)，已建立以最终功能量不确定性而非全参数误差选择实验。用Gq Cθ Gqᵀ选点是现有方法应用；我们的潜在论文价值只可能是神经设定里的可预测分离条件、实测regret和适用边界。
4. **Ogino等《Designing optimal perturbation inputs for system identification in neuroscience》**，[原作](https://doi.org/10.7554/eLife.110030)，已用控制理论设计刺激来显露被动隐藏动力学；需要明示本题固定刺激，仅选记录，避免做成同一个输入设计问题。

**判定：**目前较像“将已有目标导向设计用于一个严格定义的神经辨识问题，检验原活动重建选点何时足够”的机制/边界研究，而不是方法发明。若结果只是目标导向准则在自己的局部二次指标上更优，论文本身不成立；必须用独立参数/teacher、实际非线性响应、预先固定的刺激与读出来检验，且保证原活动导向基线得到公平实现。

## 5. Mac 1–2天限制下如何守住一篇文章的核心

这里最多能承诺**先导计算规模设计**，不能把1–2天墙钟当成熟论文保证：

- 从N约8–16、M约2–4、一个固定J家族和一个响应q起步；使用率动力学、局部后验/灵敏度＋真实非线性rollout。不要同时上spiking、大连接组、多脑区和机器人身体。
- 首批只检验一个命题：在有限观测而参数响应敏感方向未被覆盖时，是否出现活动误差相近而q误差不同；实际可实施选点能否降低q误差。不要先承诺一定出现。
- 至少包含线性已知动力学/仅未知bias的无差异负对照、匹配随机集合、原活动导向集合、目标打乱集合；将oracle与估计选点隔离。
- 在真实非线性held-out响应上评价，不能仅用选点所优化的Gq Cθ Gqᵀ评价自己；不选事后最有利靶点。
- 一篇初稿可以先完整定义问题、推导局部准则/反例与明确限制；只有先导计算实际通过后，结果段才填写数字。经验连接结构若超时可后补，但不能先写已验证。Esmaeili外部层本轮应收回，不是该小论文必须承担的第三任务。

**最凝练的承接句：**Beiran告诉我们结构与有限活动记录何时能约束动力学；Bellec/Sourmpis要求模型接受功能干预检验；刘连庆/鲍进团队展示实际生物接口与特定环路功能的重要性。我们只检查这两种要求之间一个具体缺口：**活动重建选点能否以同一预算支持预定刺激响应估计，以及何时值得为这个目标改选记录位置。**
