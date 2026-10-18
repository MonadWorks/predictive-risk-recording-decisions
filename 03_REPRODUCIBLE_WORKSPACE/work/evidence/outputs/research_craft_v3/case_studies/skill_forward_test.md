# research-writing-figures：独立前向试用

## 试用边界

本次仅阅读指定Skill、`references/argument-and-prose.md`、`references/working-templates.md`，以及两个指定研究输入：

- `outputs/research_v2/holdout_analysis/summary.json`
- `outputs/research_v2/forecast_followup_analysis/summary.json`

没有读取v3稿件、其他agent答案、原始CSV或协议；没有联网、重跑实验或改统计。以下是职责图和一个英文结果段，不是完成了文献查证的Introduction。文献定位来自Skill的references，不能据此声称本次精读原文或确认全球文献缺口。

## 1. 从研究输入确定的表达合同

**核心问题：**有限记录设计中，先验参数集合平均的预测风险，是否改善所选记录位置产生的刺激响应误差？如果不稳定改善，它对固定预测的误差风险预报是否仍有价值？这是两个分别评价的问题。

**贡献定位：**现有模型与风险准则的有控制计算比较，以及把“选择改变带来的预测效益”和“同一预测的风险预报质量”分开检验。输入不支持将本文命名为新理论、新神经网络、新评分规则或已证实的通用改进。

**实际独立单位：**连接矩阵J。第一研究40个J，129,600评价行；第二研究也是40个独立J，6,480评价行。嵌套truth/noise/target等重复先在J内平均。不能用行数当独立n；也不能仅凭两个summary把两批40合并成一个n=80的共同效应检验。

**目前最窄的主结果：**第一研究两个预定主比较区间均跨0；第二研究预定主评分差也跨0。可直接报告估计、区间和方向，不能称为“无效”“等效”，也不能凭探索层的结果宣布集合准则普遍更好。

**未读取合同造成的具体缺口：**这些summary足以写结果概述，但没有完整动力学方程、q的精确定义、scalar/vector权重和先验分布等方法细节。正式Introduction和Methods仍要核对研究合同。这里不从方法缩写补猜这些参数。

## 2. 五段Introduction职责图

段落数由本次问题链决定：应用决策、已有模型答案、风险近似、两个不同评价对象、本文检验。它不是Skill强制的五段模板。

| 段落 | 承接的问题 | 该段要让读者知道什么 | 引用或输入的职责 | 送往下一段的问题 |
|---|---|---|---|---|
| I1：具体决策 | 当只能记录有限神经元时，记录位置为何重要？ | 把科学问题落在“为预定刺激响应选记录”这个决策，而非泛谈AI与脑科学 | Beiran & Litwin-Kumar 2025作为最近的问题设置与已有记录选择来源；不是用来宣称本研究新颖 | 结构信息和有限记录已经能解决什么？ |
| I2：既有答案 | 知道连接、再加部分活动后，哪些预测可被约束？ | 明确承接连接约束与未知生理参数下的活动预测，并承认选记录点已有先例 | Beiran支持最近既有答案；Lappalainen 2024作为结构/任务约束与功能预测的另一建模谱系，不代替本题的直接基线 | 可用的模型怎样转换成面向特定目标的设计准则？ |
| I3：风险近似 | 为什么名义点和先验集合可能给出不同设计？ | 引出目标相关预测风险与局部近似，以及逐参数状态处理不确定性的动机 | Attia et al. 2018与Zhong et al. 2026承担方法谱系；精确采用哪一个公式须回到原文核查；不把软件实现叫新理论 | 风险值改变，究竟意味着预报更准还是选点更好？ |
| I4：分离两个可检验命题 | 较大或更接近均值误差的风险是否必然改善决定？ | 将risk forecast与recording decision分离：前者保持点预测固定，后者允许记录集合改变 | 属于本研究问题定义；Gneiting & Raftery 2007只承担评分历史，具体MSE-functional一致性用本研究直接计算，不冒充整分布校准 | 什么设计能分别评价这两个命题而不互相替代？ |
| I5：本文研究与贡献 | 我们怎样作出可信的条件性判断？ | 介绍scalar/vector与local/ensemble的比较，以及另批数据上固定记录策略的风险预报检验；预告研究回答哪些条件性问题 | 两份summary支持两项检验及其独立J数量；方法参数仍待合同核对 | 进入Methods的共同信息集、目标和评价流程 |

