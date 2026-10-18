# 科研图形方法调研、v2诊断与可复用绘图合同

2026-10-16。只做来源核查、现有图形诊断和重画建议；未改结果、统计、协议或绘图代码。建议的尺寸、字号和布局是本项目工作规格，尚未被指定期刊的正式要求替代。期刊分区会随年份、数据库和学科分类变化，本报告不以“Q1”作为固定事实或图形质量认证。

## 1. 核心判断

当前图有三项值得保留的基础：点代表独立J、离群网络没有被删除、区间类型有说明。主要问题是**没有让图形结构充分表达研究结构**：2×2因素被拆成多个方法标签，配对关系主要留在减法里；实验分布和估计量不确定性占用相近视觉层级；大画布缩到论文宽度后字号不足。应该保留原始证据，重新组织“设计—配对观测—总体效应—影响/尾部”四层，而不是换一个style即结束。

现有两个研究必须保持分开：第一研究检验记录设计，两个主比较是ES−LS、EV−LV，使用97.5%区间；独立follow-up检验同一记录集和点预测上的risk forecast score，只有一个主比较，使用95%区间。后者不是前者“换指标后显著”的版本。所有下面的图形建议只调用已计算的J层指标与区间，不新增检验、重分组、选择最优场景或截断离群点。

## 2. 七组具体来源：页面、图例、代码与边界

以下按资源组计7组；LICENSE、具体脚本和同一资源的章节为核验附件，未把搜索结果聚合站当依据。

### R1. Nature Methods 官方blog：从图形任务组织内容

