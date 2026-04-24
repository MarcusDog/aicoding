# Thesis Blueprint

## Title

基于LightGBM的金融交易欺诈检测系统设计与实现

## Research Object

以公开信用卡交易数据为基础，研究极度不平衡场景下的金融交易欺诈检测模型选择、阈值优化方法以及服务化、准实时化系统实现路径。

## Research Goal

- 在极度不平衡数据条件下选出综合表现最优的欺诈检测模型。
- 在固定误报率约束下提高欺诈召回能力。
- 完成离线训练、在线推理、准实时监控与看板展示一体化系统。
- 形成可直接支撑毕业论文撰写的图表、截图、表格与代码证据链。

## Technical Route

真实交易数据下载 -> 时序切分与不平衡处理 -> 多模型实验 -> 验证集阈值优化 -> 最优模型落盘 -> FastAPI 服务封装 -> Kafka/Spark 准实时打分 -> Streamlit 看板展示 -> 论文图表与截图导出

## Chapter Plan

1. 绪论
2. 相关技术与理论基础
3. 需求分析与数据资源设计
4. 系统设计
5. 系统实现与关键技术
6. 测试与结果分析
7. 结论与展望

## Planned Evidence

- Figures:
  - 系统总体架构图
  - 准实时链路图
  - 模型对比图
  - PR 曲线、阈值权衡图、混淆矩阵、特征重要性图
- Tables:
  - 需求分析表
  - 数据集基本信息表
  - 数据切分结果表
  - API 接口设计表
  - 模型对比结果表
  - 功能测试结果表
- Screenshots:
  - 系统总览页面
  - 离线预测页面
  - 准实时监控页面
- Code excerpts:
  - 阈值搜索逻辑
  - 单笔预测接口
  - Spark 微批打分回调
- Formulas:
  - Precision
  - Recall
  - FPR
- References:
  - 欺诈检测经典文献
  - 不平衡学习经典文献
  - LightGBM、Spark、Kafka、OpenML 等官方或高可信来源
