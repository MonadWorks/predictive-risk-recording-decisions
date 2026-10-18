# v3 引用缺口审计：补足具体职责，不按篇数扩写

2026-10-16。正文基准为 `outputs/research_craft_v3/paper/论文研究稿_v3.md` 的15条参考文献版本。未改正文、摘要、统计或图。用户已认可正文的主要方向，本审计只建议局部衔接与必要应用锚点。

## 结论与优先顺序

引用的主要问题是**有些条目没有职责，而真实生物混合接口背景还略薄**，不是全文需要扩成综述。目前15条中[7,8,10,11]没有正文调用。核原文后，建议优先让[7]与[10]承担现有问题，保留[8]为相邻阅读、[11]为可选历史背景；不应四篇一起塞进I4。

新增文献候选严格限于下文5篇。推荐首选 **Kim 2023→Min 2025** 的实体系统谱系，以及 **Wang 2025** 的体外神经刺激／读出实例；如正文确需解释“神经信号的价值由系统下游决定”，再加 **Chen 2026**。**White 2016** 只在D4增加模型失配边界时采用，不必为了补足数量加入。实际可以只加3篇，不要求5篇全用。

## 一、现有四条 orphan references 的真实可用性

| 原条目 | 本轮核对的证据 | 能承担的已有段落职责 | 建议局部衔接／位置 | 不应声称与建议 |
|---|---|---|---|---|
| [7] Haber, Molnar & Motter, *State observation and sensor selection for nonlinear networks*, IEEE TCNS 5, 694–708（2018 issue），DOI [10.1109/TCNS.2017.2728201](https://doi.org/10.1109/TCNS.2017.2728201) | [作者arXiv](https://arxiv.org/abs/1706.05462)和[PMC索引](https://pmc.ncbi.nlm.nih.gov/articles/PMC6178986/)核到作者、摘要、研究对象：非线性动态下的状态估计／传感器选择；指出图论可观测性不等于实际估计能力。本轮没有复核所有定理。 | **I3结尾或I2→I3过渡最合适**：结构约束与有限动态观测之间还存在实际推断问题；也帮助解释R1“结构可达”的有限用途。 | 可用一句：`Sensor-selection studies in nonlinear networks likewise distinguish structural observability from the practical accuracy of state estimation [7].` | **建议保留并实际引用。** 它估计状态而非本项目的未知gain/bias与指定q，不能把我们的MAP选点算法称作其复现，也不能说该文证明本项目风险失配。 |
| [8] Pickard et al., *Dynamic sensor selection for biomarker discovery*, PNAS 122, e2501324122（2025），DOI [10.1073/pnas.2501324122](https://doi.org/10.1073/pnas.2501324122) | [PubMed](https://pubmed.ncbi.nlm.nih.gov/41055977/)与[原论文索引](https://pmc.ncbi.nlm.nih.gov/articles/PMC12541339/)可核：由时间序列转录组学习线性／时变模型，再动态选取生物标志物；作者代码明确。不把摘要当完整方法复算。 | 目前I1–I5／D1–D5没有必须由它支撑的独特主张；最多是在“更广生物系统有动态测量选择”时作一条旁证。 | 如不增加该主张，正文不插句。若将来研究时间变化选点，可另立真实研究问题，而不是在现稿借“biomarker”扩应用。 | **本稿建议移出参考文献，留阅读清单。** 本项目固定记录集合、已知数值J，没有转录组数据或学习A(t)，不能称已有生物信息学验证。 |
| [10] Kreutz, Raue & Timmer, *Likelihood based observability analysis and confidence intervals for predictions of dynamic models*, BMC Syst Biol 6:120（2012），DOI [10.1186/1752-0509-6-120](https://doi.org/10.1186/1752-0509-6-120) | [出版社开放全文](https://link.springer.com/article/10.1186/1752-0509-6-120)可读，核Background、prediction profile likelihood、validation profile likelihood与示例。区分参数不确定性、模型预测、带噪验证。 | **I3或D3**：参数拟合不是最终推断对象；预测区间需要针对预测本身评估。它给D3一条比泛泛“参数不确定很复杂”更具体的系统生物学谱系。 | D3可补：`Prediction-profile approaches in dynamic models assess uncertainty in the predicted quantity directly, rather than relying only on local parameter uncertainty [10].` | **建议保留并引用。** 未实现profile likelihood，不能暗示我们的局部MAP区间有该文的覆盖保证。该文不能直接证明ensemble不优。 |
| [11] Apgar, Witmer, White & Tidor, *Sloppy Models, Parameter Uncertainty, and the Role of Experimental Design*, Mol BioSyst 6, 1890–1900（2010），DOI [10.1039/b918098b](https://doi.org/10.1039/b918098b) | [原作者稿索引](https://pmc.ncbi.nlm.nih.gov/articles/PMC3505121/)可读Summary、Introduction与互补实验几何例。研究固定信号模型下通过互补扰动改善参数标定。 | 可以给I4中“设计改变参数信息”的历史背景，但[5]已直接支撑我们的目标导向准则，现稿不必为此另开sloppiness支线。 | 若保留，仅一句区分：`Complementary perturbations can improve parameter calibration in signalling models [11]; here the stimulation and measurement budget are fixed, and the evaluation target is response error.` | **可选，非必需。** 不能把它当成风险→实际q误差一致性的证明；不能把sloppiness等同不可辨识，也不能忽略数据量／实验数量随设计变化。现稿优先删除未调用条目。 |

这些是现有参考文献的再分工，不是五篇“新引文”配额的一部分。

## 二、五篇精确的新近邻：每篇只承担有限主张

### A. Kim 2023：直接肌肉驱动的实体接口基点

- **书目信息：** Yongdeok Kim et al., *Remote control of muscle-driven miniature robots with battery-free wireless optoelectronics*. Science Robotics 8, eadd1053 (2023)。[DOI](https://doi.org/10.1126/scirobotics.add1053)、[作者机构原版PDF](https://rogersgroup.northwestern.edu/files/2023/scirobotbiobot.pdf)、[PubMed作者信息](https://pubmed.ncbi.nlm.nih.gov/36652505/)。
- **可访问深度：** 作者机构11页PDF，正文与图注可读；核Fig.7与Discussion。机构版末尾含补充材料入口，不等于本轮审计全部补充实验。
- **科学主张／证据：** 无电池无线光电子与光遗传肌肉组织构成能受远程刺激的实体小机器人；图中机械轨迹和独立刺激操作构成其实体响应证据。Discussion将进一步传感／自主闭环列为可发展能力。
- **建议位置：** I1首段增加一个短应用锚点，与Min放同一句，而非新增综述段：`Biohybrid robots can translate optical inputs into motion through either directly stimulated muscle or an intervening neuromuscular interface [Kim; Min].`
- **适用边界／不应声称：** Kim系统的输入—输出不是我们的神经q，也没有评价本项目记录选择；不能称其已完成自主神经反馈闭环。用于说明为什么“指定输入对应的功能输出”值得区分，不用于证明我们的仿真具有机器人效益。
- **谱系位置：** Kim→Min 是确有共同团队与前作引用的工程推进；它与Beiran的连接约束推断是**问题层桥接**，不是共同算法来源。

### B. Min 2025：神经—肌肉转换层，以及精确控制尚未完成的边界

- **书目信息：** Hyeji Min, Yue Wang, Jiaojiao Wang, Xiuyuan Li et al., *Optogenetic neuromuscular actuation of a miniature electronic biohybrid robot*. Science Robotics 10, eadu5830 (2025)。[DOI](https://doi.org/10.1126/scirobotics.adu5830)、[作者机构14页PDF](https://rogersgroup.northwestern.edu/files/2025/scirobnmj.pdf)。
- **可访问深度：** 原版PDF全文可读；核NMJ构建、Fig.6、Discussion第10页。没有重新计算RNA或机械原始数据。
- **科学主张／证据：** 选择性刺激神经组织，经NMJ调制肌肉收缩和爬行；Fig.6展示跨样本及时间响应。作者明确限定为功能调制，仍受自发抽动、延迟及非均匀性限制。
- **建议位置：** I1与Kim共同支撑上句；D4最后一句可具体化而无需扩写：`Relating a predicted neural response to mechanical output requires an additional neuromuscular validation layer, as illustrated by current biohybrid crawlers [Min].`
- **适用边界／不应声称：** 神经rate积分不等于收缩力、PSD峰或运动速度。本项目没有NMJ模型与机械测量，不能说直接优化该机器人，更不能将“调制”写成确定的精确控制。
- **谱系位置：** 说明在Beiran→本项目的计算链之后，还缺少怎样的物理转换验证；也与Sourmpis的目的匹配干预验证原则相容，但两者提供的实验对象不同。

### C. Wang 2025：体外网络上可明确说明“写入—读出”的近邻（刘连庆共同作者）

- **完整作者／题名：** Xingchen Wang, Bo Lv, Fengzhen Tang, Yukai Wang, Bin Liu, Lianqing Liu. *Biomimetic Visual Information Spatiotemporal Encoding Method for In Vitro Biological Neural Networks*. Biomimetics 10(6):359 (2025)。[DOI](https://doi.org/10.3390/biomimetics10060359)、[PubMed作者及摘要](https://pubmed.ncbi.nlm.nih.gov/40558328/)、[作者稿入口](https://pmc.ncbi.nlm.nih.gov/articles/PMC12190828/)。
- **可访问深度：** PubMed元数据／摘要完整；可搜索原文Introduction、Conclusions。MDPI本轮429，PMC直接页验证码，未绕过；因此不声称本轮逐图／全文视觉精读。
- **科学主张／证据：** 图像经卷积、延迟、对齐、压缩形成电刺激序列，HD-MEA刺激与记录培养网络，再用logistic regression解码。实际任务是刺激编码与图像识别，不是记录预算优化。
- **建议位置：** I1末句之后、I2模型谱系之前，独立一句足够：`In cultured neural networks, spatiotemporally encoded electrical inputs and HD-MEA recordings have been used for image-evoked response decoding [Wang].` 下一句应收回本文：“Here, we abstract this input–response interface to study a prescribed response under limited recording.”后句是我们的定位，不是该文的发现。
- **适用边界／不应声称：** 不能把相关性推断的functional connectivity称作我们已知数值J；不能声称复现培养、学习、视觉或真实机器人行为；不能称其支持有限记录设计优于全活动设计。
- **与会议关系：** 官方[委员会](https://icbr2026.org/Committee.html)列Lianqing Liu为General Co-Chair，[嘉宾页](https://icbr2026.org/InvitedSpeakers.html)列其生命—非生命融合报告。这个关系只解释为何值得核读，**不进入科学论证，也不提供会议认可背书**。论文署名应为Wang et al.，不能写成刘连庆独著。

### D. Chen 2026：神经读出的用途由下游控制任务定义（刘连庆共同通讯，可选第二篇）

- **作者核对：** Zirui Chen, Lin Zhang, Guiyong Chen等；14位作者中包括Lianqing Liu及Wenxue Wang；Lianqing Liu与Mingjun Zhang、Wenxue Wang列通讯。*Cyborg-swarm cooperation and game via affective-based brain–machine interface*. National Science Review 13(13), nwag313 (2026)。[DOI](https://doi.org/10.1093/nsr/nwag313)、[出版社全文](https://academic.oup.com/nsr/article/13/13/nwag313/8697610)。
- **可访问深度：** 正常官方链接自动转向出版社minimal页面后全文可读；核作者职责、Abstract、BMI小节、Fig.1/2/4图注、仿真与真实神经输入的区分、数据可用性；未跑其RL或原始记录。
- **科学主张／证据：** BLA多通道LFP的β频带特征被解码为状态触发，进而切换机器人协作控制模式。作者明确区分：机器人策略在仿真中训练，真实动物情绪信号在实体实验进入控制环。
- **建议位置：** 若I1需要“整个状态不是系统目标”的另一实例，可用：`Neural readouts can also serve a task-specific control role: decoded affect-related signals have been used to trigger robotic mode switching [Chen].` 不需要和Wang两篇分别占一整段。若I1已有Kim/Min/Wang而密度过高，这篇可以不加。
- **适用边界／不应声称：** LFP状态检测不是rate模型的刺激响应估计；未证明我们的q是情绪、意图或可用触发。不能用其真实闭环替本项目补足物理闭环，不能声称我们的风险方法可提高其安全性或控制表现。也不要转述该文宽泛的“范式转移”口号。
- **谱系位置：** 属于刘连庆／王文学应用侧谱系的另一分支，而非Beiran或Gerstner方法直接后续。它仅支持任务定义的现实意义。

### E. White 2016：设计与模型失配的旧问题，限定我们的外推（可选第五篇）

- **书目信息：** Andrew White, Malachi Tolman, Howard D. Thames, Hubert Rodney Withers, Kathy A. Mason, Mark K. Transtrum. *The Limitations of Model-Based Experimental Design and Parameter Estimation in Sloppy Systems*. PLoS Comput Biol 12(12):e1005227 (2016)。[出版社开放全文](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005227)。
- **可访问深度：** 全文可读；核Abstract、Author Summary、Introduction对sloppiness与identifiability的区分、EGFR模型替代实验及Fig.3/4图注。
- **科学主张／证据：** 更丰富的实验可以暴露近似模型遗漏的机制；参数更受约束并不自动改善模型预测。该文在更详细的生成模型与近似拟合模型间制造结构差异，检查系统误差。
- **建议位置：** D4在“correct observation equation”后加一句：`Optimal-design studies in systems biology have also shown that more informative experiments can expose model discrepancy [White]; structural misspecification is not tested here.`
- **适用边界／不应声称：** 我们的隐bias shift是同一模型内未公开的参数分布变化，**不是该文的结构model discrepancy**；不能用该文解释我们已经找到的唯一失败机制，也不能说本研究新发现了“设计不总改善预测”。
- **谱系位置：** 与Apgar [11]形成明确的参数识别／模型有效性讨论；帮助区分本项目的局部近似问题与更广结构失配问题，而不是另立一个未做的sloppiness研究。

## 三、与三条科学谱系及Kim→Min的衔接

| 谱系 | 当前正文应承担的核心 | 本轮可以补足的地方 | 不应混成什么 |
|---|---|---|---|
| Beiran／Litwin-Kumar，加Lappalainen实例 | 连接约束、有限记录、未知生理属性、功能响应预测 | [7]具体限定“图结构信息≠实际估计精度” | 不能把光驱肌肉或HD-MEA的功能连接当成同一种已知J |
| Sourmpis／Gerstner的目的匹配扰动验证 | 应测将要使用的扰动结果；活动拟合不替代目标验证 | [10]补“预测泛函自身的不确定性”而非只看参数 | 不能说本文已用真实联合刺激／记录做外部验证 |
| Liu／Wang的生命—非生命接口 | 刺激编码、神经读出和下游控制有具体任务 | Wang提供体外写入／读出，Chen提供下游触发使用 | 不声称同算法、合作关系、会议背书或实际系统改进 |
| Kim 2023→Min 2025工程链 | 从直接肌肉光刺激进入NMJ调制与物理输出 | 在I1给真实应用锚点，在D4说明还缺哪层验证 | 不把我们的计算闭合论证误写成自主物理反馈控制 |

这里的关系是可追溯的“问题来自哪里、方法来自哪里、证据还缺哪里”，不是五篇论文构成一个连续技术栈。

## 四、最小局部修改包与数量判断

1. **I1只加两句以内的应用锚点。** Kim／Min用一共同句；Wang一短句。这样conference scope有实际出处，又不改变“有限记录支持指定预测”的中心。
2. **I3或D3各补一条已有引用职责。** [7]表明结构可达不是完整估计依据；[10]表明预测量本身需要不确定性评价。它们不用重新写成两个背景段。
3. **D4按需要回扣Min，或再加White一句。** 回扣q到机械量的缺层，White仅扩结构失配边界。不能在本研究未测的范围增加结论。
4. **Chen可替换／压缩应用例，不要求与Wang双双出现。** 如果应用句已能说明实际任务，就不为主办关系重复同一论点。
5. **删除不调用的[8]／[11]，或移入独立阅读文档。** 参考文献不是全部调研库存。若採用5个候选并复用[7]/[10]、移除另外2个，将约18条；若只采用3个则约16条。这个数量只是结果，不是目标。

当前稿不缺每个Results段后再加几篇别人文章，而是需要让应用背景与方法边界有更明确的近邻。新增引文应优先放I1／I3／D3／D4；自身结果仍由冻结数据、方法与图表负责。摘要不改，正文不重写，新方法宣言不增加。
