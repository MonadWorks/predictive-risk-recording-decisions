# 研究协作入口

当前主稿：**Predictive Risk and Recording Decisions in Partially Observed Neural Networks**。这是同一篇论文在原始比较基础上的扩展。

1. [当前论文 PDF](01_READ_CURRENT/paper_current.pdf) 与 [正文源稿](01_READ_CURRENT/paper_current.md)：正文按端点收益、信息机制、内部组合和第五个记录展开；原始准则比较与完整结果保留在补充分析中。
2. [README](README.md)：最新证据范围与结论。100-unit 部分为 8 个先导网络和七组各 40 个独立基础网络；同一组网络的重复分析不重复计数。
3. [重现与代码入口](02_重现与代码入口.md)：新实验的原始数值记录、冻结方案、分析与编译命令。
4. [研究主线与版本审计](01_研究主线与版本审计.md)：原始交接的历史背景。

本次扩展的核心正向结果是固定预算下共同记录刺激端和读出端的预测收益。机制实验进一步连接预测范围、记录精度与具体参数组合，并验证第五个记录能否约束内部组合；额外选择算法的预测收益仍不确定。

[图形摘要 v5](01_READ_CURRENT/graphical_abstract.pdf) 保留原有风险准则比较的图文，尚未重绘为端点与机制结果的摘要。历史材料位于 `02_RESEARCH_FOUNDATION/`、`04_CONTEXT_AND_HISTORY/` 和 `05_AUDIT/`；其中版本、投稿草案和检查记录各有自己的时间范围。

从根目录执行 `python3 validate_handoff.py` 可检查文件一致性、历史数值链路及新增实验的数值汇总。论文尚未投稿。
