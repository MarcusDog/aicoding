# 真实数据与证据链清单

更新日期：2026-03-19

## 当前已落盘的主数据

| 文件 | 当前用途 | 来源 | 状态 |
| --- | --- | --- | --- |
| `data/raw/complaints.csv` | 主投诉输入 | 杨浦区政府公开的生态环境信访督察案例 | 已落盘，可直接跑管道 |
| `data/raw/complaints_environment_cases.csv` | 投诉替代原始集 | 杨浦区政府“群众信访举报转办及被督察区查处情况一览表” | 已落盘，共 80 条 |
| `data/raw/candidate_points.csv` | 候选点位主数据 | OpenStreetMap Overpass API | 已落盘，共 75 条 |
| `data/raw/weather.csv` | 天气主数据 | Open-Meteo Archive API | 已落盘，2025 全年 |
| `data/raw/calendar.csv` | 节假日日历 | 国务院办公厅 2025 节假日安排 | 已落盘，2025 全年 |
| `data/raw/yangpu_environment_enforcement_index.csv` | 治理背景索引 | 杨浦区生态环境执法栏目 | 已落盘 |
| `data/raw/yangpu_environment_monitoring_index.csv` | 治理背景索引 | 杨浦区生态环境监测栏目 | 已落盘 |
| `evidence/sources/yangpu_yearbook_2023.pdf` | 区情与统计背景材料 | 杨浦区年鉴 | 已落盘 |

## 已核验的上海市公共数据开放平台资源

### 1. 12345工单办理

- 平台地址：<https://data.sh.gov.cn/view/detail/index.html?type=jk&&id=1053&&companyFlag=0>
- 数据来源部门：上海市生态环境局
- 开放类型：有条件开放
- 额外限制：页面明确写明“该项数据资源暂不向个人开放”
- 数据量：224801 条
- 数据时间范围：2019 年至 2025 年
- 主要字段：
  - `st_appeal_address` 诉求地址
  - `st_name` 事项名称
  - `st_classification` 分类
  - `st_origin_department` 污染属地
  - `st_report_type` 举报性质
  - `dt_call_time` 来电日期
  - `dt_release_time` 提交时间
  - `st_content` 内容描述
- 证据截图：
  - `evidence/sources/shanghai_open_12345_detail.png`

结论：
- 这条资源对论文证据链非常重要，因为它证明上海开放平台上确实存在正式的 12345 工单类数据。
- 但当前账号状态下只能看到元数据、字段说明和样例，不能直接拿到完整接口地址或批量数据。
- 因此它目前适合作为“目标主数据源已存在”的平台证据，不适合作为本轮可复现的实际训练集。

### 2. 杨浦区生态环境点位数据

- 平台地址：<https://data.sh.gov.cn/view/detail/index.html?type=jk&&id=O2813838122025001&&companyFlag=0>
- 数据来源部门：上海市杨浦区人民政府
- 开放类型：无条件开放
- 空间范围：杨浦区
- 数据量：232 条
- 更新时间：2026-03-18
- 摘要：空气质量、道路尘降、工地扬尘、河道水质、声环境等相关点位数据
- 主要字段：
  - `dianwei_name` 点位名称
  - `dwdz` 点位地址
  - `dianwei_jd` 点位经度
  - `dianwei_wd` 点位维度
  - `dianwei_type` 类型
  - `jcrq` 日期
  - `jcl` 数据1
  - `jcl2` 数据2
- 证据截图：
  - `evidence/sources/yangpu_environment_points_detail.png`

结论：
- 这是目前在上海市公共数据开放平台上找到的、与“杨浦区 + 空间点位 + 环境治理”最贴近的真实数据。
- 页面能直接核验字段、样例、更新时间和空间范围，足以进入论文正文作为“杨浦区真实开放数据源”。
- 页面仍提示需要实名认证后查看接口服务地址，因此本轮没有直接批量下载完整表。

## 当前项目对真实数据的使用口径

- `complaints.csv`：当前使用杨浦区政府公开生态环境信访案例作为真实投诉替代集。
- `candidate_points.csv`：当前使用 OSM 抓取的杨浦区地铁站、高校、商圈、市场等候选点位。
- 高德 Web API：当前已经接入 `web` Key，用于地理编码与 POI 活跃度补强。
- 上海开放平台资源：当前作为“平台存在性与字段证据”进入论文与答辩证据链。

## 本轮新增结果

- 已修复高德坐标化流程，`data/processed/processing_report.json` 当前结果：
  - `geocoded_rows = 76`
  - `geo_coverage_ratio = 0.95`
- 已重新生成：
  - `data/processed/complaints_cleaned.csv`
  - `data/processed/features.csv`
  - `data/processed/predictions.csv`

## 仍待你补充的最优先材料

- 上海开放平台可用的企业或实名账号权限。
  - 有了这个权限，我可以继续尝试直接拉取 `12345工单办理` 或 `杨浦区生态环境点位数据` 的完整接口数据。
- 如果你手里有杨浦区或上海市 12345 明细下载链接、截图或导出文件，也可以直接替换当前 `complaints.csv`。
