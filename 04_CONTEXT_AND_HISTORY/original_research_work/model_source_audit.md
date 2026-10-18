# connconstr 公开源码与小规模独立实现审计

审计日期：2026-10-16。只读取、下载小源码和静态检查；**未安装依赖、未执行模型、未下载大数据、未测运行时间**。

## 判断

可以从作者公开的 **Fig.3 rank-two tanh teacher** 开始独立的小规模实现：方程、参数分布、时间离散和最小原始网络规模 N=100 均可在小源码中核到。它是**生成模型基准**，不需要、也不应宣称使用真实生物活动数据。是否形成有价值的新论文取决于后续可证伪问题及结果；源码可得本身不构成新贡献。

三个经验 connectome 案例目前不能在“单文件不超过20MB”约束下保证原样复现：GitHub 不含必需 Data，Zenodo 唯一公开下载项为 **Code_NN.zip，238.1 MB**，本次未下载。仓库无明确软件许可证，宜引用论文方程、独立编写实现，不直接复制作者脚本进入拟公开项目。

## 1. 来源固定与文件可用性

- 论文：[Beiran & Litwin-Kumar, Nature Neuroscience 28, 2561–2574 (2025)](https://doi.org/10.1038/s41593-025-02080-4)。正式版 Fig.3 为维度与规模，Fig.5 为经验 connectome，Fig.6 为线性模型。不要套用早期预印本图号。
- 作者仓库：[emebeiran/connconstr](https://github.com/emebeiran/connconstr)。本次固定 HEAD：`f5f397b88f8dd5c2a5c13558ce6039194a284586`；后文行号均对应这一提交。
- 下载：[固定提交源码 ZIP](https://codeload.github.com/emebeiran/connconstr/zip/f5f397b88f8dd5c2a5c13558ce6039194a284586)。压缩 **141,394 bytes**；28个文件，解压源码合计 **738,092 bytes**。SHA256：`1579bbb5565e9d5434925ab8c549ae9bbc03683a7babb8f91c7ddd2e6e82d961`。
- 小源码保存于 `work/source_audit/pinned/`；文件清单 `zip_inventory.json`；散列与范围收据 `audit_receipt.json`；静态导入清单 `import_inventory.json`。均未执行作者模型。
- [README第7–13行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/README.md#L7-L13)明确：teacher/student 文件是示例；所有绘图要另下 Zenodo 的 Data 目录。仓库不含该目录。
- [Zenodo记录](https://zenodo.org/records/16618353)：页面检索显示 `Code_NN.zip` **238.1 MB**，MD5 `5572648bbaa9eb341c82680ed2390088`。本次未下载；其内部单文件大小和实际数组形状未核。API/导出端点读取未成功，不能补称已经审完归档内部。

## 2. 首选独立实现：Fig.3 rank-two tanh teacher

来源文件 [nn_fig3_trainStudents_abc.py](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig3_trainStudents_abc.py)，**23,734 bytes**。这是模拟网络而非动物记录。

令列向量状态为 x，神经元有效输出 q = g ⊙ tanh(x)。代码对应：

\[
J=\frac{m_1n_1^\top+m_2n_2^\top}{N},\qquad
\tau\dot x=-x+J\operatorname{diag}(g)\tanh(x).
\]

\[
x_{k+1}=x_k+\frac{\Delta t}{\tau}\left[-x_k+J\operatorname{diag}(g)\tanh(x_k)\right].
\]

| 要素 | 核实值 | 精确出处 |
|---|---|---|
| 非线性及递归形式 | tanh；class 中 gain 乘在递归输入与readout上 | 文件66行、120–125行 |
| 原文规模 | N∈{100,200,400,600,800,1000,1200} | [422–423、449–451行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig3_trainStudents_abc.py#L422-L451) |
| 观测神经元数 | {1,2,3,4,5,6,7,8,9,10,12,14,16,32,64}；前若干坐标为readout，不是自动优化采样 | 422、449、523–525行 |
| rank-two 构造 | 四维多元正态生成m₁,m₂,n₁,n₂；代码调整协方差至半正定 | 478–513行，具体协方差应按完整该段独立重述，不能简化为四个独立向量 |
| teacher gain | gᵢ=1+0.9zᵢ，zᵢ~N(0,1) | [478、515行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig3_trainStudents_abc.py#L478-L517) |
| gain范围 | **无正值截断，允许负值，无硬上界**。不能移植softplus例子的正增益约束 | 515行 |
| bias | 全零：sig_b=0，bt=0 | 558–562行 |
| 时间离散 | Δt=.05，τ=.5，因此Euler系数α=.1 | [529–545、581行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig3_trainStudents_abc.py#L529-L581) |
| 初始段 | 随机x，先模拟时间0≤t<60，共1200状态采样 | 529–542行 |
| 后续窗口 | 0≤t<20，共400状态采样，起点接前段末状态 | 544–550行 |
| student初始gain | 1+10⁻⁵×.9z，接近1；不是teacher gain分布 | 573–579行 |
| student拟合变量 | 只训练gain，bias、J、输入/输出权重、初始状态均固定；Adam，lr=.005，7000epochs | 602–608、632–641行 |
| 训练噪声 | teacher与student构造均指定noise_std=.001；class每步直接加σ×标准正态，不额外乘√dt | 119–123、602–612行 |
| 原运行调度 | sys.argv索引选择N、8个seed、观测数组合；不是零参数单次运行脚本 | 446–471行 |

**可以直接独立实现的最小规格**：先用作者规模中最小的N=100、rank=2、Δt=.05、τ=.5、bias=0、同一J固定，仅改变gain、观测与拟合条件。实现时先固定随机种子、明确观测量q、完整记录m/n协方差。先做单teacher、少量student作为运行预算测量，然后决定seed数。若改N=32或64，应称“缩小规模的适配基准”，不能称精确复现原图。

上述方程表示无噪声动力学。若首轮独立实现设σ=0以便诊断，应明确这是对原训练设置σ=.001的简化。原协方差按(m₁,m₂,n₁,n₂)排序，初始对角全1，非零交叉项为Σ₁₃=1.5、Σ₁₄=3、Σ₂₃=−3、Σ₂₄=1.5及其对称项；迭代检查特征值，将Σ₃₃和Σ₄₄乘1.1。代码在首次非负特征值分支内仍再乘一次1.1后退出（498–505行），想精确重复分布须保留此细节。

J为rank-two，可以按两次向量内积计算递归项，避免构造N×N密集乘法；这是从方程得到的计算优化建议，**本次未实现、未跑、未验证与密集版数值等价**。该简化适合小型Mac工作；不能凭此保证1–2天完成全部实验。正式版[扩展数据Fig.2](https://www.nature.com/articles/s41593-025-02080-4)也明确讨论rank-two教师的参数恢复与轨迹预测区别，不能把预测准确直接解释成gain真值可辨识。

## 3. Fig.1 softplus teacher：可读，但不宜盲跑全脚本

来源 [nn_fig1_Teacher.py](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig1_Teacher.py)，**22,279 bytes**。

状态的列向量记法可写为：q = ReLU(g)⊙softplus(h+b)，h下一步=h+α[−h+J_eff q+W_in u]+σ ε。其中J_eff由符号投影及稀疏mask得到。具体来自[145–161行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig1_Teacher.py#L145-L161)。该式是对代码的重述，不能把σ ε自动当作已正确缩放的连续时间布朗噪声。

- N=300、Δt=.05、时间窗20、60 trials：[18–26行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig1_Teacher.py#L18-L26)。
- 虽然22行定义Tau=.2，**主class训练调用α=Δt=.05**（425行），不能擅自替换成Δt/Tau=.25。
- bias初始化Uniform[−.1,.1)，gain初始化为1+.4Normal且重采样至正值，无硬上界：[391–406行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig1_Teacher.py#L391-L406)。这些是**初始化范围**；505–506行允许训练bias、gain、connectivity，不能宣称训练结果bias永远在该区间。
- 稳定性初始化另用dt=.1、softplus和Euler（459–474行），与主训练时间离散不同。
- class在t=0输出r×readout，没有乘gain；后续输出乘gain（153与161行）。独立实现如统一此定义，需要记录是自己的修正，不是逐位复现。
- 脚本含筛选网络的while循环、整段训练、交互绘图、保存文件；存在seed之前生成的随机初始化。直接运行不等于小预算确定性复现。
- `fun_lib.py`中的RNN与RNNgain类readout定义也不同，不可只因名字相近混用。

## 4. 三个经验connectome案例：结构真实，目标活动由模型生成

正式版[Data availability与Fig.5](https://www.nature.com/articles/s41593-025-02080-4)将结构来源列为Zarin 2019（果蝇幼虫）、Scheffer 2020（成年果蝇central complex）、Vishwanathan 2024（幼体斑马鱼脑干）。论文teacher/student框架生成活动轨迹；不能称“用真实生物神经记录训练/验证”。

| 案例 / 小源码大小 | 当前可核实参数与路径 | 未核及轻量限制 |
|---|---|---|
| 幼虫premotor，`nn_fig5_larva_teacher.py` **1,675 bytes** | [7–18行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig5_larva_teacher.py#L7-L18)：执行`Data/Figure5/setup.py`；bm/bp零初始化，gm/gp初始Uniform[.5,1.5)；[48–51行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig5_larva_teacher.py#L48-L51)训练后clamp gain到[.5,5]；5000epochs | setup.py不在GitHub快照。N、M、dt、taum/taup、完整forwardpass和连接矩阵均依赖缺失Data；不猜具体神经元数。 |
| 成年果蝇CX，`nn_fig5_drosophilaCx_teacher.py` **30,933 bytes** | [433–483行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig5_drosophilaCx_teacher.py#L433-L483)：读取`exported-traced-adjacencies-v1.2/traced-neurons.csv`与`traced-total-connections.csv`，选EPG/PEN/Delta7/PEG；46个EPG排序写死。N由选后矩阵shape读取。 | 两CSV缺失，文件大小/总N未核。442行先构造全hemibrain Nall²密集矩阵，再子集选择，有明显内存风险，不能当小规模Mac脚本直接运行。 |
| 同一CX动力学 | [171–189行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig5_drosophilaCx_teacher.py#L171-L189)：softplus(h+b)，有效gain=exp(g)，J=exp(wrec)⊙mask；τᵢ=2.6+2.4tanh(τlatent)，范围(.2,5)。[568–605行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig5_drosophilaCx_teacher.py#L568-L605)：bias=.1Normal，latent g=.1Normal−.2，初始τ=1；默认target函数dt=.1 | **(.2,5)是time constant范围，不是gain范围**。gain为正但没有硬上界；bias正态无硬范围。dt来自生成target的ts，默认值不可套用到别的案例。 |
| 斑马鱼，`nn_fig5_zebrafish_teacher.py` **14,575 bytes** | [65–85行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig5_zebrafish_teacher.py#L65-L85)：`goldman_data/ConnMatrix_CO_top500_2blocks_gamma038_08062020.mat`及totalInputs、cellIDType、MatOrder等。N由mat shape。 | 名称top500不足以核实最终N=500；不能据文件名报真实网络规模。另有blockassignment `.data`文件，均在缺失Data目录。 |
| 斑马鱼teacher动态 | [153–179行](https://github.com/emebeiran/connconstr/blob/f5f397b88f8dd5c2a5c13558ce6039194a284586/nn_fig5_zebrafish_teacher.py#L153-L179)：线性Euler r下一步=r+dt(Wr−r+I v)/τ；dt=.001，21000步；调用传τ=1、谱归一化参数ynew=.9 | 函数默认τ=.1、ynew=.99不是实际调用值。student文件另用dt=.1；不能把teacher预生成dt概括成整个管线步长。未读取任何MAT数据。 |

## 5. 依赖、许可与交付边界

静态导入含NumPy、PyTorch、SciPy、pandas、h5py、Matplotlib、seaborn、sklearn、networkx；未找到环境锁文件或requirements。部分脚本还引用仓库未包含的`functions_trainserverAshokOct24`，需逐脚本判断，不能据“ZIP很小”声称完整可运行。Fig.3独立方程实现可避开大部分绘图和经验数据依赖。

本固定快照28个文件中**没有LICENSE/LICENCE/COPYING文件**，README也未声明软件许可；Zenodo页面的具体license文本本次未成功核实。GitHub公开可见不等于获得任意复制、修改、分发软件的许可；[GitHub官方说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)也说明没有许可证时默认版权保留。当前可继续的路线是：以明确引用的数学模型为依据、独立书写自己的最小程序，不将上游源码复制成拟发布实现；若要直接复用或发布原脚本，需要先明确对应许可。

本审计支持“先做N=100合成teacher/student实验、报告模拟中的可观测性与参数不确定性”。它不支持声称“真实连接组的真实功能已恢复”“机器人实验已验证”“原文全套结果已复现”，也未证明某一新研究问题具有投稿价值。
