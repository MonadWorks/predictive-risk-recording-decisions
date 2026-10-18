# Fig.8 SVD基线与第二模型：独立定义和审计

2026-10-16。仅写本文件与独立参考`work/baseline_reference.py`；没有修改主实验或outputs，没有装包。本审计不等于原图复现。

## 1. 直接来源与核验范围

Beiran & Litwin-Kumar (2025), *Prediction of neural activity in connectome-constrained recurrent networks*, [正式论文](https://doi.org/10.1038/s41593-025-02080-4)，公开源码固定提交`f5f397b88f8dd5c2a5c13558ce6039194a284586`。本次精读本地`nn_fig8_plots_de.py`约138–181行、`nn_fig8_plots.py`同一块，以及`nn_fig3_trainStudents_abc.py`约478–545行。Fig.8 G/H脚本主要加载预生成训练/选点结果，所需teacher/训练脚本不完整，因此不能声称已经精确复现Fig.8非线性选点协议。正式网页当前只返回订阅预览，PMC遇验证码；未绕过访问限制。下文是可从公开数学与固定源码核实的定义。

## 2. 原线性特例：归一化行＋SVD＋正交补

原源码线性稳态映射为

\[
A=(I-J)^\dagger J\in\mathbb R^{N\times P},\quad A=U\Sigma V^\top.
\]

把参数扰动当作Euclidean各向同性，完整activity平均平方误差正比于`||A||_F²`。记录一神经元，对应一个精确线性约束`a_i δθ`。已选约束张成空间的正交补投影记P，初始P=I。候选残余行`a_iP`，若非零，则令

\[
v_i={Pa_i^\top\over\|a_iP\|_2},\quad
s_i={\|Av_i\|_2^2\over\|A\|_F^2}
={\sum_j\sigma_j^2(v_j^\top v_i)^2\over\sum_j\sigma_j^2}.
\]

选择最大`s_i`，更新`P←P−v_i v_iᵀ`。这恰好是删除一个残余参数方向带来的完整输出误差下降。剩余风险为`||AP||_F²/||A||_F²`。源码将候选行标准化、与原始右奇异方向对齐并按原始奇异值平方加权，等价于这个公式。

注意：原脚本在候选数组删除行以后保存的是当前局部索引，不是自动映射回原节点ID。独立实现应维护原ID，不能照搬`savIx`的局部索引；原脚本worst/random块还存在对零值过滤后的索引使用细节。本研究只需要数学定义明确的best greedy，不需要复制这些脚本细节。

**该法不是本项目的Bayesian trace criterion。** 它把已选方向当精确约束，基本形式没有观测噪声R、先验精度叠加，也不按测量幅度连续折算信息。不要将`trace(G C_M Gᵀ)`与其混称。

## 3. 本项目finite-time的合理适配：神经元块，而非均值时间行

一个节点不是只给一个数，而是给多trial、多时点轨迹。定义已知名义参数theta0处：

- `F_i = ∂h_i / ∂theta`：节点i所有实际校准观测拼接，形状(n_obs_per_node,P)。
- `G = ∂Y / ∂theta`：待重建的完整activity，形状(n_target,P)。必须声明Y为完整校准轨迹、刺激轨迹，还是全积分响应向量，三者不同。
- 若比较原始参数Euclidean几何，直接用F_i/G；若为了gain/bias不同量纲进行先验白化，固定`theta=theta0+Lz`、`z~N(0,I)`，对**所有**F_i和G一致右乘L。白化是本研究适配，不是原源码新增了先验后验。

取`F_iP`的右奇异向量中保留方向，形成列正交基V_i；则

\[
 s_i={\|GV_i\|_F^2\over\|G\|_F^2},\quad
 P\leftarrow P-V_iV_i^\top.
\]

这是一节点携带一块约束的无噪声几何推广；在每节点只有一行且F=G=A时精确退回上节。不要把多时点行简单平均后再套原法，平均会消掉相反符号的敏感方向。

### 重要失败边界

有限时间单节点块有时点数多于P时，经常已经理论满秩或数值近满秩。无噪声投影法会在第一个节点后把所有方向当作已知，**即使很多奇异值微小、在实际噪声下完全不能识别**。这是协议不同造成的适用性边界，不是算法胜负的公平证据。

建议冻结相对阈值`rtol=1e-8`和绝对阈值`atol=1e-12`；相对阈值使用每个**原始**块最大奇异值，不用投影后残差作分母（否则浮点残渣会被再次升格为有效方向）。记录每次候选增量秩、risk和投影幂等误差。若所有候选首轮即满秩，则如实标记此基线在该协议退化；可做预先声明的阈值敏感性诊断，但不能挑阈值让结果好看。

噪声感知的“软投影”应使用`C=(C0^-1+F_MᵀR^-1F_M)^-1`，属于本项目现有GO-A-opt基线，不再冒称原Fig.8算法。建议主表将本法称为**local noiseless block-SVD adaptation**，原始单行线性sanity单独证明退化一致性。

## 4. 独立小数值校验（已运行）

命令：`/opt/homebrew/bin/python3.13 work/baseline_reference.py`。只用NumPy，耗时约0.6秒；未训练神经模型。

| 检查 | 结果 |
|---|---:|
| 随机8×5矩阵，标量SVD式与独立greedy第一选择 | 均为原候选2 |
| 第一次归一化risk下降 | 0.4585621766 |
| 5次投影最大幂等缺陷 | 5.25e-15 |
| block满秩时第一节点后风险 | 3.82e-31（预期退化） |
| rank-two因式乘法与密集J Euler步最大绝对差 | 1.11e-16 |
| Fig.3族协方差最小特征值 | 0.1330761319 |
| seed8的100个teacher gain负值数 | 7（正确，不能截断） |

运行时本机已有NumPy2.2.5/BLAS对两个密集matmul发出了divide/overflow/invalid warning，但输出全部finite且上述独立等价断言通过；设置BLAS/VECLIB线程为1后warning仍在。不能把warning掩掉就当环境已完全合格。建议正式环境换用新venv/NumPy版本重跑此小检查；若仍出现，用独立einsum/纯内积复核并记录后端。参考文件没有抑制warning。

## 5. 第二基准：N=100已发表rank-two tanh模型家族

选它的意义：改变第一先导的activation、gain参数化、连接谱和工作点，检验近似设计的失败是否只属于小型contractive softplus模型。它是**已发表模型家族的独立适配**，不是第二份真实数据，也不是原Fig.3结果重现。

\[
J={m_1n_1^\top+m_2n_2^\top\over N},\quad
r_i=g_i\tanh x_i,\quad
\tau\dot x=-x+Jr+u(t).
\]

原协议可保留的部分：N=100、rank2、tau=.5、dt=.05、无bias、teacher `g_i~N(1,.9²)`允许负值；m/n四维Gaussian协方差按本地来源审计完整定义。独立helper保留该协方差分布（包括首次PSD后多inflate一次的分布细节），使用`default_rng`，所以不声称同seed逐位一致。

| 项目 | 第一先导 | 第二基准建议 |
|---|---|---|
| 非线性输出 | exp(logg)·softplus(x+b) | g·tanh(x)（可正可负） |
| 未知参数 | logg与bias，共2N | 直接gain g，共N；bias严格0 |
| nominal/prior | logg=0,b=0，Gaussian sd=.18 | nominal g=1；Gaussian gain prior sd=.9 |
| J | 稀疏Dale、小谱范数、N12 | 发表rank2 Gaussian族、N100；非Dale |
| 内部时间 | dimensionless tau1 | tau=.5、dt=.05 |
| 原始动力学 | contractive受驱 | 原族可产生limit cycle；不是保证所有seed都振荡 |
| 观测 | synthetic有噪声rate | synthetic有噪声signed output，不能称生理非负firing rate |

必须明确的适配：加入校准外输入与配对刺激以定义本研究q；原Fig.3主要自主振荡，无同样的刺激任务。用Gaussian gain MAP和统一已知x0作公平控制，原文则7000epoch Adam、噪声.001、teacher burn-in后给student同一起点。本研究若取消过程噪声、采用观测噪声与已知随机非零x0，均写入方法，不能叫原协议复现。尤其**x0=0且u=0会导致tanh网络永远0，gain完全没有信息**，所以首轮应明确使用预先冻结的非零随机x0和已知非零校准输入。

### 可以立即实现的轻量协议

1. N100、r2、seed与任务ID独立随机流。先2个seed测时间，不用它们决定哪种方法赢。
2. dt=.05、tau=.5、T=10（200步）用于算力预估；发表窗口20可作为冻结正式窗口，dt半减检查不能略。T=10是适配，不宣称沿用原窗口。
3. 校准2trial、3个预定输入通道；所有方法共享同一校准输入/measurement realization。记录预算8/16节点，两端点能否观测仍分protocol。
4. 目标q：事先选择stim node、readout node，已知单通道pulse与相同x0/noise-freebaseline配对，q=积分signed output差。不要基于truth挑响应最大任务。
5. g直接在实数域拟合，加显式Gaussian prior；不能使用exp(logg)限制正值。所有方法同一MAP初值/最大迭代数/停止阈值。
6. 第一轮小规模在同一N下先比较scalar/vector×nominal/ensemble四组及random；SVD只作为上述有边界的几何适配。由于原gain分布宽，局部失效可能更强，但这是待检验而非先验结论。

### factorized前向敏感性

令S=∂x/∂g，D=∂r/∂g，则

\[
D=\operatorname{diag}(\tanh x)+\operatorname{diag}(g\odot\mathrm{sech}^2x)S,
\quad \tau\dot S=-S+M(H^\top D)/N.
\]

每一步用N×2和2×P因式乘法；无需N×N×P算子。复杂度约O(NPr)，存完整200×100×100敏感性约16MB/trajectory（float64），2trial约32MB，完全可分stream降低内存。是否总运行可控应通过2seed实测再决定正式seed数，不能只凭规模公式保证耗时。

## 6. 给主实验的决策建议

优先实现noise-aware 2×2与独立测试种子，不要等“完全复现Fig8非线性”才推进。把原单行SVD数学一致性作为独立sanity，把finite-time block扩展单列且报告rank退化。第二模型必须保留signed直接gain与zero bias；如果为省事仍用softplus/loggain，就没有真正建立此第二模型基准。
