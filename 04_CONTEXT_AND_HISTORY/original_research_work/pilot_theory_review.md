# 小型rate network同信息选点先导：理论审查与可推翻检查

日期：2026-10-16。只审设计，不编写或修改代码，不改outputs。本先导只检验一个已知目标导向设计思想在特定非线性反事实任务中的效果与失败边界，**不是新OED方法，也不是生物混合机器人验证**。

## 1. 核心审查结论

方案可在Mac上的小模型中轻量实施，但“最小化q的局部后验方差，得到了更小q局部后验方差”必然成立，不能作为研究发现。应问：**当选择规则只知道同一份先导数据和名义模型时，它针对q选择的观测点，是否在独立生成的真实参数/新测量噪声下，降低反事实响应q的实际误差；这种优势是否经得住目标置换、模型局部性与目标族变化？**

仅有正结果仍是goal-oriented/c-optimal design的应用复现。它可能支持一个有限的研究问题：在已知J、未知gain/bias、预算受限的网络中，“状态重建质量”何时不是“反事实积分响应精度”的好代理。要形成独立论文，后面仍需理论条件、非平凡失败机制或外部模型/数据支持。

## 2. 最小模型与语义必须冻结

建议n=6的稳定rate network，传感预算k=2，所有15个节点子集穷举。这样不必把贪心启发式、GPU和选择算法误差混进问题。

\[
\tau\dot x=-x+\tanh(D_gJx+b+Bu(t)),\qquad \theta=(g,b).
\]

- J和B是所有设计方法都知道的结构；g为每节点的动态gain，b为动态bias。**不要同时把g当成观测仪器gain。** 若原实现拟用另一种rate方程，先冻结具体形式；这些形式的参数敏感性不同。
- 初始x(0)固定已知，所有方法同一条件。为了低成本排除混沌/多稳态混杂，可使用预先限定的J范数与有界正gain，使网络收缩；例如\(\|J\|_2\le0.6\)、\(g_i\in[0.8,1.2]\)时，tanh是1-Lipschitz，\(\|D_gJ\|_2\le0.72<1\)。这是模型生成规则，不按目标优势筛网络。
- n=6、稳定网络只是方法先导。不能用它证明真实神经系统机制、基因调控回路或脑机接口可行性；将它写成抽象网络模型即可。
- 观测 \(y_{M,t}=P_Mx(t;\theta,u_{cal})+\epsilon\)，同一候选时刻表、同一独立Gaussian噪声、同一新测量数、同一节点成本。先只选节点，不同时选时刻与刺激。
- 独立的校准输入\(u_{cal}\)用于产生新观测；目标输入\(u_*\)是要预测的刺激。两者预先冻结。一个全零初始＋零输入＋零bias的平衡点会让gain灵敏度为零，不能误当“结构上无需知道gain”。用与目标无关的弱公共probe避免这个人为退化，并如实报告剩余不可识别性。

### q明确为反事实刺激差分

\[
q(\theta)=\int_0^T w(t)c^\top\left[x(t;\theta,u_*)-x(t;\theta,0)\right]dt.
\]

两条轨迹使用同一个\(\theta\)和同一初始状态。c、w、刺激节点/幅度/持续时间与T必须先于测试真值冻结。原始积分\(\int x_u\)和该差分q不是同一目标，不可混用。

若目标是某个下游节点，允许预先指定，但不要事后从所有节点中挑出最支持方法的一个。主分析可用固定均匀输出c；或预先定义一组节点目标且报告全部。目标组过大时不必扩规模，n=6即可逐一报告。

## 3. 同信息的局部Gaussian选择：允许做什么，禁止做什么

先用所有方法共用的D0获得名义参数\(\theta_0\)与先导后验近似\(C_0\)。D0可以是全节点少量时刻的短probe，所有设计都计入同一份D0及其观测成本。设计时只能读取J、B、D0、\(\theta_0,C_0\)、候选观测协议和已登记q；**不能读取theta_true、测试噪声或真实q**。

有限差分得到新观测的敏感矩阵\(F_M\)，包括全部候选时刻；目标梯度 \(a=\nabla_\theta q(\theta_0)\)。新观测的设计期协方差为

\[
C_M=\left(C_0^{-1}+F_M^\top R_M^{-1}F_M\right)^{-1}.
\]

若使用ridge prior，从\(C_{prior}\)与D0共同更新得到C0；不要把D0信息重复计算，也不要把目标函数里出现的相同先导样本误当独立观测。应使用对称线性求解与Cholesky，而非随意伪逆遮盖病态。

状态重建设计需先固定完整状态任务\(z(\theta)\)。为避免故意让基线对着错误刺激优化，主分析宜用**与q相同输入和时间窗的全部节点刺激/对照轨迹**，而不是仅校准probe轨迹。\(G=\partial z/\partial\theta\)，并按节点/时刻归一加权，避免网格数量决定标准。

