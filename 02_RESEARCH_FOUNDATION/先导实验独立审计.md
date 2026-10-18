# main_v1独立只读审计

2026-10-16。审阅pilot.py、protocol.json、results.csv、summary.json；未改代码或outputs，未重跑336拟合。独立重算CSV聚合，并用源文件中的simulate/make_case函数做一次节点选取后Jacobian方向差分检查。

## 结论

**没有发现明显索引或解析敏感性错误；设计信息预算是对等的。但这是prior-nominal设计，不是由同信息pilot拟合theta0的设计。当前数据能支持有限的合成可行性现象，不能支持普遍优势或方法创新。** 排除端点且M=6时，归一化与绝对误差给出不同排名，必须同时说明。

## 1. 实现与信息公平

- 当前源码SHA256与main_v1/source.sha256一致；336行=12 seeds×2 pools×2 budgets×7 methods。每seed是一张J、一个truth和一份完整噪声场；**不是336个独立网络**。
- simulate真正输出的是\(r_i=e^{g_i}\,softplus(x_i+b_i)\)，内部隐状态为x；回归观测/状态风险/功能q全部基于r。应称“activity/rate reconstruction”，不可说已评价隐状态x重建。
- 解析敏感性正确计入log-gain直导数r、bias直导数slope及递归状态敏感性。源记录全Jacobian差分相对误差2.77e-11；独立检查seed103、非排序节点[9,2,7]、选取与flatten后的Jacobian方向差分相对误差1.79e-11，未见选轴/排序错位。
- prospective_design只用J、prior名义theta0=0、prior sd、公开输入和任务，未读truth/observed/test outcome。选择前后truth替换不变也有检查。所有方法用同样观测数、同一可行pool、同一噪声方差、同MAP先验与优化器。
- **没有D0或经验theta0/C0**：H0是prior precision，真实观测只在选择后用于MAP。这和“共同先导数据产生名义参数”的原设想不同，必须改文字而不是倒称已做。这里是local prior-nominal Fisher/Gauss–Newton design。
- 所有方法取同完整噪声场的相应节点，利于配对；每seed只有一次测量噪声实现，没有噪声重复，尚不能分开估计网络异质性与测量噪声效应。
- 使用逐节点greedy选择，**不是固定预算下全局最优选点**。在n=12下相同算法公平，但目标不同可能有不同贪心次优程度；不可称最优M。可以后续小例穷举验证贪心差距，但当前先导未做。

## 2. 强基线与alternate task的准确含义

- activity：校准输入train下、采样时刻的完整r轨迹局部trace风险。
- stimulus_state：与q相同刺激/对照输入及时间窗的完整r轨迹trace风险，包含q的任务条件，是合理强基线。
- response_state：先对每节点的刺激减对照r响应**时间积分**，形成N维积分响应向量，再最小化该向量的平均后验方差。它**不是完整差分时间轨迹重建**；准确名称为“integrated-response-vector design”。q正是其一个坐标，因此不是弱任务错配基线。
- response_state会为刺激节点本身的大积分响应付出设计预算，而q读出刻意与刺激节点不同。这是平均任务与单目标的合法差别，亦是预期的已知目标设计几何，不是新机制。
- shuffled_goal同时把stim移到(stim+1)%N、readout移到(readout+1)%N，**不是只打乱readout的shuffle**。应叫alternate-task design/other-task design；其效果可以支持任务特异性现象，不能当严格置换随机化检验。
- 数据已保存other_q_error。all/M=3时alternate-task自身RMSE约1.006e-4，而goal对该alternate task约8.459e-4；all/M=6分别约1.014e-4与4.528e-4。交叉评价符合任务对齐的直觉，但仍是另一刺激＋读出的联合任务。
- exclude_endpoints只排除原任务stim/readout，未排除alternate task的端点。因此alternate-task设计在自己任务上的直接测量机会不同，排端点pool下的交叉任务比较不能单独归因于goal alignment。

## 3. 指标重算：必须区分两种风险加权

normalized_q_rmse=\(\sqrt{mean(e_s^2/v_{prior,s})}\)，其中v是theta0处的局部delta-method prior variance，**不是实际抽样估计的prior q variance，也不是按真实响应幅度归一**。它给低局部prior方差任务较大权重。12个seed中未触发1e-12 floor，因此排名差异不是floor造成。