正式稿I5可简短预告：主检验未支持稳定优势，后续结果呈条件依赖。不要把“不显著”包装成理论否定，也不必在Introduction逐项列所有置信区间。

这里没有引入跨领域演示论文来填科学证据。写作演讲、通用作图参考只可用于编辑工作，不进入上述科学论证链。Sourmpis等目的匹配验证文献若使用，应承担“为何刺激响应应独立检验”的职责，不承担本研究已获生物验证的职责。

## 3. 四节Results职责图

| 小节及建议标题 | 需要回答的具体问题 | 本次输入中的证据 | 可用表达 | 尚需补齐的展示或材料 |
|---|---|---|---|---|
| R1. Prior averaging did not establish a consistent improvement in recording design | 在事前指定主层中，集合平均改变记录位置后实际q误差是否改善？ | broad、exclude_endpoints、budget3、40J；ES−LS ΔMSE=-2.5864×10⁻⁶，97.5% CI[-1.4713×10⁻⁵,4.8263×10⁻⁶]；EV−LV为1.9236×10⁻⁶，CI[-1.1480×10⁻⁶,6.8260×10⁻⁶] | 两个主比较未建立一致改善；估计方向不同，区间容纳收益和损失 | 对应每J配对图必须从已定义source data绘制，不能从summary反造40个点 |
| R2. Risk magnitude and error ranking provide different diagnostics | 风险排序好是否等于绝对风险准确？ | 同主层LS的nominal跨J Spearman约.953；nominal均值4.2777×10⁻⁵、实际MSE6.9085×10⁻⁵；ensemble风险均值6.2658×10⁻⁵ | 排序与均值量级是不同诊断；这些是原研究的描述性结果 | 不把高相关称校准；不从两个均值宣称预报评分显著改善；图需实际每J值与identity reference |
| R3. A separate fixed-prediction study tested forecast quality | 保持同一个点预测，集合风险预报是否更好？ | 后续研究local_scalar主层、40J；共享点预测；MSE完全相同；Δscore=-.45565，95% CI[-1.15857,.02367] | 集合评分均值更低，但主区间仍含0；预报对比并未重新检验不同记录设计的效益 | 显式给出score方向、公式与固定floor；保留原研究主比较，不把后续当“验证了优势” |
| R4. Forecast behaviour depends on the evaluation condition | 相同风险近似在不同条件下是否呈现不同表现？ | bias_shift+LS探索层Δscore=-1.35829，95% CI[-2.21429,-.63450]；matched+LS为.00668，CI[-.03374,.04601]；主层风险均值比1.617与casewise平均比3.716为不同汇总 | 这些探索结果提出条件依赖假说；均值风险比不能代替评分差，更不能解释为实际MSE改善 | 全部分层表并列，标探索性；没有交互检验输入时不宣称“条件效应差异显著” |

选用四节是为避免将R2描述性图和R3独立研究挤成一个“校准得到改善”的故事。若篇幅紧，可以合并R3/R4，但必须保留主检验与探索结果的地位差别。

数值验收、N100规模结果、消融或额外机制不是本次允许的输入，因此没有编成第五个结果小节。正式稿可在取得对应证据后重新安排，而不是为了套图数扩写。

## 4. 英文结果段（只使用第二研究事前指定主层）

To distinguish the quality of a risk forecast from the benefit of changing recording sites, we compared nominal and ensemble risk forecasts while holding the point predictions fixed. Across 40 independent connection matrices, the ensemble-minus-nominal difference in the prespecified score was −0.456 (95% paired network-cluster bootstrap CI, −1.159 to 0.024). Lower scores indicate better forecasts under the MSE-consistent score, S(v,e)=log(v)+e²/v, with the prespecified variance floor applied. Because both forecasts evaluated the same point predictions, their response MSE was identical (1.18×10⁻⁴). The interval therefore leaves the forecast advantage unresolved in this setting; it neither establishes equivalence nor provides evidence that changing recording sites improves response estimation.

