# 固定J、未知gain/bias、有限读出预测刺激差分q：方法谱系与贡献边界

2026-10-16。定向核查6篇原始方法/研究论文。目的不是列参考文献，而是明确当前先导的方法究竟从哪里来、适用条件是什么、哪些结果不能再称新。没有修改代码/outputs，没有重计算。

## 1. 最重要判断

**当前先导的“goal”和强“response_state”其实都属于目标导向Bayesian A-optimal设计：前者针对一个标量，后者针对N维积分响应向量。** 区别是预测空间的维度与权重，不是“有功能意识的新方法”对“只看状态的旧方法”。固定J未知gain/bias的模型与按局部参数–activity映射选神经元，也已有直接神经科学前史。

所以不能把已见到的局部方差差别或任务专门化解释成新算法/新普适原理。可能值得继续的窄问题，只能是特定神经动力学与测量限制下，局部设计的**有效范围、失败机制及风险权重**；它们是否有新意仍要验证。

## 2. 统一记号：把已有方法与本先导准确对接

已知J和输入；未知\(\theta=(\log g,b)\)。在名义\(\theta_0\)线性化校准观测h_M与目标q：

\[
F_M=\partial_\theta h_M(\theta_0),\quad
C_M=(C_{prior}^{-1}+F_M^TR^{-1}F_M)^{-1},\quad
a=\partial_\theta q(\theta_0).
\]

先导q是全非线性网络的刺激–对照积分rate差；选择风险是\(a^TC_Ma\)，属delta-method目标方差近似。设全节点积分响应向量为Q，\(G=\partial_\theta Q\)，强response_state风险为\(tr(GC_MG^T)/N\)。这正是**标量目标A-optimal与向量目标A-optimal的比较**。当前选择用prior名义theta0=0，后续MAP拟合才使用观测；不能把它写成已经完成了sequential/pilot-informed设计。

## 3. 六篇直接前史

### 3.1 最接近神经模型的原论文：Beiran & Litwin-Kumar，2025