还应设置一个更强的state基线：重建全部节点的**差分响应轨迹**\(z_\Delta=x_u-x_0\)，按其trace后验风险选M。否则q方法可能仅因去除了与目标无关的公共baseline不确定性而赢，结论很容易成为人为任务不匹配。如果相对这个response-state基线的优势消失，必须明确报告，不能泛化为“状态重建不是好代理”。

\[
M_{state}=\arg\min_{|M|=k}\operatorname{tr}(WG C_MG^\top),
\qquad
M_q=\arg\min_{|M|=k}a^\top C_Ma.
\]

这里“latent-state posterior variance”是参数不确定性传播到隐状态轨迹的方差；它不自动等同带过程噪声的filter/smoother后验。若实际系统有过程噪声，需要另建状态空间模型；本先导先不加。

选择后再生成该M的新观测D_M，并用D0+D_M做相同的非线性MAP/ridge拟合，得到\(\hat\theta_M\)；通过完整非线性ODE预测\(\hat q_M=q(\hat\theta_M)\)。真值只由独立评价端计算\(q_{true}\)。所有设计的拟合算法、初始化数量、终止容差与预算一致。

**重要：** 主评价是新噪声重复下\((\hat q_M-q_{true})^2\)及bias，不是\(a^\top C_Ma\)。局部预测方差只是设计内部量，可以另报与实际误差是否一致。完整Bayesian posterior若未抽样验证，应称局部Laplace/线性化近似，别称精确后验。

## 4. 五项严格检查：每项都允许推翻正面故事

### 检查一：真值隔离与逐阶段冻结

设计程序接口只接收共享pilot和名义模型，不接收theta_true。目标列表、随机种子、网络生成规则、ridge强度、有限差分步长、预算和失败定义在评价前冻结。允许真值模块生成D0/未来观测，但不允许把生成真值作为设计者已知的额外输入。

**推翻条件：** 目标输出节点、刺激、J seed或ridge在看了q误差后才选；或某设计用真值初始化/算梯度、另一设计仅用theta0。这时任何优势不成立。theta_true设计可单列为不参与竞争的oracle upper-reference，但不能混入可部署方法。

### 检查二：名义优势必须转化为独立实际误差优势

每个冻结网络与pilot重复，用同一完整噪声场\(\epsilon_{i,t,r}\)的对应子集评价各M，做配对比较；该噪声场不对设计者开放。对每个M都重新拟合非线性模型，再算q误差。网络/pilot作为独立实验单位，测量噪声重复只是单位内重复，不能当作几百个独立网络增加显著性。

至少对少量预先指定实例检查：有限差分步长h/2、h、2h下敏感性与选点是否稳定；ODE容差变化；局部线性q与完整非线性q的差异；先导后验抽样后的非线性响应是否明显偏离局部Gaussian。既不需要大MCMC，也不需要用最终测试结果反调设计。

**推翻条件：** 只有设计内部方差更小，实际q误差不降或更差；轻微数值设置改变就翻转排名；优势只在theta0=truth出现。此时应报告局部设计失效/校准不足，而非隐藏负结果。

### 检查三：matched random＋shuffled goal的完整二维风险矩阵

Matched random从相同可行子集、相同k/时刻/成本均匀抽样；n=6,k=2可直接评价全部15个M，因此不用挑随机seed或只报最差随机抽样。若约束节点度数等匹配，应在看结果前定义，且所有设计共享同一可行域。不要把oracle最佳随机M当可实施基线，也不要只用一个幸运/倒霉M。

Shuffled goal：在预登记目标族中对c的节点标签作同范数置换，保持刺激与时刻表不变，用\(q_\pi\)在theta0处的梯度选\(M_{q_\pi}\)，然后同时报告它在真实目标q与自身目标\(q_\pi\)上的误差。节点完全对称/置换不改变q时应标记退化，不能强行当有效shuffle。

**推翻条件：** q设计只在精心挑选目标上赢，跨预登记目标族消失；shuffle在原q上同样有效，说明优势可能来自高信息节点而非goal alignment；或state设计对两类目标都更好。此时不能说“必须按功能选测点”。反过来，shuffle在自己的目标上恢复优势，比仅展示它在原目标失败更有解释力。

### 检查四：严格线性差分null与generic linear reference分开

Null固定为
\[
\dot x=Ax+b+Bu,
\]
A/B已知、仅b未知，q仍是同一初始条件下刺激减无刺激响应。此时
\[
\delta\dot x=A\delta x+B u,\quad\delta x(0)=0,
\]
故q与b无关，\(\partial q/\partial b=0\)，\(\operatorname{Var}(q|D)=0\)。即使每个b自己的共同起点取不同稳态，同b的两条轨迹相减仍成立。

