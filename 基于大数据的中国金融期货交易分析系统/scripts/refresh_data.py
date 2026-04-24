from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.metrics import build_analysis_snapshot, build_correlation_matrix, build_main_contract_series
from analysis.metrics import (
    build_comparison_frame,
    build_market_overview,
    build_notice_summary,
    build_quality_report,
    build_volatility_forecast,
)
from analysis.spark_jobs import materialize_main_contract_with_spark
from ingest.sources.cffex import CffexClient
from ingest.sources.nbs import NbsClient
from ingest.sources.pbc import PbcClient
from project_config import GOLD_DIR, SOURCE_CATALOG, ensure_directories
from warehouse.storage import WarehouseStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh official public datasets for the CN futures analytics system.")
    parser.add_argument("--days", type=int, default=180, help="Calendar days to backfill from today.")
    parser.add_argument("--pbc-limit", type=int, default=6, help="Number of PBC reports to parse.")
    parser.add_argument("--nbs-limit", type=int, default=3, help="Articles to parse per NBS series.")
    parser.add_argument("--enable-spark", action="store_true", help="Also materialize a Spark local demo dataset.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_directories()
    today = date.today()
    start_date = today - timedelta(days=args.days)

    store = WarehouseStore()
    cffex = CffexClient().fetch_dataset(start_date=start_date, end_date=today)
    pbc_series, pbc_logs = PbcClient().fetch_macro_series(limit=args.pbc_limit)
    nbs_series, nbs_logs = NbsClient().fetch_macro_series(limit_per_series=args.nbs_limit)

    futures_daily = cffex.daily.sort_values(["trading_date", "product_id", "instrument_id"])
    macro_series = pd.concat([pbc_series, nbs_series], ignore_index=True) if not pbc_series.empty or not nbs_series.empty else pd.DataFrame()
    ingestion_log = pd.concat([cffex.ingestion_log, pbc_logs, nbs_logs], ignore_index=True)
    source_catalog = pd.DataFrame([source.__dict__ for source in SOURCE_CATALOG])

    main_contract_daily = build_main_contract_series(futures_daily)
    volatility_forecast = build_volatility_forecast(main_contract_daily)
    analysis_snapshot = build_analysis_snapshot(main_contract_daily, volatility_forecast=volatility_forecast)
    correlation_matrix = build_correlation_matrix(main_contract_daily, macro_series)
    comparison_frame = build_comparison_frame(main_contract_daily)
    market_overview = build_market_overview(main_contract_daily, cffex.notices, volatility_forecast=volatility_forecast)
    quality_report = build_quality_report(futures_daily, macro_series, cffex.notices, ingestion_log)
    notice_summary = build_notice_summary(cffex.notices)

    store.write_table("futures_daily", futures_daily, layer="silver")
    store.write_table("contracts", cffex.contracts, layer="silver")
    store.write_table("trade_calendar", cffex.trade_calendar, layer="silver")
    store.write_table("notice_events", cffex.notices, layer="silver")
    store.write_table("macro_series", macro_series, layer="silver")
    store.write_table("ingestion_log", ingestion_log, layer="silver")
    store.write_table("source_catalog", source_catalog, layer="silver")

    store.write_table("main_contract_daily", main_contract_daily, layer="gold")
    store.write_table("volatility_forecast", volatility_forecast, layer="gold")
    store.write_table("analysis_snapshot", analysis_snapshot, layer="gold")
    store.write_table("correlation_matrix", correlation_matrix, layer="gold")
    store.write_table("comparison_frame", comparison_frame, layer="gold")
    store.write_table("market_overview", market_overview, layer="gold")
    store.write_table("quality_report", quality_report, layer="gold")
    store.write_table("notice_summary", notice_summary, layer="gold")

    used_spark = False
    if args.enable_spark:
        spark_output = GOLD_DIR / "main_contract_daily_spark"
        used_spark = materialize_main_contract_with_spark(futures_daily, spark_output)
    print(f"futures_daily rows: {len(futures_daily)}")
    print(f"macro_series rows: {len(macro_series)}")
    print(f"notices rows: {len(cffex.notices)}")
    print(f"volatility_forecast rows: {len(volatility_forecast)}")
    print(f"spark materialized: {used_spark}")


if __name__ == "__main__":
    main()
