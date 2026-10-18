# ICBR 2026：历史稿件核实与代表研究地图

检索日期：2026-10-16。此文件只做公开资料研究，无投稿、注册、联系。标题、作者关联、年份尽量以原期刊/作者所属大学为准；方法与实验层级为摘要级核实，未完整审计原始数据。

## 一、先纠正“往届稿件”的问题

官网首页明确称 **2026 First International Conference on Biohybrid Robotics**，并称 ICBR 2026 为应生物工程与机器人融合这一转变而设立。因此，不能把别的 ICBR 会议论文当作本会往届录用样本，也不能据此推算录用率或审稿水平。[会议首页](https://icbr2026.org/)

以 “ICBR biohybrid robotics 2025 proceedings”等组合检索，未查到属于同一会议系列的往届论文集。这个“未发现”是检索结论，并非数据库全覆盖证明。2025 的 ICBR 大量搜索结果是 **International Congress for Battery Recycling**（电池回收大会）；主办方 ICM 的历史页明确其为第30届，和本次机器人会议无关。[ICM 2025历史页](https://icm.ch/past-events/30th-international-congress-for-battery-recycling-icbr-2025)

还发现检索索引中 **www.icbr2026.org** 的首页、Spe.html、Reg.html 混入 **ACFPE 2026 电力能源会议** 内容，而用户提供的裸域 **icbr2026.org** 正常返回生物混合机器人会议。当前无法仅据索引判断是主机配置、历史模板还是索引缓存问题。凡费用、出版、往届信息，都必须逐页确认内容及会议全称，不可仅凭域名。示例：[错误语境 www 首页](https://www.icbr2026.org/)、[www 费用页](https://www.icbr2026.org/Reg.html)。

所以本次“过往稿件”应转换为三类材料：① 2026 已公布的邀请报告和专题报告，能说明组织者当前想讨论什么；② 邀请嘉宾及核心团队的真实既有研究，能说明他们熟悉何种问题与证据，但**不是本会录用门槛**；③相邻成熟会议的真实接收题材，用于判断可实现的研究粒度。

**出版性质必须先说清：** 官网CFP明确：提交的是研究摘要，**不做同行评议，不被EI收录**，接收后需到场报告，口头或海报由组织者决定；Tutorials/Workshops的报告也不同行评议且不入论文集。[CFP](https://icbr2026.org/CFP.html)。因此，它可以是交流、找合作、展示初步结果的平台，不能当作正式同行评议论文发表。以下顶刊文章是领域路线图，不应制造“本会达到顶刊标准才可投”的印象。

## 二、16篇代表阅读材料（15篇研究 + 1篇综述）

分类含义：**BH** = 工程系统直接利用活细胞、活组织、生物体或功能性生物成分；**BI** = 仿生/生物启发，机器人本体不因此含活成分；**EN** = 支撑技术，可能服务 BH，但该论文本身不构成 BH。证据分“计算”“体外/台架”“动物”“人体试用”；层级不等于质量分数。

| # | 准确标题、年份与来源 | 与本会人物关系 / 分类 | 方法、已验证内容与边界 | 软件/AI可切入处（研究建议，非原论文主张） |
|---|---|---|---|---|
| 1 | **Regulation of C2C12 Differentiation and Control of the Beating Dynamics of Contractile Cells for a Muscle-Driven Biosyncretic Crawler by Electrical Stimulation** (2018), Soft Robotics. [DOI](https://doi.org/10.1089/soro.2018.0017) / [PubMed](https://pubmed.ncbi.nlm.nih.gov/30277855/) | 刘连庆、张闯、王文学等；BH | 环形分布多电极调节C2C12肌细胞分化与肌管驱动爬行；体外活组织+机器人实验，非临床。 | 自动识别收缩/疲劳、刺激参数辨识、个体差异鲁棒控制。 |
| 2 | **A Manta Ray-Inspired Biosyncretic Robot with Stable Controllability by Dynamic Electric Stimulation** (2022), Cyborg and Bionic Systems. [DOI](https://doi.org/10.34133/2022/9891380) / [原文全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC11781248/) | 刘连庆、张闯等；BH，外形又是BI | 培养骨骼肌组织驱动鳐鱼形游泳器，8电极动态调整电场方向，使刺激方向与肌肉轴线保持平行；体外游泳与仿真验证。不能把“仿鳐外形”与“活肌肉驱动”混为一谈。 | 视觉姿态追踪→实时刺激闭环；比较固定电极、动态控制、学习控制，计入组织存活和刺激损伤。 |
| 3 | **Modular Living Muscle-Based Biomimetic Actuators for Biosyncretic Robots** (2025), SmartBot. [原文](https://onlinelibrary.wiley.com/doi/10.1002/smb2.12012) | 刘连庆、张闯、杨连超等；BH | 结构优化的模块化培养骨骼肌；摘要报告最大收缩力2.92±0.07mN、无负载约28%应变、10Hz单抽搐响应；组装多种肌肉布局与爬行/游动机器人。体外原型。 | 利用结构参数、培养条件、收缩力做可复现实验数据库；形态优化/可解释代理模型。 |
| 4 | **Explosive sensing with insect-based biorobots** (2020), Biosensors and Bioelectronics: X. [DOI](https://doi.org/10.1016/j.biosx.2020.100050) / [原论文PDF（大学托管）](https://www.pos.entomologia.ufv.br/wp-content/uploads/2020/12/artigo-Pedro-Nascimento.pdf) | Barani Raman；BH | 读取蝗虫嗅觉神经群体活动，以多变量响应区分爆炸物气味；实验室生物传感概念验证，不等于野外排爆系统。 | 神经信号解码、跨个体迁移、漂移、少样本校准、开放集拒识。要按昆虫/时间划分训练测试，避免重复试次泄漏。 |
| 5 | **Structure-Preserving Numerical Integrators for Hodgkin--Huxley-Type Systems** (2020), SIAM Journal on Scientific Computing. [期刊原文](https://epubs.siam.org/doi/abs/10.1137/18M123390X) / [作者预印本](https://arxiv.org/abs/1811.00173) | Raman共同作者；EN，计算神经科学 | 研究分裂与组合积分方法，比较较大时间步下极限环及神经脉冲的保持；纯数学/数值证据，没有生物机器人实验。 | 快速且保动力学的神经控制器仿真、数值误差基准；说明纯算法路线存在，但必须有对应领域问题。 |
| 6 | **Cellular Cargo Delivery: Toward Assisted Fertilization by Sperm-Carrying Micromotors** (2016期刊卷；2015在线), Nano Letters. [ACS原文](https://pubs.acs.org/doi/10.1021/acs.nanolett.5b04221) | Oliver G. Schmidt；BH | 金属镀层聚合物微螺旋用磁场推动活动障碍精子；在流道中捕获、运输、释放活精子。论文自己指出成功受精仍有挑战，不能写成已临床助孕。 | 单细胞跟踪、捕获/释放规划、轨迹与细胞完整性的联合评价。 |
| 7 | **Si chiplet-controlled 3D modular microrobots with smart communication in natural aqueous environments** (2025), Science Robotics. [DOI](https://doi.org/10.1126/scirobotics.adu6007) / [PubMed](https://pubmed.ncbi.nlm.nih.gov/40834063/) | Schmidt共同作者；BI/EN，**不是活细胞BH** | 自折叠/卷曲膜+硅chiplet，太阳能采集、光通信、浮力/电解驱动、模块对接；水中实物实验。模仿细胞模块化，材料系统仍是非生物。 | 低功耗程序、模块协同、通信协议与容错、任务级仿真。注意不能把微处理器“智能”说成自主学习。 |
| 8 | **Endoscopy-assisted magnetic navigation of biohybrid soft microrobots with rapid endoluminal delivery and imaging** (2021), Science Robotics. [DOI](https://doi.org/10.1126/scirobotics.abd2813) / [大学解读](https://www.cpr.cuhk.edu.hk/en/press/cuhk-develops-biohybrid-soft-microrobots-with-a-rapid-endoluminal-delivery-strategy-for-gastrointestinal-gi-diseases/) | 张立；BH | 磁性干细胞球微机器人+内镜辅助磁驱动及双成像平台EMADIS；利用软组织适应狭窄环境。原型和生物/动物场景验证，非已完成临床疗效试验。 | 医学影像跟踪、多模态定位、导航控制、手动/自动对照。 |
| 9 | **Magnetically driven biohybrid blood hydrogel fibres for personalized intracranial tumour therapy under fluoroscopic tracking** (2025), Nature Biomedical Engineering. [DOI](https://doi.org/10.1038/s41551-025-01382-z) / [中大研究条目](https://research.cuhk.edu.hk/en/publications/magnetically-driven-biohybrid-blood-hydrogel-fibres-for-personali/) | 张立、徐天添、王奔等；BH（血液衍生生物材料，不等于活体自主驱动） | 用自身血液与少量磁粒制纤维，磁控、X线透视跟踪、可降解与按需药物释放；摘要明确有小型猪颅内肿瘤给药验证。大动物证据仍不等于临床有效。 | X线低对比跟踪、剂量/路径优化、患者特异几何建模、不确定性与失败监测。 |
| 10 | **Autonomous environment-adaptive microrobot swarm navigation enabled by deep learning-based real-time distribution planning** (2022), Nature Machine Intelligence. [原文](https://www.nature.com/articles/s42256-022-00482-8) / [作者代码](https://github.com/lidongYang22/Autonomous-microrobot-swarm-navigation) | 张立、窦琪、杨立栋等；EN，磁性纳米颗粒群本身非活体BH | DNN为群体分布提供实时规划，定义不同自主级别，在通道/障碍物环境中做真实磁性粒子群导航、递送及搬运；补充材料含超声/X线验证。其“自主”来自系统闭环，不是只离线预测一个标签。 | 最直接的软件切口：代码复现、分布外几何、动态障碍、不同群体尺寸、鲁棒/安全策略及统计基准。需解释如何迁移至真正BH。 |
| 11 | **A soft neuroprosthetic hand providing simultaneous myoelectric control and tactile feedback** (2021在线；2023卷期), Nature Biomedical Engineering. [DOI](https://doi.org/10.1038/s41551-021-00767-0) / [PubMed](https://pubmed.ncbi.nlm.nih.gov/34400808/) | 谷国迎、盛鑫军等；EN/人机生物电子接口，不是活肌肉驱动手 | 柔软充气手结合肌电控制与触觉反馈；原文摘要报告截肢者试用及一名个体的闭环感觉。人体可行性不能替代大规模临床比较。 | 肌电解码、校准负担、触觉反馈编码、日常任务迁移；需有真实参与者和伦理/数据权限。 |
| 12 | **A high-dexterity soft neuroprosthetic hand for daily activities** (2026), Nature Communications. [原文](https://www.nature.com/articles/s41467-026-75105-6) | 谷国迎；EN/生物电子接口 | 11主动自由度软手，2通道肌电接口；论文页面介绍4名截肢者及日常操作/标准测试。不是传统狭义活细胞BH，但与大会软体+医用接口方向相连。 | 解码及任务选择、少通道控制效率、跨用户泛化、以日常功能量表评价而非只报分类准确率。 |
| 13 | **Analytical Modeling and Inverse Design of Centimeter-Scale Hard-Magnetic Soft Robots** (2023在线；2024卷期), IEEE Transactions on Automation Science and Engineering. [DOI](https://doi.org/10.1109/TASE.2023.3313395) / [作者PDF](https://softrobotics.sjtu.edu.cn/pdf/Jinqiang_TASE_2023.pdf) | 谷国迎团队；BI/EN | 考虑磁化分布、重力和大变形的解析模型及逆设计，制造具目标抓握姿态的硬磁软机器人。模型+实物；无活生物成分。 | 可微优化、材料参数辨识、实验误差/外推评价、形态与控制联合设计。 |
| 14 | **A material point-based simulation method for soft robots with free boundary interactions** (2024在线；2025卷期), Robotica. [DOI](https://doi.org/10.1017/S0263574724002066) / [出版方PDF](https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/CC5FAD852CA62C57B1A88AD992383B82/S0263574724002066a.pdf/material_pointbased_simulation_method_for_soft_robots_with_free_boundary_interactions.pdf) | 夏泽洋、沈杰、张蓓佳等；EN | 物质点法+自动微分+隐式积分处理软体和流体的大变形/不确定接触，普通气动软指两组实验验证；不是纯动画仿真，也不是生物混合机器人实验。 | 对AI/软件团队最相关：可微仿真、数据同化、参数辨识、模型降阶、孪生与控制耦合。 |
| 15 | **Fully automated cardiac MRI segmentation using dilated residual network** (2022在线；2023卷期), Medical Physics. [原文](https://aapm.onlinelibrary.wiley.com/doi/10.1002/mp.16108) | 夏泽洋、熊璟等；EN，医学影像 | 扩张残差网络改善U-Net瓶颈特征；以ACDC心脏MRI评价心室/心肌分割。医学影像数据基准不直接证明心脏辅助机器人闭环价值。 | 患者特异心室模型、时间一致性、功能参数、分割不确定性向器械设计/控制传播。单做通用分割容易偏离本会主题。 |
| 16 | **The Emergence of Functional Ultrasound for Noninvasive Brain–Computer Interface** (2023), Research（**综述，非新原型实验**）. [DOI](https://doi.org/10.34133/research.0200) / [全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC10427153/) | 郑海荣、牛丽丽等；EN/BCI方向地图 | 梳理功能超声脑活动读取及超声调控；用于理解郑海荣“脑机接口/生物智能”的知识背景。不能将综述列举的他组结果归为本作者新实验。 | 神经解码、时空去噪、跨个体泛化、闭环刺激、因果验证；需要神经数据/平台合作。 |

## 三、这组文章透露的可操作标准

1. **材料/生物创新路线**通常靠真实培养、制备、活性与功能实验；纯软件团队没有湿实验伙伴时，不宜假装能复刻完整活肌肉或细胞机器人。
2. **算法路线有真实先例**：#10明确是深度学习控制；#14明确把自动微分用于仿真；#15是医学影像网络；#5是数值方法。但其中仅#10较直接接近机器人闭环，另外几条必须把和本会机器人问题的联系补足。
3. **最强的算法投稿故事**宜是“解决明确BH系统的测量/控制/设计难点”，证据至少包括适当基线、留出个体/批次/环境、失败案例和可复现协议。若只能仿真，应明确限定为 simulation / enabling technology，不声称体内或临床验证。
4. **医疗故事重在完整链条**：成像可见→定位→导航→递送或助力→效果→安全/清除。只报轨迹漂亮或Dice提高，往往不能回答最终临床价值。
5. **不能据这些顶级期刊倒推出 ICBR 录用门槛**。它们用于识别同行对什么认真；首届会议尚无公开历史接受/拒绝数据，且CFP明确不做同行评议。实际接收筛选与口头/海报安排，不等于学术论文同行评审。

## 四、优先级建议（在“我们主要是软件/AI能力”这个尚待确认的假设下）

- **优先A：微机器人闭环感知与导航基准。** 以第六节2025–2026最新研究为首选基线，#10作为历史理解入口；先复现并检查已有方法的失败边界。跨几何、动态环境和sim-to-real本身已有先例，不能直接当创新。若日后能获得BH真实视频/台架合作，可进一步验证。
- **优先A：软体–活体组织交互的可微仿真与患者特异模型。** #14主办团队已有直接先例，官方心脏专题又明确含 sensing/control、patient-specific modelling/digital twins；如果做到模型参数验证或台架耦合，适配度高。只把通用机器人引擎改名为“数字孪生”不够。
- **优先B：活肌肉/细胞驱动器健康与控制。** 与#1–3对应，需要实验室合作；软件可先交付收缩检测、疲劳估计、批次划分和刺激优化，而不是新材料承诺。
- **优先B：昆虫神经传感解码。** #4、#5方向明确；若真实数据可公开获取/合作获得，跨个体稳定性、少样本校准比再造一个分类网络更有说服力。
- **条件式B：心脏MRI→几何/力学/控制。** #15说明夏泽洋团队做过影像AI；如果继续到个体心脏辅助器械规划/仿真，契合度高；停在纯分割模型，主题连接较弱。

上述优先级是依据公开研究与议程作出的匹配推断，不是对组织者个人喜好的判断，也不是接收保证。

## 五、相邻成熟会议的真实题材：4例，更接近可交付的项目粒度

这些是 **RoboSoft 2024 / BioRob 2024** 的真实接收或论文记录，**不是本会往届**，两者出版制度也不同于本届ICBR。仅用于题材参照。

| 会议 / 类型 | 真实题目 / 来源 | 对本次选题的启发与边界 |
|---|---|---|
| RoboSoft 2024，Contributed Paper，口头MoBT1.2 | **Bilayered Biofabrication Unlocks the Potential of Skeletal Muscle for Biohybrid Soft Robots** — Aiste Balciunaite, Oncay Yasa, Miriam Filippi, Mike Yan Michelis, Robert Kevin Katzschmann. [会议官方接收列表](https://gravishlab.ucsd.edu/robosoft2024/proceedings/) | 是直接的骨骼肌BH方向。证明“一个生物致动器几何/制备改进”即可构成会议研究题目，无需完整临床系统；本次仅核验接收与题目，未据标题推断统计强度。 |
| RoboSoft 2024，Contributed Paper，Interactive TuPo2S.22 | **MoLDy: Open-Source Library for Data-Based Modeling and Nonlinear Model Predictive Control of Soft Robots** — Daniel G. Cheney, Marc D. Killpack. [官方列表](https://gravishlab.ucsd.edu/robosoft2024/proceedings/) / [作者代码](https://github.com/byu-rad-lab/moldy) / [DOI](https://doi.org/10.1109/RoboSoft60065.2024.10522031) | 软件工具库+学习动力学+闭环控制也是成熟会议题材。原作者BYU学位论文说明该库为软体机器人建模控制服务：[大学全文条目](https://scholarsarchive.byu.edu/etd/10948/)。迁移至ICBR仍需讲清活体/医疗机器人接口问题。 |
| RoboSoft 2024，Contributed Paper，Interactive TuPo1S.24 | **Physics-Informed Neural Network for Scalable Soft Multi-Actuator Systems** — Carly Mendenhall, Jonathan Hardan, Trysta Chiang, Laura Blumenschein, Adrian Buganza Tepole. [官方列表](https://gravishlab.ucsd.edu/robosoft2024/proceedings/) / [DOI](https://doi.org/10.1109/RoboSoft60065.2024.10522053) | PINN/多执行器可扩展建模属支撑技术，可作为算法型参照；它自身不因“soft”或“physics-informed”变成BH。 |
| BioRob 2024，正式会议论文 | **Optimization of a Synergy-Driven Musculoskeletal Model to Estimate Muscle Excitations and Joint Moments of the Ankle Joint at Different Walking Speeds** — F. Damonte, V. V. Khanapuri, G. Durandau, M. Sartori. [作者大学托管论文](https://ris.utwente.nl/ws/portalfiles/portal/468487168/Optimization_of_a_Synergy-Driven_Musculoskeletal_Model_to_Estimate_Muscle_Excitations_and_Joint_Moments_of_the_Ankle_Joint_at_Different_Walking_Speeds.pdf) / [DOI](https://doi.org/10.1109/BIOROB60516.2024.10719730) | 个体特异肌骨模型+IPOPT与直接配点优化，为假肢控制估计肌肉激励与关节力矩；说明“建模与优化”可形成独立稿件。是人类运动/辅助控制，不能直接等同于活细胞BH。 |

额外参照：BioRob 2024官方专题含“Bioinspired and Biohybrid Soft Robots: Advanced Materials and Enabling Technologies”，把AI、计算控制、微流控、生物制造与细胞刺激放在同一讨论框架，显示跨学科支撑技术确有位置。[官方Workshop列表](https://www.biorob2024.org/workshops-tutorials/)。

## 六、2025–2026最新进展补查：必须收窄“研究空白”

以下三篇已是正式期刊论文。只核实公开正文/摘要、图注与资源声明，**未下载运行复现、未核验代码能否完整重现全部实验**。三者研究对象主要是人工磁性群/磁性微机器人或声学微气泡群；不能因为场景是“血管”，就将其称为活细胞BH。

1. **Autonomous navigation of intelligent microrobotic swarms in unknown environments**，2026-06-22，Nature Machine Intelligence。作者Xuanyu An、Shengming Luo、Haoyu Zhang、Qijun Yang、Yuanbiao Ma、Bin Wang、Jiansheng Du、Qianqian Wang（东南大学，通信作者王倩倩）。Transformer式时序注意力RL＋多层域随机化，处理部分观测；已展示动态避障、搬运、移动目标与暂时视觉丢失恢复，并在装有猪血的脑血管**体外仿体**中以激光散斑成像导航。不是活猪体内验证。[论文](https://www.nature.com/articles/s42256-026-01252-6)；[代码/模型/训练日志/实验部署入口](https://github.com/seuwanglab/Intelligent-Microrobotic-Swarm-in-Unknown-Environments)；[固定版本Zenodo](https://doi.org/10.5281/zenodo.18153971)。**“未知环境＋动态障碍＋暂时不可见”已经有人系统做过，不能笼统当空白。**

2. **Minute-scale training for microrobot navigation**，2026-09-28，Nature Machine Intelligence。作者Yinghan Sun、Aoji Zhu、Xiang Ji、Yamei Li、Jiachi Zhao、Yun Wang、Li Zhang、Huijun Gao、Lidong Yang（张立/高会军/杨立栋通信）。并行人工血管仿真＋TSR奖励，训练压至10分钟以内；已提供不同微机器人、动态场景、流动与3D血管**模型**的零样本迁移演示，附重复轨迹试验。**“加速RL训练/跨机器人sim-to-real”也不能泛称新。** [论文](https://www.nature.com/articles/s42256-026-01305-w)；[作者代码](https://github.com/yinghansun/mr-nav)；[人工血管数据集](https://doi.org/10.5281/zenodo.21719761)；[代码归档](https://doi.org/10.5281/zenodo.21761240)。GitHub README与预印本的吞吐数口径不同，报告无需据此放大性能，应以最终稿及具体硬件配置为准。

3. **Model-based reinforcement learning for ultrasound-driven autonomous microrobots**，2025-06-26，Nature Machine Intelligence。Mahmoud Medany、Lorenzo Piglia、Liam Achenbach、S. Karthik Mukkavilli、Daniel Ahmed（ETH＋IBM）。Dreamer v3式世界模型用于超声驱动微气泡群，在真实微流道中做静态/流动、避障与逆流导航；新环境先约50%成功，增加30分钟训练后超过90%。是台架物理系统，不是临床/体内治疗。[论文](https://www.nature.com/articles/s42256-025-01054-2)；[仿真与物理训练数据/检查点](https://doi.org/10.6084/m9.figshare.28940828.v1)；[控制与分析代码](https://github.com/M-Medany/Model-Based-Reinforcement-Learning-for-Ultrasound-Driven-Autonomous-Microrobots)；[归档](https://doi.org/10.5281/zenodo.15054076)。**“世界模型使少样本微机器人控制成为可能”已有直接先例。**

由此修订前面的优先A：先以2026最新工作为基线，做**独立、预先冻结划分的复现实验和失效分析**，再决定创新点。可研究但尚未在本轮证实为空白的细分问题包括：真实细胞/组织活性变化造成的非平稳动力学；把导航表现与细胞存活/功能损伤共同评价；跨实验室成像和驱动设备的外部验证；具有明确定义风险预算的拒绝/接管策略。上述也需要进一步逐项查新，不能预先宣称首次。若仅投本届不同行评议的长摘要，**扎实复现＋清楚的边界/失败发现**比假定新颖性更适合拿去讨论与找合作。
