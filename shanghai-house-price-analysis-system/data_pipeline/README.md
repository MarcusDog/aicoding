# Data Pipeline

该目录包含真实数据采集与预处理脚本：

- `collect_price_indices.py`：抓取国家统计局上海二手住宅月度指数
- `collect_lianjia_listings.py`：低频抓取链家上海二手房公开列表页
- `clean_data.py`：对链家列表页结果做去重和字段整理
- `run_pipeline.py`：一键执行上述流程

输出目录：

- `data_pipeline/outputs/official_price_indices.csv`
- `data_pipeline/outputs/raw_lianjia_listings.csv`
- `data_pipeline/outputs/cleaned_lianjia_listings.csv`

运行方式：

```powershell
python data_pipeline/run_pipeline.py
```

注意：

- 链家详情页可能触发验证码，因此首版仅使用公开列表页做样本采集
- 国家统计局页面抓取使用公开发布页面，不依赖登录
