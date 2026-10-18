# EcN 备选：方法依据与最小规范

核查：2026-10-16。适用对象为GSE228761的二次研究先导；以下是设计协议，尚未执行。它不保证形成论文，不把规范当作科学新意。

## 六个核心依据

1. **原始实验与作者代码：** Triassi et al., Cell Systems 2023, [DOI 10.1016/j.cels.2023.05.004](https://doi.org/10.1016/j.cels.2023.05.004)；[作者EcN_analysis仓库](https://github.com/VoigtLab/EcN_analysis)。用途：重建构型/诱导/重复、原始分析和既有结论。
2. **MINSEQE：** [FGED原始指南](https://www.fged.org/projects/minseqe/)；[NCBI对MIAME/MINSEQE的官方说明](https://www.ncbi.nlm.nih.gov/geo/info/MIAME.html)。用途：样本、实验变量、原始/处理数据与处理方法的审计及报告。它是信息完整性标准，不证明统计正确。
3. **DESeq2官方release vignette：** [Analyzing RNA-seq data with DESeq2](https://www.bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html)。本轮页面显示1.52.0；实际执行应锁定所安装版本。相关小节：Input data、Collapsing technical replicates、Control features for estimating size factors、Contrasts、Interactions、LRT、Model matrix not full rank。用途：原始counts、计数联合模型、交互contrast及模型可识别性。
4. **组成偏差与TMM：** Robinson & Oshlack, Genome Biology 2010, [A scaling normalization method for differential expression analysis of RNA-seq data](https://doi.org/10.1186/gb-2010-11-3-r25)。用途：测序组成变化可扭曲库大小比较，鲁棒缩放应基于明确假设。它不证明任一归一化必然正确。
5. **嵌套交叉验证：** Varma & Simon, BMC Bioinformatics 2006, [Bias in error estimation when using cross-validation for model selection](https://doi.org/10.1186/1471-2105-7-91)。用途：分离模型/超参数选择与外层误差估计。本文没有规定EcN必须leave-gate-out；按gate分组是针对本研究泛化目标的设计判断。
6. **DOME：** Walsh et al., Nature Methods 2021, [recommendations for supervised machine learning validation in biology](https://doi.org/10.1038/s41592-021-01205-4)。用途：数据、优化、模型、评估透明报告；只适用于实际开展的监督预测部分，不把它套成所有探索网络分析的质量认证。

## 分阶段协议

| 阶段 | 必须做什么 | 能过关的产物/继续条件 | 方法依据 |
|---|---|---|---|
| 1. 资源审计 | 区分原始FASTQ、原始gene counts、FPKM、DE结果；逐列连接GSM/SRX、菌株构型、IPTG、培养时间、重复、QC、已知批次；区分同培养物多run与独立培养；检查工程插入序列和宿主locus注释 | 一张机器可读样本清单；每文件来源、哈希、版本、缺失字段；登记96与QC后实际n各自说明。metadata不足就收缩问题，不补造配对/批次 | 1、2 |
| 2. 原文复现 | 优先复现原文使用样本与QC、sensor/WT和gate/sensor比较、效应方向及主要图；先复现再替换方法。原文已排除4/96低mapping样本；每组有效重复需读表确认 | 原始分析与复现差异对照；差异来自版本、注释、QC还是统计方法均有说明；不以“新方法多检出基因”作为科学结论 | 1、2 |
| 3. 归一化审计 | 保留宿主与外源feature身份；以原始宿主counts估计鲁棒size factors作为候选；与原文FPKM和合理全feature/宿主限定鲁棒策略做敏感性比较；已知稳定controls可使用controlGenes，但不得从想保留的结论反挑controls | 外源转录占比、size factors、MA/PCA和关键效应在策略间的变化；结论依赖某策略时明确报告 | 3、4 |
| 4. 联合构型×诱导建模 | 在样本metadata支持时，采用含构型、诱导、交互及可识别批次的固定效应计数模型；以sensor-only为构型参考；联合抽取预定义contrast，控制多重检验，报告效应与SE/CI | 不只给显著基因名单；给共享效应、交互偏离及估计不确定性；检查设计矩阵满秩、低计数和离群敏感性 | 3 |
| 5. 条件性预测 | **仅在目标有独立定义且有可用标签时做。** 外层按gate完整留出，内层也按gate分组；所有筛基因/模块、降维、缩放、超参数选择在训练fold内；与简单模型比较 | 外层逐gate结果、分组表、调参范围、误差及不确定性；不得用外层挑模型，再报告同一外层最优分数 | 5、6 |
| 6. 外部验证 | 模型/特征/方向/阈值先冻结，再看独立数据；区分新gate、同实验室新批次、独立实验室、不同宿主菌株/环境几层验证 | 外部样本来源和重叠核查；分析冻结记录；失败同样报告。没有外部数据就仅声称内部可重复性 | 2、6 |
| 7. 报告 | 发布样本清单、排除理由、原文复现、主contrast、效应与CI、FDR、归一化/离群敏感性；若预测则给DOME表；代码锁版本、随机种子和可执行环境，保存全部外层预测 | 一条可追溯的原始/处理数据→分析→图表链；探索性与确认性结果分别标注；声明未测的功能与未识别的机制 | 2、6 |

## 本数据最重要的技术边界

### A. host-only normalization 是敏感性设计，不是自动正确的校正

外源载荷大量转录时，“每百万全部mapped reads”的宿主FPKM可能受组成影响。应明确size factor基于哪些features、排除了哪些外源/rRNA条目。对DESeq2，通常将宿主基因counts子集用于估计size factors即可构造宿主相对丰度分析；`controlGenes`仅适用于先验上可信不变的子集，**全宿主基因不等于全都不变**。

DESeq2 median-ratio和TMM都依赖可作为相对参照的多数特征/稳定部分。若宿主大量基因一致改变，去除外源features仍不能辨识绝对全局RNA变化；没有spike-in、绝对RNA/细胞数等外部参照，应保持“宿主相对转录响应”的表述。TMM作为另一个完整敏感性分析流程时，应使用其有效库大小/offset；不要把归一化count矩阵再输入DESeq2重复归一化。上述是依据3、4对本实验的应用判断。

### B. 联合contrast 的精确定义

最基本设计可写成 `~ construct + induction + construct:induction`，有真实且不完全混杂的批次时再加入batch。它估计的是固定构型的诱导响应差异。sensor-only设为参考后，某gate交互项对应log尺度的：

`[gate(+IPTG) − gate(−IPTG)] − [sensor(+IPTG) − sensor(−IPTG)]`。

也保留同状态gate与sensor的基线/总效应比较。主诱导项只代表参考构型，不是所有构型平均诱导效应。多个gate共享sensor对照，contrast估计相关；不可逐一算差后当独立观测。联合模型保留这一结构，聚合时还应保留协方差或对完整独立样本单位重采样。

DESeq2在基因间估计离散度、可对效应作适用的收缩；**这不等于自动给gate随机效应或分层因果模型**。若后续做模块层级模型，需另写其生成假设与估计器，不能拿DESeq2名称代替。完全混杂的batch与condition无法靠加入协变量解决。

### C. leave-gate-out 仍不等于功能预测

本数据的主要目标是宿主响应解释；若没有匹配growth/capacity或真实输出标签，就不开展所谓“负担/功能预测”。若目标仅是留出gate的转录重建，要明确评价的是RNA模式、不是生理功能；仅有10种repressor，外层最多约10个构型单位，不能用几十个培养重复冒充几十种新设计。

共享sensor对照若被同时用于构造训练和测试contrast，会带来参考误差相关。要说明部署时是否真的允许这个公共参考；必要时留出独立参考样本或在联合评估中传播参考协方差，不能仅称gate不同便宣布完全独立。统计推断可联合估计归一化；监督预测的学习型预处理则需在训练集拟合并给出新样本的冻结变换规则。

## 不采用的做法

- 将FPKM/TPM四舍五入后当原始counts输入DESeq2/edgeR；由已归一化表逆造读数。
- 将同培养物测序lane、多run、不同基因、网络边或重复抽样当新的生物样本；同构型随机拆分后声称泛化到新构型。
- 在约3–4重复的小组分别推断高维网络，再把不稳定hub当机制；或因“想用AI”优先选GNN。
- 全数据先筛DEG/模块/网络，再做交叉验证；把外层测试用于调参或挑最漂亮的图。
- 将从输入RNA计算的“应激分数”当独立真实负担标签；无外部功能读数却声称预测增长、疗效、运动或递送。
- 将不显著当等效、把归一化敏感性删掉、把探索后形成的假设写成预先设定。

这些限制是本实验设计与样本规模下的方法判断，并不是上述标准对所有GNN/网络方法的普遍禁令。最低规范的目的，是判断这个备选是否值得继续；若只复现既有结论，应如实停止或作为复现记录，不为了投稿再添算法。
