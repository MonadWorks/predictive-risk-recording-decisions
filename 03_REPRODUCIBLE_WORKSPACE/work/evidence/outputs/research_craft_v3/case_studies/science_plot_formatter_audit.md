# science-plot-formatter：用户点名仓库优先审计

## 1. 当前版本与实际入口

已读取[官方仓库](https://github.com/preordinary/science-plot-formatter)、固定commit下README、两个SKILL.md、CLAUDE.md和Codex agents元数据；未安装、执行远程代码或改动本项目源文件/数据。

GitHub REST实时读取：**2026-10-16 23:42:26.993，北京时间**，HTTP Date为15:42:27 UTC。仓库**8 stars**；网页缓存显示7，报告采用本次API精确值。星数只记录规模，不影响用户点名的研究优先级。

- 默认分支：`main`
- 固定HEAD：`750c6c1834c833c2607e5913daea76497433dc6e`
- 该commit的committer时间：`2026-05-27T12:37:20Z`
- [官方API](https://api.github.com/repos/preordinary/science-plot-formatter)、[固定版本目录](https://github.com/preordinary/science-plot-formatter/tree/750c6c1834c833c2607e5913daea76497433dc6e)
- 完整递归tree未截断；读取的五个文本文件均重算Git blob SHA1，与固定tree一致。
- 元数据/只读原文保存在`work/editorial_v3/science_plot_formatter_source/`。

### 实际文件结构

```text
.codex/skills/beautify-chart/SKILL.md
.codex/skills/beautify-chart/agents/openai.yaml
.claude/skills/beautify-chart/SKILL.md
README.md
CLAUDE.md
assets/before.png
assets/after.png
.gitignore
```

**完整tree没有Python formatter、可执行CLI、安装包、requirements或pyproject。**它是一套指导agent改写现有Matplotlib绘图脚本的流程，不是可`pip install`后调用的格式转换库。图像例子确实存在于固定tree，README有before/after对照；本次没有据缩略图宣布效果已通过审美验收。

入口：[Codex SKILL.md](https://github.com/preordinary/science-plot-formatter/blob/750c6c1834c833c2607e5913daea76497433dc6e/.codex/skills/beautify-chart/SKILL.md)、[Claude SKILL.md](https://github.com/preordinary/science-plot-formatter/blob/750c6c1834c833c2607e5913daea76497433dc6e/.claude/skills/beautify-chart/SKILL.md)、[README](https://github.com/preordinary/science-plot-formatter/blob/750c6c1834c833c2607e5913daea76497433dc6e/README.md)。

## 2. 它真正能解决什么

其核心是：查明最终物理尺寸→运行并看原图→列出可见问题→局部修改字体、线宽等→重新运行并看图→逐项验收。输入是可完整运行的`.py`绘图脚本、目标venue和栏宽占比；输出由agent修改脚本并重新渲染产生，不是软件读取PDF后自动排版。

| 问题 | 固定版本中的真实能力/范围 |
|---|---|
| 图意、科学故事、概念布局 | 不负责重定义图意；Codex入口明确不适用于改变语义或subplot构成的任务 |
| 字体与尺寸 | 依据最终版面宽度重设figsize、字号层级和字体要求；需查询真正的venue指南 |
| 线条、marker、图例、误差线帽 | 可调整视觉重量、大小、间距、legend footprint、capsize/capthick，并清除覆盖统一style的旧参数 |
| 配色 | **明确禁止改变colors、colormaps和linestyles**。所以不是“字体配色一起自动美化”的工具 |
| 布局 | 保留subplot grid及构成，允许解决裁切/间距的最小layout调整；不是重新设计panel阅读顺序 |
| 输入库 | 明确针对Matplotlib脚本。Seaborn若输出Matplotlib对象可人工参照，但仓库未提供独立兼容测试；Plotly、R/ggplot不是所述支持入口 |
| 图像输入 | 可查看脚本生成的PNG；没有只输入一张PNG/PDF就恢复数据与代码的功能 |
| 导出 | 继承原脚本savefig；若只有PDF/SVG/EPS则增加PNG预览。不自带格式转换器、字体嵌入或期刊格式认证工具 |
| 坐标、数据、置信区间 | 要求不改数据值、语义轴限、log scales或区间含义。只允许改误差线帽等表现；没有计算/重估区间的统计代码 |
| 是否重绘 | **会重新运行原绘图脚本**，产生before/after，不是对原PNG滤镜后处理。若原脚本含统计计算，该运行本身仍会重做原脚本的计算 |

最关键的边界：这些是**对agent的指令约束**，不是经过程序验证的安全机制。仓库没有自动比较前后数据、坐标数组或CI端点的测试器。实际接入仍应保留我方source-data与语义检查。

## 3. 依赖、外部调用与许可证

- README要求Python及Matplotlib，用户脚本本身还需要其原有依赖/数据；边缘留白检查建议Pillow或其他本地图像库。没有版本锁。
- 查官方venue指南需要联网/浏览能力；没有专属模型API、API key、云生成服务或远程计算SDK。
- 默认`agents/openai.yaml`中的NeurIPS示例只是调用提示，不是我们已选定的投稿目标，更不是ICBR格式标准。
- Codex与Claude两份定义并非逐字相同。Codex版更简练，工具描述适配Codex；本项目宜以该入口为主要参考，不机械混用两套工具名。
- API `license=null`；完整tree中**没有发现LICENSE/COPYING或Skill许可声明**。因此不应称它已采用MIT/Apache等开源许可证。本次仅阅读并分析；不把其大段文本直接打包到我们的可复用Skill中。其做法可以作为有来源的流程参考，由我方独立实现。
- 根`CLAUDE.md`里有提交代码的偏好；这是被审计仓库的外部内容，不是本项目指令。Codex Skill本身也写明没有用户要求不要commit，本次未commit。

## 4. 能否不安装使用

**能。它的核心资产是SKILL.md里的流程，不存在必须安装的formatter程序。**本次已经读到固定版本、确认流程和边界，可以在本任务中借鉴其审图方法，自行实现必要的图形修改；不需要复制到用户全局skills目录、不需要重启Codex，也不需要读取任何凭据。

应区分两种说法：

1. 可以说“参考science-plot-formatter的最终尺寸—before/after审图流程”；
2. 不能说“运行了它的formatter CLI”或“正式安装并自动验证通过”，因为没有这样的已执行步骤。

## 5. 当前项目的具体接入方式

它适合成为**概念/编码重做之后的最终物理尺寸与细节打磨层**。对本项目，优先落在配对效应、风险预报等Matplotlib数据图；概念图Fig.1的对象、结构和研究故事仍由前面的设计工作解决。

### 建议接入流程（尚未执行）

1. **选择独立render入口。**不要直接让“原样运行”触发`run.py`、模型拟合或覆盖既有analysis目录。另建一个只读取冻结panel source的绘图副本，输出到新的本地工作目录；研究源/数据不动。
2. **先确定工作宽度。**已有稿件尺寸则沿用；未知venue时把尺寸明确标成项目暂定规格，不把NeurIPS示例或推测的ICBR栏宽当官方要求。后续确定真正venue再查其指南。
3. **基线必须先看。**用本地现有Python环境与Agg渲染PNG和既有矢量格式，实际打开最终尺寸预览。记录的是具体问题，例如哪一组label被裁、哪个legend遮住哪些J点，而不是泛写“提高美观”。
4. **只改表现参数。**在副本中统一font/linewidth/markersize/figsize，按需改误差线帽及最小间距；颜色、方法顺序、坐标限、尺度、点位、CI端点、分母与独立n保持既定版本。若重构图意/编码尚未完成，先退回设计阶段，不用这条Skill掩盖结构问题。
5. **before/after审图。**逐条对照问题，查看完整图及最终物理尺寸局部。留白像素测量可辅助找边缘裁切，但背景包围框不能发现内部重叠，也不是视觉质量分数。
6. **保留语义验收。**对前后使用的J列表、panel数组、效应/CI数组、轴scale/limits及source-data哈希做一致性核对。这里只比较已定义量，不增加新的统计分析。
7. **保留审阅记录。**保存baseline、修改版、参数diff、问题resolved/partial/still present及来源commit。最多几次有目的修整；未解决的问题直接写清，不靠多次盲改冒充优化。

### 如何与前一份高星Skill方案相接

```text
概念语义与构图（canvas / schematics的有条件借鉴）
        ↓
数据编码和panel组织（scientific-visualization）
        ↓
最终尺寸、视觉重量与真实before/after验收（science-plot-formatter）
```

这是职责分工，不是四条Skill全文叠加。用户已明确当前图不满意，允许我们重做设计；不应让formatter“不改composition”的狭窄边界阻止前一层该做的设计，也不应在最终打磨时顺手改变已冻结的科学比较。

## 6. 结论

**值得优先采用其审图与物理尺寸流程，可以不安装使用。**它是小而明确的Matplotlib格式打磨Skill，最有价值的是“先真实看图、再按具体问题修改、最后再看图”，不是某个万能rcParams字典。

它不承担概念叙事、重构布局、统计计算或置信区间验证；也不自动修改配色。仓库未声明许可、没有固定依赖或自动formatter实现，应据实记录，避免把流程参考说成已安装并得到软件认证。
