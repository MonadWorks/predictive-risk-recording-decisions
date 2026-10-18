# Research v2: constrained neural observation and predictive risk

2026-10-16。完整的模拟研究记录，不是已获证实的新方法或真实生物验证。先读上一级的《阶段二研究报告》和《论文研究稿_v2》；本目录附带副本于`documents/`。

## 已完成的研究与结论

| 记录目录 | 独立J | 评价行 | 实际MAP调用 | 核心秒数 |
|---|---:|---:|---:|---:|
| development_run | 8 | 19,200 | 5,696 | 25.4 |
| holdout_run | 40 | 129,600 | 38,610 | 356.0 |
| risk_forecast_followup_run | 40个新J | 6,480 | 3,006 | 17.5 |
| rank2_n100_refined_run | 8个新J | 3,072 | 1,436 | 693.1 |

四阶段合计158,352行、48,748次实际MAP调用，最高层独立单位为96个J。随机集合、真值、噪声和目标嵌套在J内。合计不含正控制、诊断和smoke；`package_smoke_run/`是当前交付源码的额外执行检查。

第一轮主ES−LS相对MSE差−3.74%（97.5% CI −18.48%至+12.12%），EV−LV +2.69%（−2.95%至+11.51%）。独立风险预测主score差−0.45565（95% CI −1.15857至+0.02367）。两轮主要证据都没有建立稳定集合优势；100节点结果有条件变化，8J全探索。所有正式运行的拟合均成功、无fallback；数值诊断中的有限未收敛结果仍在诊断文件。

## 模型和来源身份

自写模型/统计代码，结构谱系来自Beiran & Litwin-Kumar, Nature Neuroscience 2025, doi:10.1038/s41593-025-02080-4。目标准则是已有GO-OED的局部近似，非新原则。

主模型为N=12 softplus率网络，未知log-gain/bias。第二家族N=100 rank-two tanh使用已发表分布，但自己的初值、校准输入、噪声与MAP均为适配；不是原图复现。负gain按该数学分布保留。使用精确低秩状态分解、解析ZOH输入滤波与RK4阶段积分。`run_rank2.py --substeps 2`必须用于该协议，不能直接用默认Euler `run.py`冒充相同结果。

未使用真实神经活动、经验连接矩阵或活体干预数据。未分发未明确授权的上游代码/权重。SVD参考只在自身无噪声线性内部状态条件下校准，不放到带噪rate模型排行榜中作“优于原文”的证据。

## 环境

实际环境位于工作区`work/research-v2-env`，Python3.13.2，`include-system-site-packages=false`。`requirements.lock`包含全部解析依赖；`environment/`保存配置、平台和pip check回执。核心运行不需要GPU。锁定NumPy2.2.5、SciPy1.15.2、Numba0.61.2、Matplotlib3.10.1。安装依赖需要正常网络；没有修改全局Python。