| Pool / M | Goal绝对RMSE | Activity | Response-vector | Random | Parameter | Goal归一RMSE | 归一意义下的备注 |
|---|---:|---:|---:|---:|---:|---:|---|
| all / 3 | 0.0002585 | 0.0026690 | 0.0022389 | 0.0024465 | 0.0022580 | 0.3496 | 两种聚合均较好 |
| all / 6 | 0.0002614 | 0.0013438 | 0.0007402 | 0.0017524 | 0.0013678 | 0.2491 | 两种聚合均较好，但绝对误差由少数seed支配 |
| exclude / 3 | 0.0020140 | 0.0026885 | 0.0024473 | 0.0024172 | 0.0023063 | 0.6057 | 两种聚合较好，配对不确定性仍大 |
| exclude / 6 | 0.0024219 | 0.0022879 | 0.0024235 | 0.0021961 | 0.0018460 | 0.6252 | 归一最佳；绝对RMSE输给activity/random/parameter，与response近乎持平 |

绝对RMSE量级可由少数大响应网络支配：seed111占all/M3 activity SSE的88.3%、random的82.8%；all/M6 activity的97.0%、random的98.3%。这不自动说明应排除seed111；它说明权重与网络异质性必须公开。

作为**事后影响诊断而非新主结果**：去掉seed111后，all/M6的goal RMSE约2.438e-4、activity2.421e-4、random2.389e-4，优势消失；response约7.511e-4。不得据此删掉不利seed，也不得忽略此敏感性只报“6倍提升”。

配对bootstrap是每seed绝对误差差的均值，而非RMSE差；不能用其区间给RMSE改善显著性背书。12个异质seed、多个方法/预算/pool对照，区间只能保持exploratory标记。goal_wins用diff<0，ties用abs(diff)<1e-12，计数可能重叠，解读胜/平应以容差互斥定义为准。

## 4. 其他叙述限制

- all/M3的goal含readout 10/12，response-vector仅1/12；all/M6为12/12对3/12。直接读出节点可测时的优势明显，但排端点后尤其M6优势减弱；不能声称已排除端点便利解释。
- 每seed只生成一个原任务和一个alternate任务，没有同J上的任务族交叉验证，尚不足以说对任务家族普遍成立。
- q的12个真值绝对量级跨约200倍，局部prior方差跨约7200倍；归一风险与绝对风险回答不同问题，二者都应保留。
- 后验q_variance是MAP处Gauss–Newton＋prior近似，忽略残差二阶项/多模态，不是精确posterior。n=12的95%coverage只能作诊断，不能证明校准。
- 线性bias-only差分null通过，梯度严格0、q范围约1.77e-16；这排除一类实现错误，不证明非线性结果新颖。
- dt/2仅在一个固定检查seed17上验证（q相对改变约0.35%），不是全12例积分收敛审计。source里的模拟与truth同Euler网格，属于模型内合成验证，未检验求解器/模型失配。
- J已知、gain/bias未知，prior名义与truth分布匹配、无过程噪声；未知J、结构误差、测量模型误差、生物非平稳性都未验证。

## 5. 是否值得继续

值得做一轮小而有约束的机制核查，**不值得仅凭当前结果扩成“新方法”论文**。最有价值的后续不是加网络数求显著性，而是：固定目标族与风险加权，补测量噪声重复；核查积分向量与差分轨迹两种强基线；以预登记跨任务矩阵区分已知targeting几何和端点便利；在少量例比较greedy与穷举；再看真正困难的模型局部性/失配是否留下可研究命题。

当前最稳妥一句话：**在12个模型内合成实例中，prior-nominal目标设计可改善若干预算/可测节点设置下的指定积分响应预测；这种效果依赖端点可测性、任务尺度与风险加权，排端点高预算下没有一致绝对误差优势。**

### 审计后补充：新增validation.json已读回

root随后增加的`work/pilot/main_v1/validation.json`现已单独核对。其time_step_audit覆盖全部12个teacher，因此上面关于“仅seed17”的限制仅描述原始summary/checks，**已被新增诊断补足**。12个teacher的q在dt/2下最大相对变化约0.405%，是更好的真值积分稳定性证据；尚未等同于全MAP拟合、选点及方法排名都在半步长重新运行。新增6节点枚举中3个例子的目标梯度为零，另2个非零例greedy与穷举同解；不能据此宣称12节点所有预算都全局最优。
