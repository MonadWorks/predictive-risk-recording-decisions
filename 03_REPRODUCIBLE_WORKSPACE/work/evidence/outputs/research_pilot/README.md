# 合成神经网络先导：可重跑实验包

2026-10-16。独立实现；数据全部为模拟生成。用于研究可行性与数值核查，不是生物验证、原论文复现或新方法交付。

## 已运行什么

- `main_v1/`：冻结的12个网络、336次拟合；种子100–111，N=12，M=3/6，2个候选池，7种准则。
- `protocol.json`在该次正式运行前写入，`protocol.sha256`为其散列；`source.sha256`对应本目录`pilot.py`。
- `results.csv`：全部实例，不删除不利网络；`summary.json`：聚合、探索性配对区间及检查。
- `validation.json`：后续数值/影响诊断，与冻结主实验区分；不作为新主结果。
- `environment.json`：实际Python与直接科学依赖版本、运行平台、包来源。

主要发现是：方法排名受端点可测性、风险权重和少数网络实例影响。当前不足支持普遍优势或新方法。`shuffled_goal`实际同时改变刺激与读出，是alternate-task参照；`response_state`是全节点**积分响应向量**，不是完整差分时间轨迹。

## 实际环境

Apple M4 Max，36GiB RAM；Python 3.13.2、NumPy 2.2.5、SciPy 1.15.2、Matplotlib 3.10.1、threadpoolctl 3.6.0。主计算8.02秒，不含制图、依赖准备或调研。线程上限设为2；此平台`threadpool_info()`返回空列表，不能据此声称已经观察到BLAS实际线程数。

本机已建立`work/research-env`专用venv入口，以`--system-site-packages`复用已安装包，没有改全局环境。它不是从空环境独立安装验证的环境。`requirements.txt`固定直接依赖，未锁定全部传递依赖和二进制构建。

## 重跑

在这个目录下，用已具备上述依赖的Python执行。输出另存新目录，保留`main_v1`：

```sh
MPLCONFIGDIR="$PWD/.mpl-cache" XDG_CACHE_HOME="$PWD/.cache" python3 pilot.py --out rerun_100_111 --teachers 12 --seed-start 100 --wall-limit 120
```

本机可用的解释器为`/opt/homebrew/bin/python3.13`；专用venv解释器位于工作区`work/research-env/bin/python`。其他机器可先创建普通venv并安装直接依赖：

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

后一安装流程是可复建建议，本次没有从空环境重装验证。若未完成全部12个网络，应按`completed_teachers`和CSV行数报告部分结果，不能沿用336次的结论。

只重算冻结CSV的诊断和小型数值检查：

```sh
python3 validate.py --audit-out validation_rerun.json
```

该脚本核对源码散列、336条记录、有限值、12个teacher的步长变化、跨任务风险、逐例影响和小网络穷举。它不会重做336次拟合，也不会覆盖原诊断。固定输入下的所有拟合步长稳健性、完整后验校准、原Fig.8算法、经验连接组和真实干预数据仍未验证。

## 方法来源与适配

基础率模型取材于[Beiran & Litwin-Kumar 2025](https://doi.org/10.1038/s41593-025-02080-4)所研究的模型家族；选点准则来自既有[目标导向实验设计](https://doi.org/10.1088/1361-6420/aad210)。本程序由我们独立书写，没有分发作者仓库代码。N、J分布、输入、参数先验、正增益参数化和初值均为本先导自己的简化适配。

设计只用名义先验θ=0，没有共同先导数据D0，也没有用真值初始化。拟合使用所选节点测量。真正评分为非线性预测响应，不是被优化的局部方差。所有时间/输出无量纲。

细节及限制见上一级《研究收敛与纵向调研》《先导实验独立审计》。先导不能替代下一轮预登记机制研究。