**数字出处：**`forecast_followup_analysis/summary.json`的`primary`、`score`、`score_interpretation`、`analysis.primary_interval`和`point_predictions_shared`。实际floor=10⁻²⁴，无风险触及floor。公式在段内省略max只是因为明确说明应用预定floor；Methods必须写完整max形式。若需更短正文，可把公式和最后一句后半移入Methods/Discussion，不改变结论。

## 5. 对Skill的前向试用评价

### 直接有用的四点

1. **分离研究贡献和表达优化。**“保持方法、estimand和分析不变”使我直接采用现有97.5%与95%区间，没有为了文字统一改成同一种区间，也没有因为跨0改写成等效结论。新颖性位置由最近先行工作决定，不能从更好看的图产生。
2. **区分科学引用与展示参考。**引用有职能，使Beiran用于已有答案、OED文献用于方法来源、评分文献用于历史；写作演讲没有被塞入科学参考。Skill给出的案例表很有帮助，但其文献断言仍需原文查证，不能把Skill本身当科学来源。
3. **保护独立单位。**模板主动要求独立单位，因而保留每项研究n=40 J，并把129,600/6,480行及嵌套重复放在记录层，未用行数制造精度。
4. **避免把后续研究拼成“成功闭环”。**“follow-up是新问题”使风险评分与记录设计改善被拆开；共享预测意味着相同MSE，这一事实直接控制了英文段落的主张。

### 没有被强制的东西

- Skill明确段落数量依论证决定；本次5段Introduction与4节Results来自任务，而非固定格式。
- 没有要求添加统计检验、删异常值、改变分母或补做实验。
- 明确建议把限制写在改变推断的位置，而非逐段重复免责声明。英文段落只保留一个实质性的推断边界，避免每句“我们不声称”。

### 实际摩擦与可改进处

| 摩擦 | 本次表现 | 对Skill的建议；不改现有文件 |
|---|---|---|
| 专属研究案例太具体 | `argument-and-prose.md`直接给本研究三条谱系，新使用者可能误把它当通用必引文献表 | 在该表前加一句“仅为原项目演示；新项目须替换并逐项核查”，或搬到明确标注的case study；保留方法而非复制名单 |
| 风险、方差与概率校准易混用 | 输入已说明MSE-consistent score并不要求Gaussian；仅靠常用“calibration”标签仍可能写过头 | 在通用claim ledger添加“target functional / probability distribution”一列或检查句，不要求每个领域都讨论方差 |
| 只有summary时需要缺失输入处理 | Skill要求研究合同，但本次输入只有summary；若强行完成可诱发补猜模型参数 | 建议增加一句：缺少方法合同则用显式占位或限定为结果写作，不以审计阻塞所有可完成部分 |
| 负向表述可能聚集 | 若机械复制“not new / not validation / no claim”会使Introduction像自我辩护 | references已有正面改写实例，可再强调每个核心限制只在适当位置交代一次；本次已通过“已有答案→本题问题”消化 |
| 单句贡献易把不确定结果包装得太强 | “disentangle”可能被读成已完成因果识别 | 实际正文用“evaluate separately / distinguish in the design”，除非有相应辨识证据，不把结构清楚等同机制已证实 |

### 判定

**可用于下一轮稿件工作，且本次未导致统计越权。**最有效的是让两个研究的问题、独立单位和可允许结论先对齐，再写英文。当前Skill无需添加固定章节数或更长检查清单；优先改进是把项目特定例子标得更清楚，并说明输入不足时如何继续完成可信部分。

前向试用只证明它能约束这一次具体写作任务；没有测试最终作图、渲染、源数据导出或不同领域可迁移性，不能据此宣称该Skill已全面验证。