**必须通过：** goal梯度接近数值零、选点全tie（用固定标签顺序打破tie，不拿误差挑选）、各方法q都等于已知A/B计算值。此null不能计算“相对误差改善比”，分母本来近零，应报绝对误差/容差。若实现里出现稳定方法差异，先查paired初值、q定义、数值积分与错误引入A未知。

Generic linear-Gaussian q=cᵀx会保留对b的依赖，目标导向设计可以获益；它适合作为已知方法sanity reference，**不是上述零差异控制**。非线性模型中baseline会改变局部gain，因此bias不再必然抵消，恰是先导可检查的具体机制。

### 检查五：排除直接测目标/高信号/条件数与人工选靶

把“允许直接测q读出节点”作为主协议明确写出；若要说明网络传播价值，另设预登记的禁止读出节点协议，让所有设计同样受限，不能只限制random/state。报告目标梯度a与state风险权重\(G^\top WG\)的几何关系、各M信息谱、名义条件数及输出信号量级。这些诊断只解释结果，不作为看测试结果后剔样的依据。

固定J的一组独立seed、固定的目标/刺激配对全部展示，特别保留state和goal选同一M、q接近零以及明显饱和的实例；若某类无效实例的判定需要阈值，预先定义并同时报告未筛结果。

**推翻条件：** 优势完全由直接测目标节点、换算单位/状态网格权重、特定ridge、极低q或一个特殊网络造成。这样的结果最多说明设计标准的已知几何差异，不能支持广泛的生物学结论。

## 5. 最小规模与Mac预算建议

起步只做n=6,k=2、单一固定采样表、2–3个冻结目标/刺激组合。用少量固定J seeds与pilot噪声重复，另有未来测量噪声重复；先确认线性null、敏感性和完整非线性拟合。因为仅15个M，可缓存每个theta0的全部敏感性，随后枚举代价几乎只是小矩阵运算。

用端到端小样本运行时间线性估算总耗时，设置明确上限。若已有代码需要1–2天，优先减少网络/目标数与posterior诊断实例，不牺牲所有M的公平预算、truth隔离和null。不要为了得到显著性在看到结果后不断加seed；预定的小先导允许结论“不确定/没有优势”。

先导只需输出：所有实例的选点表、名义风险与实际q误差对照、配对效应分布、state与goal的交叉误差矩阵、null误差与数值稳健性日志。不要只交一张最好看的网络图。

## 6. 前史与方法贡献边界

- Attia、Alexanderian、Saibaba，**Goal-Oriented Optimal Design of Experiments for Large-Scale Bayesian Linear Inverse Problems**，Inverse Problems，2018。[作者原始稿](https://arxiv.org/abs/1802.06517) / [作者大学出版列表](https://asaibab.math.ncsu.edu/pub.html)。直接将QoI后验不确定性与全参数不确定性区分；本先导的局部q方差选点是这条成熟思想的应用。
- Liepe、Filippi、Komorowski、Stumpf，**Maximizing the Information Content of Experiments in Systems Biology**，PLoS Computational Biology，2013。[原文](https://doi.org/10.1371/journal.pcbi.1002888)。已有Bayesian系统生物学实验设计，纳入先验并讨论局部近似之外的方法。不能把“同信息下选择更有用观测”说成首次。
- Kreutz、Timmer，**Systems biology: experimental design**，FEBS Journal，2009（方法综述，非原创实验）。[原文](https://doi.org/10.1111/j.1742-4658.2008.06843.x)。说明设计标准随研究问题而变、观测时刻/刺激/测量预算必须共同定义，随机化/重复/混杂不能省略。
- Sussillo、Abbott，**Generating Coherent Patterns of Activity from Chaotic Neural Networks**，Neuron，2009。[原文](https://doi.org/10.1016/j.neuron.2009.07.018) / [PubMed](https://pubmed.ncbi.nlm.nih.gov/19709635/)。提供经典泄漏rate network＋非线性rate/readout的建模谱系；本先导不是其FORCE学习复现，也不应宣称使用小tanh网络即具生物真实性。

**可以成立的初稿措辞：** “We conduct a controlled pilot comparing state-reconstruction and goal-oriented sensing under a shared nominal model, and evaluate their consequences for nonlinear counterfactual response prediction.”

**目前不能成立的措辞：** 新目标导向设计方法、首次发现任务导向观测、证明latent-state重建无价值、证明真实生物网络的最优测量策略，或证明生物混合机器人性能提升。是否值得后续研究，取决于上述严格检查是否留下一个既有OED几何无法直接解释的、可重复的具体问题。
