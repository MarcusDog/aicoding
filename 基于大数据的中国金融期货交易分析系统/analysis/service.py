from __future__ import annotations

from datetime import date

import pandas as pd

from analysis.metrics import (
    build_analysis_snapshot,
    build_comparison_frame,
    build_correlation_matrix,
    build_main_contract_series,
    build_market_overview,
    build_notice_summary,
    build_quality_report,
    build_volatility_forecast,
    historical_var,
    summarize_trend,
    summarize_volatility,
)
from warehouse.storage import WarehouseStore


CORE_TABLES = [
    "contracts",
    "futures_daily",
    "macro_series",
    "notice_events",
    "ingestion_log",
    "source_catalog",
    "main_contract_daily",
    "analysis_snapshot",
    "correlation_matrix",
    "comparison_frame",
    "market_overview",
    "notice_summary",
    "quality_report",
    "volatility_forecast",
]


class AnalysisService:
    def __init__(self, store: WarehouseStore | None = None) -> None:
        self.store = store or WarehouseStore()

    def get_contracts(self, product_id: str | None = None) -> pd.DataFrame:
        df = self.store.read_table("contracts", empty_ok=True)
        if product_id and not df.empty:
            df = df[df["product_id"] == product_id]
        return df.sort_values(["product_id", "contract_month"]) if not df.empty else df

    def get_market_daily(
        self,
        product_id: str | None = None,
        instrument_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        main_only: bool = False,
        limit: int = 120,
    ) -> pd.DataFrame:
        table = "main_contract_daily" if main_only else "futures_daily"
        df = self.store.read_table(table, empty_ok=True)
        if df.empty:
            return df
        if product_id:
            df = df[df["product_id"] == product_id]
        if instrument_id and "instrument_id" in df.columns:
            df = df[df["instrument_id"] == instrument_id]
        if start_date:
            df = df[pd.to_datetime(df["trading_date"]).dt.date >= start_date]
        if end_date:
            df = df[pd.to_datetime(df["trading_date"]).dt.date <= end_date]
        return df.sort_values("trading_date").tail(limit)

    def get_trend(self, product_id: str, window: int = 20) -> dict[str, object]:
        return summarize_trend(self.store.read_table("main_contract_daily", empty_ok=True), product_id, window)

    def get_volatility(self, product_id: str, window: int = 20) -> dict[str, object]:
        main = self.store.read_table("main_contract_daily", empty_ok=True)
        forecast = self.store.read_table("volatility_forecast", empty_ok=True)
        return summarize_volatility(main, product_id, window, volatility_forecast=forecast)

    def get_volatility_forecast(self, product_id: str | None = None, limit: int = 180) -> pd.DataFrame:
        df = self.store.read_table("volatility_forecast", empty_ok=True)
        if df.empty:
            return df
        if product_id:
            df = df[df["product_id"] == product_id]
        return df.sort_values("trading_date").tail(limit)

    def get_var(self, lookback: int = 60, confidence: float = 0.95) -> pd.DataFrame:
        main = self.store.read_table("main_contract_daily", empty_ok=True)
        return historical_var(main, lookback=lookback, confidence=confidence)

    def get_correlation(self) -> pd.DataFrame:
        main = self.store.read_table("main_contract_daily", empty_ok=True)
        macro = self.store.read_table("macro_series", empty_ok=True)
        return build_correlation_matrix(main, macro)

    def get_analysis_snapshot(self) -> pd.DataFrame:
        return self.store.read_table("analysis_snapshot", empty_ok=True)

    def get_comparison_frame(self) -> pd.DataFrame:
        return self.store.read_table("comparison_frame", empty_ok=True)

    def get_market_overview(self) -> pd.DataFrame:
        return self.store.read_table("market_overview", empty_ok=True)

    def get_notice_summary(self, limit: int = 20) -> pd.DataFrame:
        df = self.store.read_table("notice_summary", empty_ok=True)
        return df.sort_values("published_date", ascending=False).head(limit) if not df.empty else df

    def get_quality_report(self) -> pd.DataFrame:
        return self.store.read_table("quality_report", empty_ok=True)

    def get_source_metadata(self) -> pd.DataFrame:
        return self.store.read_table("source_catalog", empty_ok=True)

    def get_system_health(self) -> dict[str, object]:
        tables = []
        available = set(self.store.list_tables())
        for table_name in CORE_TABLES:
            exists = table_name in available
            row_count = self.store.table_row_count(table_name) if exists else 0
            tables.append({"table_name": table_name, "exists": exists, "row_count": row_count})

        ready_tables = [item for item in tables if item["exists"] and item["row_count"] > 0]
        status = "ready" if len(ready_tables) == len(CORE_TABLES) else "partial" if ready_tables else "empty"

        snapshot = self.get_analysis_snapshot()
        latest_date = None
        if not snapshot.empty and "trading_date" in snapshot.columns:
            latest_date = pd.to_datetime(snapshot["trading_date"]).max().strftime("%Y-%m-%d")

        return {
            "status": status,
            "latest_trading_date": latest_date,
            "ready_table_count": len(ready_tables),
            "required_table_count": len(CORE_TABLES),
            "tables": tables,
            "startup_steps": [
                "python -m pip install -r requirements.txt",
                "python scripts/refresh_data.py --days 180",
                "python scripts/run_local_stack.py",
            ],
        }

    def refresh_gold_tables(self) -> None:
        futures_daily = self.store.read_table("futures_daily", empty_ok=True)
        notice_events = self.store.read_table("notice_events", empty_ok=True)
        macro_series = self.store.read_table("macro_series", empty_ok=True)
        ingestion_log = self.store.read_table("ingestion_log", empty_ok=True)

        main = build_main_contract_series(futures_daily)
        volatility_forecast = build_volatility_forecast(main)
        snapshot = build_analysis_snapshot(main, volatility_forecast=volatility_forecast)
        corr = build_correlation_matrix(main, macro_series)
        comparison = build_comparison_frame(main)
        overview = build_market_overview(main, notice_events, volatility_forecast=volatility_forecast)
        quality = build_quality_report(futures_daily, macro_series, notice_events, ingestion_log)
        notice_summary = build_notice_summary(notice_events)

        self.store.write_table("main_contract_daily", main, layer="gold")
        self.store.write_table("volatility_forecast", volatility_forecast, layer="gold")
        self.store.write_table("analysis_snapshot", snapshot, layer="gold")
        self.store.write_table("correlation_matrix", corr, layer="gold")
        self.store.write_table("comparison_frame", comparison, layer="gold")
        self.store.write_table("market_overview", overview, layer="gold")
        self.store.write_table("quality_report", quality, layer="gold")
        self.store.write_table("notice_summary", notice_summary, layer="gold")
