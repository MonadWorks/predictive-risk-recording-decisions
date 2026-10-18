# Graphical abstract — archived version 4

2026-10-18，正式保存为 v4 版式。最后提出的横轴标题上移已取消，最终图像与此前审阅的 v4 逐字节一致；历史 ZIP 保留。论文题目：**Predictive Risk and Recording Decisions in Partially Observed Neural Networks**。

- `graphical_abstract.pdf`：正式矢量 PDF。
- `graphical_abstract.svg`：可编辑矢量资产。
- `graphical_abstract.png`：300 dpi 预览。
- `graphical_abstract_copy.md`：按模块整理的正式文案，包含四行底部文字。
- `graphical_abstract_text.txt`：从最终 PDF 提取的全文。
- `source/render_graphical_abstract.py`：渲染入口。
- `source/optical_grid.py`：字体、布局、整组间距与对齐规则。
- `source/baseline/`：保留的 Claude v4 原始绘图代码、冻结数据与网络实例。
- `source/fonts/`：此次本机渲染使用的字体副本。
- `semantic_fact_audit.json`、`verification.json`：数值、语义和排版核查。
- `editorial_review_v2.md`：文案候选、选择理由与参考来源。
- `SHA256SUMS.json`：正式快照与源文件的校验值。

## 后续修改和重渲染

在此目录下运行：

```sh
python3 -m pip install -r source/requirements.txt
python3 source/render_graphical_abstract.py
python3 source/audit_graphical_abstract.py
```

新渲染输出到 `rendered/`，不会直接覆盖本目录的正式快照。审阅后再决定是否更新正式版本。脚本及所需数据使用相对路径，可整体移动目录。字体为原本本机使用的 BentonSans、Times New Roman 和 JuliaMono；不将字体描述为开源字体。

本次只调整图形摘要的布局与一句结论措辞，没有重新估计结果，也没有投稿或上传。主论文正文 PDF 未因这次图形摘要归档而修改。