**Prediction of neural activity in connectome-constrained recurrent networks**，Nature Neuroscience 28,2561–2574。[正式版](https://www.nature.com/articles/s41593-025-02080-4) / [开放作者稿](https://pmc.ncbi.nlm.nih.gov/articles/PMC12648571/) / [代码](https://github.com/emebeiran/connconstr) / [最终数据入口](https://doi.org/10.5281/zenodo.16618353)。

**已核原文方法：** teacher/student共享连接权重，未知单神经元参数不同；研究未测activity预测与参数退化。正式版Fig.8“Optimal selection of recorded neurons”利用参数到activity的局部映射A及其SVD，选择使subsampled loss与full loss的stiff modes更对齐的神经元，随后正交投影再选；非线性情形以初始参数猜测线性化，可迭代细化。**它已经处理了固定J、未知生物参数、有限读出与非真值初始猜测选点。**

**本先导何时可以借用：** 作为rate-model假设与完整activity预测基线的直接出处；可在相同theta0和信息预算下实现其已发表SVD选点，检验与我们trace-posterior基线的差别。

**局限与禁止主张：** 当前activity基线不是作者SVD算法的忠实复现；我们的teacher更小、输入与先验不同，也未复现其图。原文已有“参数未恢复但未测activity可预测”与记录神经元排序，不能称首次发现。剩余差别在于**预定反事实积分q**与完整activity预测，并不自动构成创新。

**本地已固定源代码的核验补充：** 只读查看`work/source_audit/pinned/nn_fig8_plots_de.py`，138–181行确有row normalization、SVD与投影式顺序选择；158行的线性映射是\(A=pinv(I-J)J\)。`calculate_perf`把候选归一化行与右奇异方向的重叠按奇异值平方加权；每选一行后更新正交补投影，再挑最大score。该代码块是线性特例，**没有我们当前的prior precision＋noisy finite-time posterior trace criterion**。此外当前先导观测r而内部状态x不同，不能未经变量映射就把该固定点A直接当r的敏感矩阵。若后续复现，要按作者完整线性协议另建sanity baseline，再为非线性迁移明确给出自己的推导。

`nn_fig8_gh.py`依赖的teacher及Figure8预生成数据没有在这次本地源代码检查中备齐，因此这里只能说“已核源码方法”，不能说“已复现Fig.8 G/H效果”。

### 3.2 标量/向量预测风险的直接数学前史：Attia, Alexanderian & Saibaba，2018

**Goal-oriented optimal design of experiments for large-scale Bayesian linear inverse problems**，Inverse Problems 34,095009。[DOI](https://doi.org/10.1088/1361-6420/aad210) / [作者全文](https://arxiv.org/html/1802.06517)。

**已核公式：** 在线性Gaussian模型中，参数posterior covariance为\(\Gamma_{post}\)，目标线性算子P给\(\Sigma_{post}=P\Gamma_{post}P^*\)。原文A-GOODE取\(tr\Sigma_{post}\)，D-GOODE取\(logdet\Sigma_{post}\)，并给Bayes risk/EIG解释；目标维度改变即可改变设计。

**本先导何时可以借用：** 用P=aᵀ得到标量q方差，用P=G得到全积分响应风险；有限参数、独立Gaussian噪声下的C_M公式是直接特例。若非线性和posterior足够局部，可以作为便宜近似。

**局限与禁止主张：** 原文线性Gaussian结果不证明我们非线性、固定单真值的MAP误差收益；单点局部近似不是全Bayesian期望。**单目标优于平均目标、按q选传感器**已在这条前史里，不能称新。response_state本身也是GOODE，论文应称“scalar versus vector predictive-risk designs”。

### 3.3 非线性目标设计已有更完整方法：Zhong, Shen, Catanach & Huan，2026正式发表（2024预印本）

**Goal-Oriented Bayesian Optimal Experimental Design for Nonlinear Models Using Markov Chain Monte Carlo**，SIAM/ASA Journal on Uncertainty Quantification 14(1),19–47，2026-01-02在线，2026年3月卷期（2025-08-28接收，不能将接收年份当发表年份）。[正式论文DOI](https://doi.org/10.1137/24M1649344) / [公开作者全文v1](https://arxiv.org/html/2403.18072v1)。

**已核方法：** 针对非线性观测与非线性QoI，最大化QoI的expected information gain；用nested Monte Carlo、MCMC posterior采样、KDE posterior-predictive density和KL估计，再以Bayesian optimization搜设计。原文T3示例展示参数EIG与QoI EIG能给相反设计排名。

**本先导何时可以借用：** 不必在Mac上全量实现；可用它说明单点Gaussian方差近似省掉了哪些平均与非线性推送。只在几个冻结实例用posterior样本推送Q/q检验偏斜、饱和和多模态，便能判断局部近似是否值得信任。

**局限与禁止主张：** EIG不等于平方误差风险，KDE/MCMC/nested MC有自己的成本与估计偏差。不能说它“只是更精确的同一个variance criterion”；也不能把我们便宜的greedy局部版本叫新的非线性GO-OED。若目标梯度在theta0为0，二阶目标仍可能不确定，局部variance设计会退化；这个一般性问题也不新。

### 3.4 非线性网络选点的观测谱前史：Haber, Molnar & Motter，2018卷期（2017在线）

**State observation and sensor selection for nonlinear networks**，IEEE Transactions on Control of Network Systems 5(2),694–708。[DOI](https://doi.org/10.1109/TCNS.2017.2728201) / [作者全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC6178986/)。

**已核方法：** 离散动力学的初值–观测映射w(x0)及Jacobian用于非线性状态重建。原文Eq.22以固定传感器数量、binary选择优化\(-logdet(J_{obs}^TJ_{obs})\)；比较经验observability Gramians，并展示观测时长、观测比例与估计误差的关系。

**本先导何时可以借用：** 作为“图结构本身不足，动态Jacobian/观测时间窗重要”的直接前史。若要把参数作为常值扩展状态，可讨论扩展系统\(\dot\theta=0\)，但此扩展需自己定义，不能冒充原文直接验证了本模型。

**局限与禁止主张：** 初始状态observability与固定初值下未知gain/bias识别不是同一问题；logdet观测Gramian也不等同q预测风险。不能把某个rank满了说成q后验已校准，更不能把固定J的图论可观测性当实际反事实可预测性保证。

### 3.5 生物/神经数据的动态选点已有实证：Pickard等，2025

**Dynamic sensor selection for biomarker discovery**，PNAS 122，e2501324122。[正式DOI](https://doi.org/10.1073/pnas.2501324122) / [开放正文](https://pmc.ncbi.nlm.nih.gov/articles/PMC12541339/) / [作者预印本](https://arxiv.org/abs/2405.09809)。作者Joshua Pickard、Cooper Stansbury、Amit Surana、Lindsey Muir、Anthony Bloch、Indika Rajapakse。

**已核方法：** 基于observability选择随时间改变的传感器，使用rank、Gramian determinant/trace等指标；Eq.11从选中观测构成Y与观测矩阵O，最小二乘/伪逆估计未测状态。细菌基因表达例用一个replicate学习动力学/选点，另一个replicate验证；还分析神经activity与EEG。

**本先导何时可以借用：** 强调训练/设计与独立验证划分，明确我们静态M与其动态sensor schedule不同。可提供真实数据选点未来方向，但不能现在把其公开神经数据自动当成与本固定J模型对齐的connectome数据。

**局限与禁止主张：** 用数据估计A(t)的动态状态重建不直接识别刺激因果差分；输入、模型误差及观测机制仍重要。“将observability用于生物或神经传感器选择”“有限读出可预测其他变量”已有实证，不能泛称新。

### 3.6 目标可预测不要求参数可唯一识别：Kreutz, Raue & Timmer，2012

**Likelihood based observability analysis and confidence intervals for predictions of dynamic models**，BMC Systems Biology 6,120。[DOI](https://doi.org/10.1186/1752-0509-6-120) / [全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC3490710/)。

**已核公式：** 原文Eq.9定义prediction profile likelihood：固定预测值z，在\(F(D_{pred},\theta)=z\)约束下最大化现有数据的likelihood。由profile阈值求预测区间；不要求参数本身唯一。原文明确预测可以是积分、peak或其他动态函数；并区分无噪声模型prediction与有新测量噪声的validation。

**本先导何时可以借用：** 少量冻结实例上做q的profile诊断，可以检验MAP处Gaussian窄区间是否漏掉远处、同样符合测量的参数解。对严重非识别/非Gaussian情况，比仅看局部H逆更有解释力。

**局限与禁止主张：** 优化局部失败会给假窄profile；likelihood-ratio阈值依赖渐近条件。不能直接把带ridge prior的MAP目标套上频率学\(\chi^2\)置信区间并宣称coverage。参数可识别性与目标可识别性的区别早已建立，不是本先导新概念。

## 4. 由这些文献推导的本题边界（本节是方法对接，不声称新定理）

### 4.1 强向量基线对标量目标有保守联系

若\(q=c^TQ\)，则在同一局部协方差下
\[
Var(q)\approx c^T(GC_MG^T)c
\le\|c\|^2\,tr(GC_MG^T).
\]
所以完整响应向量风险不是与q毫无关系的愚蠢代理；它给一个保守上界，但不优先单个c方向。某个c方向的改进会牺牲其他方向，属于已知风险分配。

若预先不知道c，且目标分布满足\(E[cc^T]=I/N\)，则对任何固定M，平均标量预测方差恰等于向量平均trace风险。**允许goal在知道c后选不同M，而state对所有c使用一套M，比较的是“任务事先已知的专门化收益”与“一套记录服务多任务的通用性”。** 这不是无条件的goal优越。即使平均结果更好，也可能只是\(E_c\min_M R(M,c)\le\min_M E_cR(M,c)\)这条基本优化关系。

### 4.2 反事实差分q不是现成因果实证

模拟中对同theta运行刺激/对照是结构模型的反事实。它依赖J、输入通道、activation family和初始条件都正确；本先导truth与拟合使用同一模型，只展示模型内预测，不识别真实神经因果效应。

### 4.3 当前线性null是具体代数抵消，不是GO-OED失效

A/B已知、只b未知、paired initial的线性系统中，刺激–对照差分与b无关，所以目标不需要任何测量。非线性gain/bias改变刺激传播后，这个消去才不成立。该null验证了q定义及数值实现，**不能拿它证明非线性结果来自新理论**。

### 4.4 真正待检验的是局部近似怎样失效

可研究但未确立创新的问题：当任务端点不可测、posterior具有长sloppy方向、或校准与刺激条件的工作点分离时，theta0处a与实际posterior q几何是否偏离？这种偏离是否能用一个便宜、可校验的诊断预测？诊断是否比“再多抽样/换更强先验”更有信息？这里有潜在具体问题，但需要与现有非线性GO-OED、robust design和profile方法继续对照。

## 5. 对当前实验与前言的直接建议

1. 前言从Beiran2025的固定连接但生物参数退化问题切入，并承认其已有neuron selection；不要先宣称“connectome仍缺功能”后把所有选点工作抹掉。
2. 第二步说明GO-OED早已解决“为预测而非参数本身设计”的一般问题；我们的实验只是把scalar反事实QoI、vector响应、activity三种目标放到同信息控制下比较。
3. 第三步提出一个具体可检验问题：**当记录只允许远离刺激/读出端点，且从公共校准输入估计非线性gain/bias时，哪个预测风险代理能稳定对应实际反事实误差？** 问题必须同时报告绝对风险与事先规定的任务归一风险。
4. 方法部分把当前prior-nominal、analytic sensitivities、greedy、Gauss–Newton、ridge先验逐个标为成熟方法；不使用“novel framework”。
5. 下一轮优先补原论文SVD基线或说明未复现；明确response_state为**积分向量**，若加差分轨迹则作新基线命名；固定任务族与可测端点协议；再用少量q-profile或posterior推送检验局部近似。
6. 若最后只剩标量任务专门化的经典收益，停止“新方法”叙述；保留可复现先导/研究笔记。若发现稳定、非平凡且可诊断的局部失败机制，再讨论独立论文贡献。
