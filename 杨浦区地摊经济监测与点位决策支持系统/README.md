# 杨浦区地摊经济监测系统

这是一个围绕杨浦区街区级摆摊点位推荐与可视化决策支持的本科毕业设计项目原型。当前实现重点是三件事：

- 用真实公开数据替代空想数据源，保证论文和系统都有证据链。
- 把投诉、候选点、天气、节假日统一进一条可复现的数据处理流水线。
- 提供可本机运行、可截图、可导出的答辩演示页面。

## 当前已完成

- 真实数据下载与整理
  - `data/raw/complaints.csv`
  - `data/raw/candidate_points.csv`
  - `data/raw/weather.csv`
  - `data/raw/calendar.csv`
  - `data/raw/manual_labels.csv`
- 数据清洗与特征工程
  - `src/pipeline/build_features.py`
  - `src/pipeline/cleaning.py`
  - `src/pipeline/features.py`
- 推荐与导出
  - `src/model/train.py`
  - `src/model/predict.py`
  - `src/model/rule_baseline.py`
  - `src/model/labeling.py`
- 可视化原型
  - `app/main.py`
- 证据链与论文辅助材料
  - `docs/data-sources.md`
  - `evidence/sources/`
  - `thesis/`

## 论文交付件

- 最新可提交论文：
  - `thesis/lida_thesis_workspace/deliverables/潘哲-毕业论文-公式目录修订版.docx`
  - `thesis/lida_thesis_workspace/deliverables/潘哲-毕业论文-公式目录修订版.pdf`
- 其他修订版本保留在：
  - `thesis/lida_thesis_workspace/deliverables/`

## 当前数据状态

- 已确认上海市公共数据开放平台存在正式的 `12345工单办理` 数据资源，但当前页面显示为有条件开放，且暂不向个人开放。
- 已确认上海市公共数据开放平台存在 `杨浦区生态环境点位数据`，并已保留详情页截图证据。
- 当前系统主投诉输入仍使用杨浦区政府公开的生态环境信访督察案例替代集。
- 当前高德 `web` Key 已接入，投诉坐标化覆盖率已提升到约 `95%`。

## 目录说明

- `data/raw/`：原始数据
- `data/processed/`：清洗结果、特征表、预测结果
- `src/`：数据处理、训练、预测逻辑
- `app/`：Streamlit 页面
- `docs/`：数据说明、测试说明、交付文档
- `evidence/`：截图、来源证明、下载痕迹
- `thesis/`：论文蓝图和写作素材
- `scripts/`：本机运行脚本
- `tests/`：回归测试

## 运行方式

先安装依赖：

```powershell
python -m pip install -r requirements.txt
```

跑数据流水线：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_pipeline.ps1
```

导出论文配图：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/export_assets.ps1
```

启动页面：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_app.ps1
```

抓取答辩截图：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/capture_screenshots.ps1
```

运行测试：

```powershell
pytest -q
```

## 你后续最值得补的材料

- 上海开放平台可调用权限，优先是 `12345工单办理`
- 杨浦区或上海市更完整的 12345 明细导出
- 人工标注点位样本
- 问卷或访谈结果

## 备注

如果后续拿到正式客流数据，现有工程可以直接把 `flow_proxy_score` 升级为真实客流特征，不需要推倒重来。

人工标注建议使用 `data/raw/manual_labels.csv`。现在页面内已经提供“人工标注入口”，可直接保存标签并一键重训。

为保证流水线稳定，候选点 `poi_score` 默认优先复用已清洗结果和本地规则，不再每次构建都强制请求高德周边 POI。若确实需要在线补抓，可设置环境变量 `ENABLE_AMAP_POI_ENRICH=1`。
