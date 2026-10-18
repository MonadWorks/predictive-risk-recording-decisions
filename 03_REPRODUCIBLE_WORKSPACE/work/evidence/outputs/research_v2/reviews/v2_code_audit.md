# v2 独立代码审计（只读主实现）

审计对象：`models.py`, `design.py`, `inference.py`, `run.py`, `checks.py` 及 development / holdout / rank2_n100 协议。未运行正式结果，未安装包，未修改主实现。

## 结论

未发现会使当前设计比较失效的敏感性、观测轴、设计数据泄漏或拟合 cache 错误。正式 holdout 启动前应修正下列协议/验收问题；它们不要求修改科学模型来追求更好结果。

1. **N100 协议主层为空**：`rank2_n100.json` 继承了 `condition=broad, budget=3`，实际只有 `published_gain` 和预算 5/10。应明确将该运行定义为探索性尺度/模型族检验，移除主比较标记，或另定义有效且预先声明的层。不可直接对不存在的主层生成“无差异”结论。
2. **补时间离散误差验收**：当前 checks 检查的是已离散模型的导数、因子化和独立实现一致性，没有检查 dt=.05 的连续时间近似精度。建议对预先固定、独立于 holdout 的多个代表案例比较 dt=.05/.025（必要时 .0125），保持相同物理时长、刺激边界和记录时刻，报告 Q、G 和主要设计选择稳定性。若将模型定义为离散时间系统而不声称连续模型复现，可明确降格，但原文 tau=.5 的 N100 桥接尤其需要此检查。
3. **冻结与开发边界**：运行时记录源码/协议哈希是可复现记录；独立 holdout 还需在查看其结果前明确冻结。开发集允许选方法，但选择后必须留最终 frozen protocol/source receipt，不能把运行后产生的 receipt 称作事前注册。

## 数学与实现检查

- softplus：`dr/dtheta = gain*sigmoid(x+b)*dx/dtheta`，log-gain 的直接项为 r，bias 的直接项为 gain*sigmoid。代码与该链式法则一致。
- rank2 tanh：gain=1+theta，直接导数 tanh(x+b)，不是误用 log-gain 的 r；允许负 raw gain，符合协议声明 N(1,.9²)。tau=.5 在状态和敏感性 Euler 步均生效。
- 敏感性状态更新先完整计算 dr 和 J dr，再按节点更新 S；不存在因就地更新造成的节点先后依赖。
- `left @ (right @ r)` 与显式 J 一致，checks 给出的误差约 4e-15。N100 的低秩加速不改变动力学。
- 参数标准化正确：设计中 F=D*sd/noise，g=G*sd，先验精度 I。MAP 在原参数中使用 prior precision diag(1/sd²)，两者一致。
- 集合公式是每个 particle 分别计算 `C_l=(I+ΣF_i,l'F_i,l)^-1`，再平均 `tr(C_l W_l)`，没有将平均信息矩阵求逆来代替所声明的目标。
- nominal particle 单独用于 local 方法；ensemble 使用其余独立 prior draws，不误把 nominal 当额外抽样。
- scalar 和 vector 使用同三个事前指定读出。vector 的 W 为三组 g 外积的平均，权重是相同的 raw-response 权重；它不是全 N 神经元目标，必须如实描述。
- readout/stimulation 的共同 endpoint 排除针对三个读出并集，对所有 scalar/vector/random 方法一致，避免每个 scalar 享有不同候选池。
- R/D 的节点轴与拟合观察轴匹配；`nodes` 排序后与 `observed[:,:,key]` 同序。非排序子集检查有意义。
- 缓存只在相同 network / condition / truth / noise 下、按完全相同节点集合复用，MAP 与目标 q 无关，所以重复设计共享一次拟合是公平的。不同噪声/真值下 cache 会重置。
- public_case / build_bank / recording_designs 接口无 truth 字段。model、truth、design、MC scale、random design、measurement noise 使用分离的 seed stream；所有方法共享同一个噪声 realization，属于配对设计，不是泄漏。

## 统计与报告限制

- 独立单位是 J；同一 J 的多个真值、噪声、读出、random repeat 必须先聚合或作为层级处理，不能当独立 n。当前协议已如此声明，分析器尚未审计。
- 40 个 holdout J 可以给出条件性的 Monte Carlo 比较；不能外推为真实连接组总体、生物样本或临床证据。N100 仅 6 个 J，适合探索性尺度检查。
- 两个事前主比较的 97.5% 区间与 Bonferroni family 约定相容；其他条件、交互和相关性都应标探索性。
- `wall_limit_seconds` 在整个 J 完成后检查，保留完整聚类，优于中途截断。若触发，应报告预定 N / 完成 N、固定顺序和 partial 状态；不能用已有结果补充选择额外种子或当作已完成 40 个 J。网络耗时可能与难度关联，因此不宜把 partial 当正式结果直接替代 full run。
- 若 `least_squares.success=False` 但结果有限，当前使用最后迭代点并标记失败；发生异常时才退回名义均值。该合理策略需在 protocol failure_policy 里准确写明，避免读者理解为任何 optimizer failure 都回退。
- MAP covariance 是局部 Gauss–Newton / Laplace 近似。95% coverage 只能作为诊断，不是已校准后验。variance、passive rollout 的 finite 检查也可更完整。
- 结构/激活函数、x0、输入和噪声模型均已知，无结构错配；有限真值偏置不是完整的模型错配研究。不能将该结果推广到未知 connectivity 或真实脑刺激预测。
- reachable 只依据非零 J 的图路径，不保证 q 具有实质大小；raw MSE 主指标应保留所有案例，scale_floor 仅保护次指标，不可借此选择性丢弃难例。
- 多次 identical-particle 检查验证集合退化等价，但不证明贪心全局最优；6 节点确切子集检查只验证一个实例，应报告 regret，不作一般最优性主张。
- 输出目录保护目前只检查 status.json；若进程在第一次完整 J checkpoint 前崩溃，再用同目录会覆盖部分 protocol/source receipt。发布时建议使用新目录并检查非空目录，或明确保留失败目录。

## 可支持的工作表述

可以称为：已知网络、有限记录和有限计算预算下，对局部预测风险设计的集合平均扩展进行合成基准与模型族桥接检验。尚不可以称为：新最优设计理论、真实神经干预验证、原文图复现或已证明临床/机器人效益。