在解压目录建立独立环境，例如：

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip check
```

设置`NUMBA_CACHE_DIR`、`MPLCONFIGDIR`、`XDG_CACHE_HOME`到本目录的临时子目录即可。运行器记录编译预热和实验时间，统一限制BLAS线程为协议指定值2。Mac M4 Max/36GiB的速度不能保证在其他机器相同。

## 先验证交付文件，再进行新运行

只读完整性核查不需科学计算依赖：

```sh
python3 validate_package.py
```

`SHA256SUMS.json`记录交付时文件哈希；`package_integrity.json`核对原始行数、J、协议及源码快照。哈希只能证明记录一致，不能认证生物结论。

原运行目录拒绝覆盖。下面命令从包根目录执行，使用新的输出目录；示例假定已建立`.venv`。数值检查和独立控制会写固定名字的检查文件，为保留交付记录，建议在整个包的副本中执行它们。

```sh
NUMBA_CACHE_DIR="$PWD/scratch/numba-cache" .venv/bin/python checks.py
NUMBA_CACHE_DIR="$PWD/scratch/numba-cache" .venv/bin/python rank2_refined.py
.venv/bin/python run.py --protocol smoke.json --out rerun_smoke
.venv/bin/python run.py --protocol holdout.json --out rerun_holdout
.venv/bin/python analyze.py --run rerun_holdout --out rerun_holdout_analysis
.venv/bin/python run_rank2.py --protocol rank2_n100_refined.json --substeps 2 --out rerun_n100
.venv/bin/python analyze.py --run rerun_n100 --out rerun_n100_analysis
```

核心固定种子和生成协议可复现统计输入，但跨平台浮点/优化终止可能不逐位相同。`run.py`自动保存执行时间、协议、core源码快照和哈希；rank2入口另存后端源码快照。所有冻结均为本地执行前记录，未声称外部公开预注册。

独立风险预测复跑：

```sh
.venv/bin/python run.py --protocol risk_forecast_followup.json --out rerun_forecast
.venv/bin/python forecast_analysis.py --run rerun_forecast --out rerun_forecast_analysis --freeze risk_forecast_followup_freeze.json
```

这里`--freeze`引用原假设冻结回执；新运行有自己的execution_freeze。不要把复跑称为新增独立研究，seed未改变。

已有结果的只读分析复算不必重新拟合：

```sh
.venv/bin/python analyze.py --run holdout_run --out recalculated_holdout
.venv/bin/python analyze.py --run rank2_n100_refined_run --out recalculated_n100
.venv/bin/python forecast_analysis.py --run risk_forecast_followup_run --out recalculated_forecast --freeze risk_forecast_followup_freeze.json
```

## 目录索引

- 根目录`.py`是独立实现；`*.json`协议以实际冻结版本为准。没有用最初协议生成器重新生成后来的修订协议。
- 每个`*_run/`含results.csv、designs.json、models.json、status、环境、协议/源码哈希及执行源码快照。rank2另含backend快照。保存全部有限最后迭代与fallback标记，原始记录不能静默删点。
- `development_analysis/`、`holdout_analysis/`、`rank2_n100_refined_analysis/`是网络层配对分析，含汇总、cluster区间、LONO、完整作图数据、图注、PNG/PDF。
- `forecast_followup_analysis/`固定点预测/记录集合，只比较两个风险预测，含一致MSE评分的独立复算资料。
- `mechanism_results/`只读开发集，含Taylor余项、选点Jaccard、读出包含率和完整分母。其脚本按相对路径读取`development_run`，不读取holdout。
- `linear_risk_control_results/`非退化线性Gaussian正控制：144目标/设计格、每系统8192次MC。`svd_reference_results/`是原准则的独立几何校准。各有README和源数据。
- `diagnostics_results.json`保留粗Euler失败、有限集合稳定性和小迭代预算的MAP诊断；`rank2_refined_checks.json`记录修正后独立RK4核查。它们不参与主方法排名。
- `reviews/`保存设计、统计和独立代码/结果审计。**早期审计的建议不等于最终执行合同**：最终以`documents/实验方法与报告规范_v2.md`、实际协议及执行快照为准。N100文案清理后的结果不变验证见分析复核记录。
- `logs/`保留正式运行日志。原报告中的绝对路径是本机历史位置，不是算法输入；解压后按本说明相对路径运行即可。

统计重复单位、原始/标准化权重、失败政策、两个97.5%主区间与其他探索95%区间、先验风险的近似身份均见方法合同。无效标准化目标保留原始结果，完整标准化格记NA；不能为了改善排名调整floor或删目标。

每幅图提供300dpi PNG、嵌字矢量PDF、数据CSV和图注。SVD参考中36条平台浮点警告连同等价内核检查保留；未隐藏为“全局无警告”。环境缓存告警与科学运行失败是不同事项。

未进行摘要投稿、注册或外部联系。下一步应先判断论文贡献，不能因有158,352行记录便认为新颖性已经成立。
