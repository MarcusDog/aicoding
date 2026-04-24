# 项目分析

## 基本信息

- 论文题目：基于大数据的杨浦区“地摊经济”监测系统设计与实现
- 项目根目录：`C:\Users\lenovo\OneDrive\Desktop\毕业设计_4\杨浦区`
- 开题报告：`C:\Users\lenovo\OneDrive\Desktop\毕业设计_4\杨浦区\附件4-潘哲本科毕业论文(设计)开题报告1119.docx`
- 工作模板：`C:\Users\lenovo\OneDrive\Desktop\毕业设计_4\杨浦区\thesis\lida_thesis_workspace\deliverables\thesis-working.docx`

## 项目定位

该项目不是传统意义上的交易平台，而是一个面向杨浦区街区治理场景的数据监测与推荐原型。其核心任务是把投诉替代数据、候选点位、天气与节假日等信息整合起来，形成热点观察、候选点评分、Top3 推荐和证据导出的闭环。

## 代码结构

- `src/pipeline`
  - `cleaning.py`：字段标准化、时间处理、坐标补全、去重与异常处理
  - `features.py`：空间邻域统计、投诉风险与活跃度代理特征构建
  - `build_features.py`：整合清洗、特征、热点与处理报告输出
- `src/model`
  - `rule_baseline.py`：六维规则评分与解释生成
  - `train.py`：逻辑回归训练接口与指标输出
  - `predict.py`：综合得分排序与推荐结果导出
  - `labeling.py`：人工标注模板、读取、合并与统计
- `app/main.py`
  - Streamlit 单页应用，负责指标卡、图表、推荐列表和导出能力
- `scripts`
  - `run_pipeline.ps1`：管道运行入口
  - `export_thesis_assets.py`：论文图表导出
  - `capture_app_screenshots.py`：页面截图导出

## 数据资源

- 投诉替代集：`data/raw/complaints.csv`
- 候选点位：`data/raw/candidate_points.csv`
- 天气数据：`data/raw/weather.csv`
- 节假日数据：`data/raw/calendar.csv`
- 开放平台证据：`evidence/sources/shanghai_open_12345_detail.png`、`evidence/sources/yangpu_environment_points_detail.png`

## 当前可验证结果

- 清洗后投诉记录：80 条
- 候选点位：75 个
- 热点网格：47 个
- 投诉坐标覆盖率：95%
- Top3 推荐点位：百联ZX造趣场、上海合生汇、五角场
- 自动化测试：`pytest -q` 通过
- 页面截图：`evidence/screenshots/dashboard-full.png`
- 论文图表：`evidence/figures/figure-01` 至 `figure-07`

## 论文写作重点

1. 需要如实说明：当前项目已核验上海开放平台上的 12345 工单资源，但正式演示仍采用杨浦区生态环境信访案例作为投诉替代集。
2. 需要强调：系统已实现逻辑回归训练接口，但当前生产数据缺少有效人工标注，因此正式推荐结果采用规则评分输出。
3. 需要突出：项目已经完成从数据处理、评分排序、前端展示到图表截图导出的完整原型链路。

## 风险与处理

- 风险一：模板前置页破坏。
  - 处理：沿用学校模板转换出的 `thesis-working.docx`，仅替换字段和正文。
- 风险二：截图误用其他项目页面。
  - 处理：已在独立端口重新抓取当前项目真实页面。
- 风险三：参考文献失真。
  - 处理：仅保留已核验的论文、官方文档和开放平台页面。
