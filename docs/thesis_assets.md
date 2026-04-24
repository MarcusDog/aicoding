# 答辩版截图与论文配图说明

本文件汇总系统当前已经准备好的答辩截图与论文配图素材，便于后续直接插入毕业论文或答辩 PPT。

## 1. 系统截图

截图由 [capture_app_screenshots.py](C:\Users\lenovo\OneDrive\Desktop\毕业设计_4\基于大数据的中国金融期货交易分析系统\scripts\capture_app_screenshots.py) 自动生成，输出目录为：

- `artifacts/thesis/screenshots/`

建议图注：

- 图 5-1 系统答辩展示页截图
- 图 5-2 合约行情页面截图
- 图 5-3 趋势与波动分析页面截图
- 图 5-4 相关性与 VaR 页面截图
- 图 5-5 数据来源与质量说明页面截图

## 2. 论文配图

图表与结构图由 [export_thesis_assets.py](C:\Users\lenovo\OneDrive\Desktop\毕业设计_4\基于大数据的中国金融期货交易分析系统\scripts\export_thesis_assets.py) 自动生成，输出目录为：

- `artifacts/thesis/figures/`
- `artifacts/thesis/diagrams/`

推荐用途：

- `fig_4_1_system_architecture.svg`：系统总体架构图
- `fig_4_2_data_flow.svg`：数据处理流程图
- `fig_3_1_data_model.svg`：数据库或核心数据模型说明
- `fig_6_1_product_comparison.png`：品种对比分析
- `fig_6_2_if_trend_ma20.png`：趋势分析
- `fig_6_3_if_drawdown_volatility.png`：风险分析
- `fig_6_4_var_bar.png`：VaR 结果展示
- `fig_6_5_correlation_heatmap.png`：宏观相关性分析
- `fig_6_6_quality_overview.png`：数据质量与抓取情况

## 3. 使用顺序建议

1. 第 3 章数据库设计：放 `fig_3_1_data_model.svg`
2. 第 4 章系统架构：放 `fig_4_1_system_architecture.svg`、`fig_4_2_data_flow.svg`
3. 第 5 章系统实现：放 `fig_5_1` 到 `fig_5_5` 系统截图
4. 第 6 章系统测试与结果分析：放 `fig_6_1` 到 `fig_6_6` 图表

## 4. 更新命令

```powershell
python scripts/refresh_data.py --days 150 --pbc-limit 6 --nbs-limit 3
python scripts/export_thesis_assets.py
python scripts/capture_app_screenshots.py
```
