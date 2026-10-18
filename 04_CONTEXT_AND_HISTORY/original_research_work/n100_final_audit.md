# N100 refined 最终独立审计

审计为只读核对与独立复算，没有删除实例、修改源文件或重跑研究实验。

## 完整性与冻结

- 8 个 J（8000–8007）全部完成，3072 条评价记录，1436 个独立 MAP 调用（按 J / truth / noise / nodes 去重），与 status 完全一致。运行 693.140 秒。
- 独立核对192个 J×pool×budget×method单元，每单元 truth/noise/target/design_repeat 的完整笛卡尔积，无缺失或重复；所有节点预算与共同端点排除正确；同一 J/truth/target 的 q_true 不随噪声或方法变化。
- backend 的 6 份冻结源码逐份 SHA256 匹配；核心 4 份 source_snapshot 与其哈希及 backend 快照一致；protocol 的原始字节 SHA256 与两个执行冻结及 protocol.sha256 均一致。
- 当前工作副本与 backend 6 个哈希的逐份比对：models.py: True, design.py: True, inference.py: True, run.py: True, rank2_refined.py: True, run_rank2.py: True.
- 冻结明确为本地执行时记录，并非公开预注册。协议 phase 为 exploratory_refined_published_model_family；primary_stratum=null、primary_comparisons=[]，分析 primary_effects=[] 且 confirmatory eligible=false。

## 有限失败与数值质量

- 所有主要预测、误差、风险、MC 尺度、拟合目标等字段均有限；0 条未收敛评价记录，来自 0 个独立 MAP 调用；fallback=0。
- 冻结 inference.py 及 protocol 均明确：有限但达到迭代上限的 last iterate 保留并标 optimizer_success=False，异常才回退名义均值。本运行没有此类实例；代码和分析均没有剔除这类实例的分支。

| J | MAP调用 | 未收敛调用 | 评价行 | 未收敛评价行 |
|---|---:|---:|---:|---:|
| 8000 | 180 | 0 | 384 | 0 |
| 8001 | 172 | 0 | 384 | 0 |
| 8002 | 172 | 0 | 384 | 0 |
| 8003 | 184 | 0 | 384 | 0 |
| 8004 | 180 | 0 | 384 | 0 |
| 8005 | 184 | 0 | 384 | 0 |
| 8006 | 184 | 0 | 384 | 0 |
| 8007 | 180 | 0 | 384 | 0 |

- 未收敛调用的 nfev：[]，本次全部1436次调用均返回 optimizer_success=True。此状态是优化器终止条件，不等于找到全局最优或全部生理参数被正确识别。
- 24 个 J×target MC 尺度均唯一、正且大于固定 floor；范围 2.0295503e-06 至 0.0034668743。所有 normalized_squared_error 独立复算正确。
- 使用冻结后端、固定 seed 和32个 prior MC draws 独立重算 J8000 的三个尺度，最大绝对差 0。这是32次 Monte Carlo估计，不是精确总体方差；尺度抽样误差未进入当前 bootstrap。
- refined 数值验收基于独立诊断种子1880/1881：sub2 对 sub8 的全网络 Q 最大相对误差约1.4e-5、G约4.22e-5，完整密集小模型 RK4 与方向导数检查通过；这些是有限诊断案例，并非对所有真值、先验粒子和拟合点的统一误差上界。

## 独立统计复算

- 从原始 CSV 分 J / pool / budget / method 独立聚合，全部24个方法分层的 MSE、normalized MSE、MAE 与 summary 一致，最大绝对差 0。
- 未导入 analyze.py。以固定 seed870231 独立重建10000次8-J配对 bootstrap：全部 MSE/normalized MSE 比较和2×2交互的点估计及95%区间匹配，最大点差 0，区间端点差 2.22e-16。
- 下表保留两个主要关注的探索性比较；负值倾向第一个方法。所有区间为点对点95%，未作跨层或跨指标多重比较控制。

| Pool | M | 对比 | ΔMSE | 95% CI | 相对MSE变化 | 删除单个J后的ΔMSE范围 |
|---|---:|---|---:|---|---:|---|
| all | 5 | ensemble_scalar - local_scalar | -1.5175e-05 | [-5.0932e-05, 6.7406e-06] | -39.4% | [-2.0368e-05, 1.6604e-06] |
| all | 5 | ensemble_vector - local_vector | -8.5087e-05 | [-0.00025088, -9.7218e-07] | -85.5% | [-9.7276e-05, -2.4805e-06] |
| all | 10 | ensemble_scalar - local_scalar | -1.4695e-06 | [-4.4099e-06, 2.3429e-07] | -11.0% | [-1.7798e-06, -6.2848e-08] |
| all | 10 | ensemble_vector - local_vector | -3.4563e-07 | [-1.0668e-05, 7.805e-06] | -2.5% | [-2.9654e-06, 4.1091e-06] |
| exclude_endpoints | 5 | ensemble_scalar - local_scalar | -2.5457e-05 | [-6.1737e-05, -2.4994e-06] | -15.4% | [-3.0283e-05, -8.4482e-06] |
| exclude_endpoints | 5 | ensemble_vector - local_vector | -2.0384e-05 | [-3.7024e-05, -3.6775e-06] | -13.6% | [-2.4551e-05, -1.6074e-05] |
| exclude_endpoints | 10 | ensemble_scalar - local_scalar | 1.15e-05 | [-4.8523e-06, 3.0389e-05] | 9.5% | [4.3416e-06, 1.5582e-05] |
| exclude_endpoints | 10 | ensemble_vector - local_vector | -3.5666e-05 | [-7.8402e-05, -5.7469e-06] | -22.8% | [-4.097e-05, -1.6353e-05] |

## 判读边界与文档问题

- 这是8个独立合成 J 的探索性模型族/尺度扩展，不能替代、覆盖或补救另一主研究的冻结检验；不能把3072评价行当作 n=3072，也不能把效应更有利的层升格为主结果。
- 原始与标准化指标的区间不一定得出相同方向，应并列呈现；8个J下 bootstrap和影响诊断仍较脆弱。
- L32 是基于独立选点稳定性诊断选择，不能宣称已证明集合收敛或新算法最优。已知连接矩阵、原始signed gain、已知输入与x0、零阶保持输入、共用 MAP、RK4积分响应等适用范围应在正文写明。
- 轻微文档模板问题：summary.analysis.primary_interval 仍写通用97.5%主比较说明；figure_captions_and_analysis.md 还描述本运行不存在的 primary_paired_effects / primary ECDF 等图。实际 primary_effects为空、所有 paired_effects 的 primary=false，数值分析未因此升格，但发布前应将模板说明改成本运行全探索性及真实文件清单。
- 审计未见阻断完整性或统计复算错误。对优化收敛、Monte Carlo分母误差和外推范围应保留上述限制。