[Methagora：A view of every Points of View column](https://blogs.nature.com/methagora/2013/07/data-visualization-points-of-view.html)，2013-07-30。具体可看“Composition and layout”区域及其中引用的 **Layout Fig.2**，它把布局、负空间、文字、轴与标注分别组织，适合作为重画前的检查导航。原始Layout DOI为[10.1038/nmeth.1711](https://doi.org/10.1038/nmeth.1711)；本轮正文触发Nature身份跳转，未声称重读全文。实际建议依据可读官方blog的分类与说明，而非假装看过付费原图细节。

对本项目：主图先回答“比较什么、证据如何配对、估计多不确定”；说明性的长段落移进caption，图内保留短标题和关键标记。这里学习布局原则；不复制Nature示意图，未核得其开放图像再利用许可。

### R2. Wong：Color blindness，含2023归属更正

[Nature Methods 2011原文](https://doi.org/10.1038/nmeth.1618)的Fig.2展示色觉差异友好配色；[2023更正](https://www.nature.com/articles/s41592-023-01974-0)补充了Ito/Okabe相关来源。对本项目的直接含义是：颜色需和形状、填充或分面冗余编码，而不是使用六种颜色后宣称可访问。浅色点叠加透明度，在缩印后可能不足；常见palette的名字也不保证实际图可辨。我们自行绘制数据，不复制原文图片；不将调色板或灰度筛查等同于完整色觉测试。

### R3. Wilke：配对数据的真实案例

[Fundamentals，第12.4节](https://clauswilke.com/dataviz/visualizing-associations.html)：Fig.12.11用166个国家的两个时间点CO₂排放作配对scatter，明确画x=y；Fig.12.12/12.13用较少个体的slopegraph保留身份。其启发是：先显露配对，再显示差，而不是并列两根柱子。本项目40J适合paired scatter＋差值分布，全部40条四方法连线则可能拥挤。**不借用示例中挑选10国的规则挑选我们的网络。**

书稿[LICENSE](https://github.com/clauswilke/dataviz/blob/master/LICENSE)为CC BY-NC-ND 3.0 US，不能把“可在线读”理解成可任意改作图例分发。我们采用概念并自行实现，不搬运书图或整段R代码。

### R4. Wilke：分布与估计不确定性分开

[第16章：Visualizing uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html)，具体对照Fig.16.15–16.17：拟合不确定性不是原始点的离散度。对本项目：灰/彩点呈现J层分布，黑色区间表示总体均值或配对效应的cluster CI，图注分别命名。我们不照搬其posterior线束，也不临时给本研究加不同置信水平、动画或新的统计估计。章节适合做“到底画SD、CI还是分布”的选择参考，不是某个bootstrap方法必然正确的依据。许可证同R3。

### R5. Rougier：可执行的联合布局例子

[Scientific Visualization书与源码](https://github.com/rougier/scientific-visualization-book)。实际检查了[code/layout/standard-layout-2.py](https://github.com/rougier/scientific-visualization-book/blob/master/code/layout/standard-layout-2.py)：NumPy＋Matplotlib，GridSpec按5:1分配中心scatter和边缘hist，使用constrained layout。它具体示范了“主关系大、辅助分布小、共享位置尺度”。本项目可借其布局骨架，但无需机械给每个scatter加hist；N=40时ECDF通常更直接地保留全部值，且不引入bin选择。

[LICENSE.txt](https://github.com/rougier/scientific-visualization-book/blob/master/LICENSE.txt)区分：书为CC BY-NC-SA 4.0；代码为保留版权/免责声明的BSD两条款形式。样例字体Roboto Condensed不是统计依赖，可用已安装字体替换。该资源是书和Python示例，不把它当已验证的Agent Skill；未安装或执行上游代码。

### R6. SciencePlots：可借样式，但必须检查覆盖项

[仓库](https://github.com/garrettj403/SciencePlots)、[实际gallery](https://github.com/garrettj403/SciencePlots/wiki/Gallery)。已核[pyproject](https://github.com/garrettj403/SciencePlots/blob/master/pyproject.toml)：Python≥3.8，运行依赖Matplotlib，MIT。gallery有`science + no-latex`与scatter实例。实际[science.mplstyle](https://github.com/garrettj403/SciencePlots/blob/master/src/scienceplots/styles/science.mplstyle)默认启用LaTeX，并设置tight bbox；所以在本Mac上不应为了一个style默认装整套TeX，也不能以预设figsize保证最终PDF尺寸。它是样式包，核验到的是pyproject与mplstyle，不是声称已找到SKILL.md。

建议仅作视觉参照。现有Matplotlib足以实现本项目；若以后采用，应锁版本、临时style context、显式关闭不需要的LaTeX，并覆盖最终物理尺寸。`nature`/`ieee`样式名是外观预设，不是投稿合规认证。

### R7. 真正有SKILL.md的候选：K-Dense scientific-visualization

[实际SKILL.md](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/SKILL.md)已读，307行，frontmatter记录v1.4、last-reviewed 2026-10-01；[根LICENSE.md](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/LICENSE.md)为MIT。仓库已从旧Claude Scientific Skills命名迁移；应引用实际当前路径，不从聚合站复制安装命令。本轮只审计，不启用、安装或执行。

- 它声明的工具包括Read/Write/Edit/Bash/Glob/Grep；这不是主机已授予权限的证明，也不能称“只有只读指导”。
- Python≥3.11和uv用于其固定示例；依赖随任务分开：palette工具主要标准库，metadata按需加载Pillow/pypdf，绘制导出要Matplotlib。Plotly/Kaleido静态导出另涉及Chrome；本项目不需要整套升级。
- 抽查了[palette_audit.py](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/scripts/palette_audit.py)、[image_metadata.py](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/scripts/image_metadata.py)、[figure_export.py](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-visualization/scripts/figure_export.py)。它们涉及本地模块导入、读文件和可选写输出，不是单个无依赖提示词；有价值的是尺寸/字体/对比/源数据检查，但抽查不等于全仓安全审计。
- `allowed-tools`、示例包版本和上游自我宣传都不替代本地复现。本轮GitHub API commit查询不可访问，未伪造SHA pin；只记录访问日和技能自述版本。后续若vendoring，先固定具体commit并逐文件审查。当前更适合由root做**项目内playbook与独立绘图脚本**，不用安装整个库。

## 3. v2具体诊断：先看最终尺寸，再评美观

已目视检查holdout primary/raw以及follow-up primary、全部strata、risk-vs-actual、ratio/ECDF图。下列尺寸由PNG实际像素与DPI metadata读取；不是凭截图估计。原脚本常规字号约9pt，缩放列仅说明按180mm排版的后果。

| 文件 | 实际像素@约300dpi | 当前宽度 | 放到180mm后原9pt约为 | 诊断 |
|---|---:|---:|---:|---|
| holdout primary_paired_effects | 2673×1456 | 226.31mm | 7.16pt | 文字占比过高，顶部有较大空白；配对差保留了信息，但两panel范围不同且多数点贴0 |
| holdout raw_risk | 4768×2925 | 403.69mm | 4.01pt | 12个panel挤进论文宽度会不可读；方法色彩掩盖2×2结构；不同panel不能比视觉高度 |
| follow-up primary score | 1919×1420 | 162.48mm | 9.97pt | 尺寸并非主要问题；单极端网络撑大轴范围，使其余点挤在零附近。必须保留极端点，并加完整分布视角 |
| follow-up risk_vs_actual | 2975×1336 | 251.88mm | 6.43pt | 共享轴和y=x正确；多数点近原点且空间闲置，宜补充展示，不以“更靠线”代替主score |
| follow-up ratios_and_distribution | 2976×1336 | 251.97mm | 6.43pt | 两panel回答不同问题；ratio-of-means不是个体ratio的平均，现有说明应保留，不能用大ratio暗示效果更好 |

提高PNG DPI不会修复4pt字。下一版应从180mm物理宽度直接设计，PDF保持该宽度；不要先做400mm图再缩印。长防误读说明移caption，图内只留指标、方向、n和必要编码。

## 4. 可执行的整图安排

### 主结果图：既呈现2×2，也呈现配对与不确定性

最初可把合同矩阵与结果放一张整图，但root现已选择更清楚的分工：**方法矩阵留在Fig.1；Fig.2只呈现两个并列paired scatter和底部两行relative-MSE forest**。整体宽180mm，高度约125–140mm，按实际渲染验收。上方两scatter分别为scalar/vector，x=local network MSE，y=ensemble network MSE，同x/y范围、等比例、y=x，40J全部保留。两轴均严格正时采用完整范围log–log并标明坐标；若有零值则回到线性或另作明确的零值展示，不加伪计数。底部forest直接读取已算的aggregate mean-MSE ratio变化及97.5%CI，0%线，标ES−LS与EV−LV。配对差ECDF移紧随其后的补充图，保留尾部与ties，不新增统计检验。

不要把B中一个点再称为“ensemble样本”：它同时编码local和ensemble这对结果。若数值跨尺度导致挤在原点，先保留线性完整图与ECDF；只有全部数值严格正、明确标注坐标变换时，才可另给完整log–log配对scatter。零值不能加任意伪计数，signed difference不能直接上普通log。这里不建议截断轴或删除极端网络。

图内可写`40 independent networks`与`paired cluster CI`；3 truths×3 noise×3 readouts是每J嵌套结构，完整说明放caption。97.5%是本研究两个主比较的预定家族，不因换图变95%。**预定主估计量仍是原始MSE均值差**；relative-MSE forest是既有辅助效应量的可读展示，caption或紧邻主结果表必须同时保留raw差及其97.5%CI，不能静默把ratio改称原定primary。CI跨零表达不确定性，不能写成等效。

### Follow-up主图：把“预测不变、只评risk”放在视觉结构里

A为小信息框，展示同一选点/同一qhat，分叉到nominal risk与ensemble risk，再共同进入S(v,e)。B显示所有40J的score差分布，保留J6015的尾部；可用水平strip配合完整ECDF，而非仅加高一个竖直轴。C显示唯一primary总体score差与95%CI，直接取已有表。现有ratio-of-means与mean-case-ratio适合表格/补充，分别命名，不拼成“效果”面板。risk-vs-actual两panel也移补充，保持相同轴范围并标descriptive。

不能让bias_shift探索性panel取代原定broad主场景；全部六strata保留在补充，primary和exploratory有显式标签。第一研究40J与follow-up新40J不是可合并的80个同一问题样本。

### 补充图清单

- 原12panel raw-risk拆成三个条件图，每张2×2布局：行预算M，列接口可行域；方法顺序固定。保留原完整概览与源表，拆图不丢场景。
- 标准化风险、各目标结果、LONO、全部网络ECDF、MAP局部区间覆盖、优化失败、成本与N100探索模型放补充/表格。若正文讲相应机制，则引用，不做无叙事作用的主图装饰。
- 不同单位的指标不共用一个色阶。若做对比矩阵/heatmap，仅用已定义相同单位的effect，null居中、缺失独立标识，并附数值/CI表；不能把有无显著性的棋盘当效应图。

## 5. 两因素编码、尺寸和导出规格

两种方案均可执行，但必须全篇选定一个，不能混用：

- **本项目已选方案（root确认）**：objective颜色固定scalar蓝`#0072B2`、vector橙`#D55E00`；nominal/local空心、ensemble实心。follow-up只研究single-response，所以两forecast同蓝，以空/实心区分，在同一J的y水平用线连接。paired decision scatter中的一个点同时承载两种近似方法，颜色只表示objective；横轴local、纵轴ensemble，不再给其点颜色赋approximation含义。两行forest也仍用objective颜色，CI可黑色或对应深色，null为0；无需再造ensemble颜色。Activity可用灰三角、Random灰叉。形状/facet/文本冗余表达objective，图注写清同一语义。
- 备选方案（本项目不使用）：local/nominal灰`#6E6E6E`、ensemble蓝`#0072B2`，objective用圆/方与facet表达。这适合以近似方法为全篇主编码的其他项目，但不能和本项目已选的objective颜色混在同篇图中。

forest的相对效应需完整命名：`100 × [mean_J(MSE_E) / mean_J(MSE_N) − 1] (%)`。即使简写E−N，也不能把它误称平均个体百分比变化；所有CI直接读取原分析。follow-up同J连线只呈现配对关系，不把线数当独立样本增加n；网络排列使用ID或明示的全量排序规则。

本项目暂定：白底，正文图中文字8.5–9pt，panel字母10–11pt，轴/CI线约0.6/1.0pt，原始J点约3–4pt直径，点透明度不低于可辨要求并带必要边框。近零参考线`#8A8A8A`，可省网格；文字`#222222`。这些是起点，不是某刊统一规定。标签缩到最终版面后再检查，不能只看放大的PNG。

用GridSpec/subfigure明确布局和物理尺寸；采用constrained layout就不再叠tight_layout。若要求180mm精确宽，优先`bbox_inches=None`并正确分配边距，导出后读PDF MediaBox/PNG有效宽度验证；`bbox_inches='tight'`会改变页面尺寸，不能假装figsize即成品尺寸。输出矢量PDF（嵌TrueType）和300dpi预览；SVG需说明字体是文本还是路径。这里无需Plotly/Kaleido、额外Chrome或TeX。

## 6. 可跨领域复用、但带适用条件的principles/tricks

| 原则/技巧 | 什么时候适用 | 实际动作 | 容易犯的错误 |
|---|---|---|---|
| 先写estimand，再选图 | 要比较方法、条件、处理 | 图形合同写清总体、单位、权重、效应、区间、方向 | 先选好看模板，再给它找指标 |
| 配对用共同坐标和差值 | 同一患者/动物/数据集/J接受两种条件 | paired scatter＋identity line；用预定义差值展示总体效应 | 按两组独立样本画CI，丢掉pair ID |
| 样本分布与估计CI双层呈现 | 既关心平均效果又关心失败/尾部 | 原始独立单位点/ECDF＋单独mean/CI | SD、SE、CI、预测区间混称error bar |
| cluster先于画图软件 | 存在患者内重复、动物内细胞、网络内noise等 | 用研究设计指定的独立层级计算区间，再传给绘图代码 | Seaborn按行自动bootstrap，虚增n；多中心/交叉结构不一定能用一个简单cluster替代建模 |
| 2×2用语义矩阵/正交编码 | 两因素确实可分开操作 | 一个因素用行列/shape，另一个颜色/填充；固定legend | 四种组合变四个无关系色块，或看起来有交互就宣称交互 |
| 分布偏斜时加ECDF | n有限、有ties/长尾，不想选择带宽 | 全部独立单位按原值排序，保留0线和尾部 | 光滑violin掩盖ties，或裁尾让结果“更紧” |
| 同单位才共轴/共色阶 | 可直接比较的场景/指标 | paired axes共享尺度；不得共享时显式写范围不同 | raw与标准化混轴；每格独立色阶却比较深浅 |
| 比例的估计量要写公式 | 风险比、fold-change、平均相对效果 | 区分mean(A)/mean(B)、mean(A/B)，CI按所用函数重算 | 在个体ratio散点旁放总体ratio却称平均个体效果 |
| 主/探索层级进入图布局 | 有冻结主场景或独立follow-up | 主图放预定问题，完整其他场景留补充并标明 | 事后只选赢的一格当标题；多图重新定义primary |
| 显示变换不改变统计目标 | 动态范围太宽 | 保持原始估计量；明示log/symlog及零值规则 | 加伪计数、变换后均值冒充原始均值、隐匿断轴 |
| 源数据和figure作为可重建产物 | 论文/汇报/共享 | 每panel有source table、筛选键、生成命令、尺寸/字体检查 | 只保存PNG；在绘图脚本中重新挑seed、改CI或改权重 |

这些原则可迁移到生物信息学、模型benchmark和临床回顾数据，但独立单位、可交换性、权重与因果解释必须重定，不能直接把本研究的“J-cluster”替换成任意ID就宣称有效。

## 7. 重画验收合同

1. 原始results、protocol、所有数值CSV与primary对象不变；新图只消费已有表，输出新目录。J层聚合/CI不得在plotting库中默默重算。
2. 全部点与图表来源能追踪到row/network ID；对照主图与supplement，任何缺失都写原因，离群点不删除。标签如J5029/J6015只为已有影响诊断，不把它们当排除理由。
3. 第一研究主forest确为97.5%而follow-up主forest确为95%；0%效应、ratio=1、score difference=0等null线正确。原始MSE、ratio、score不混单位。
4. 图形只讲估计与适用边界：CI跨零不证明等效，风险变大不代表校准变好，score不是完整概率校准，模拟不是生物干预验证。
5. 检查最终180mm页面中的字体、点边界、重叠、字体嵌入、灰度及实际色觉模拟；palette工具筛查只是部分检查。完成PDF与PNG逐panel读回。
6. 安装决定与学术方法分开：本轮没有安装任何未知GitHub skill、运行上游脚本或升级环境。root可把经过选择的规则转成项目内playbook，并在代码中写清来源；不要把README、星数或“publication ready”字样当审计结论。

## 发布前最终选择与许可差异补记（root）

Fig.2最终采用原始MSE均值差的forest（显示单位10⁻⁵ q²），直接读取原effect及97.5%CI；百分比保留结果表。上文relative-forest是布局讨论过程，不是最终主图统计口径。

许可核查存在版本/入口差异：本轮作者在线书首页明确显示CC BY-NC-ND 4.0 International，而本笔记核对的GitHub LICENSE为3.0 US。两者不混称同一许可；本项目没有搬运图像或代码，所以不依赖对这种差异的自行解释。若未来要复用原图/代码，须对具体文件和版本重新核许可。
