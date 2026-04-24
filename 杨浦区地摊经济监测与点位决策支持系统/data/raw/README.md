# 原始数据目录

本目录只放可追溯的原始输入文件，不要把清洗后的文件覆盖回这里。

最小输入集：

- `complaints.csv`: 投诉明细
- `candidate_points.csv`: 候选点位
- `calendar.csv`: 节假日/工作日标记
- `weather.csv`: 天气明细

可选输入：

- `flow_observation.csv`: 真实客流观测
- `poi_snapshot.csv`: 地图平台导出的 POI 或活跃度快照
- `labels.csv`: 人工标注样本

建议同时保留一份来源证明到 `evidence/sources/`，包括：

- 下载页面截图
- 来源链接
- 下载日期
- 字段说明
- 授权或脱敏说明
