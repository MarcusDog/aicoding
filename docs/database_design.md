# 数据库设计文档

## 1. 核心表

### 1.1 `contracts`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| instrument_id | string | 合约代码，如 `IF2606` |
| product_id | string | 品种代码 |
| product_name | string | 品种名称 |
| contract_month | string | 合约月份 |
| first_trade_date | date | 首次出现日期 |
| last_trade_date | date | 最后出现日期 |
| latest_open_interest | double | 最近持仓量 |
| latest_close_price | double | 最近收盘价 |

### 1.2 `trade_calendar`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| trading_date | date | 日期 |
| is_trading_day | boolean | 是否可抓取到交易数据 |
| source | string | 来源说明 |

### 1.3 `futures_daily`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| trading_date | date | 交易日 |
| product_id | string | 品种代码 |
| product_name | string | 品种名称 |
| instrument_id | string | 合约代码 |
| contract_month | string | 合约月份 |
| open_price | double | 开盘价 |
| high_price | double | 最高价 |
| low_price | double | 最低价 |
| close_price | double | 收盘价 |
| settlement_price | double | 结算价 |
| pre_settlement_price | double | 前结算价 |
| volume | double | 成交量 |
| turnover | double | 成交金额 |
| open_interest | double | 持仓量 |
| open_interest_change | double | 持仓变化 |
| source | string | 数据源 |
| source_url | string | 原始链接 |
| fetch_time | string | 抓取时间 |
| license_note | string | 使用说明 |

### 1.4 `macro_series`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| series_name | string | 指标名 |
| series_group | string | 指标组 |
| observation_date | date | 观测日期 |
| value | double | 指标值 |
| unit | string | 单位 |
| source | string | 数据源 |
| source_url | string | 原始链接 |
| fetch_time | string | 抓取时间 |
| license_note | string | 使用说明 |

### 1.5 `analysis_snapshot`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| trading_date | date | 最新交易日 |
| product_id | string | 品种代码 |
| instrument_id | string | 主力合约 |
| close_price | double | 最新收盘价 |
| daily_return | double | 日收益率 |
| rolling_ma_5 | double | 5 日均线 |
| rolling_ma_20 | double | 20 日均线 |
| rolling_vol_20 | double | 20 日滚动年化波动率 |
| var_95_hist_60 | double | 60 日历史模拟 VaR |

### 1.6 `ingestion_log`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| source_name | string | 来源名称 |
| dataset_name | string | 数据集名称 |
| request_url | string | 请求地址 |
| status | string | 成功或失败状态 |
| record_count | int | 记录数 |
| trading_date | date | 对应日期 |
| fetch_time | string | 抓取时间 |

## 2. 衍生表

### 2.1 `main_contract_daily`

- 每个交易日每个品种仅保留主力合约
- 主力规则：`open_interest` 优先，其次 `volume`，再次 `contract_month`

### 2.2 `correlation_matrix`

- 行情收益率与宏观指标统一对齐后生成的相关性矩阵

## 3. 存储策略

- Parquet 负责文件化落盘，便于论文留档与 Spark 演示
- DuckDB 负责本机查询与 API 服务
