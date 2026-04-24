from __future__ import annotations

from datetime import date

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from analysis.service import AnalysisService


app = FastAPI(title="中国股指期货盘后分析系统 API", version="1.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

service = AnalysisService()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "CN Index Futures Analytics API", "docs": "/docs", "health": "/api/system/health"}


@app.get("/api/system/health")
def get_system_health() -> dict[str, object]:
    return service.get_system_health()


@app.get("/api/contracts")
def get_contracts(product_id: str | None = Query(default=None)) -> list[dict[str, object]]:
    return service.get_contracts(product_id=product_id).to_dict(orient="records")


@app.get("/api/market/daily")
def get_market_daily(
    product_id: str | None = Query(default=None),
    instrument_id: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    main_only: bool = Query(default=False),
    limit: int = Query(default=120, ge=1, le=1000),
) -> list[dict[str, object]]:
    return service.get_market_daily(
        product_id=product_id,
        instrument_id=instrument_id,
        start_date=start_date,
        end_date=end_date,
        main_only=main_only,
        limit=limit,
    ).to_dict(orient="records")


@app.get("/api/analysis/trend")
def get_trend(product_id: str = Query(...), window: int = Query(default=20, ge=2, le=120)) -> dict[str, object]:
    return service.get_trend(product_id=product_id, window=window)


@app.get("/api/analysis/volatility")
def get_volatility(product_id: str = Query(...), window: int = Query(default=20, ge=2, le=120)) -> dict[str, object]:
    return service.get_volatility(product_id=product_id, window=window)


@app.get("/api/analysis/volatility-forecast")
def get_volatility_forecast(
    product_id: str | None = Query(default=None),
    limit: int = Query(default=180, ge=1, le=1000),
) -> list[dict[str, object]]:
    return service.get_volatility_forecast(product_id=product_id, limit=limit).to_dict(orient="records")


@app.get("/api/analysis/correlation")
def get_correlation() -> list[dict[str, object]]:
    return service.get_correlation().to_dict(orient="records")


@app.get("/api/analysis/overview")
def get_overview() -> list[dict[str, object]]:
    return service.get_market_overview().to_dict(orient="records")


@app.get("/api/analysis/comparison")
def get_comparison() -> list[dict[str, object]]:
    return service.get_comparison_frame().to_dict(orient="records")


@app.get("/api/analysis/var")
def get_var(
    confidence: float = Query(default=0.95, ge=0.8, le=0.999),
    lookback: int = Query(default=60, ge=20, le=252),
) -> list[dict[str, object]]:
    return service.get_var(confidence=confidence, lookback=lookback).to_dict(orient="records")


@app.get("/api/metadata/sources")
def get_sources() -> list[dict[str, object]]:
    return service.get_source_metadata().to_dict(orient="records")


@app.get("/api/metadata/quality")
def get_quality() -> list[dict[str, object]]:
    return service.get_quality_report().to_dict(orient="records")


@app.get("/api/metadata/notices")
def get_notices(limit: int = Query(default=20, ge=1, le=100)) -> list[dict[str, object]]:
    return service.get_notice_summary(limit=limit).to_dict(orient="records")
