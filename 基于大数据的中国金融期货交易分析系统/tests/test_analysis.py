import numpy as np
import pandas as pd

from analysis.metrics import build_analysis_snapshot, build_main_contract_series, build_volatility_forecast, historical_var


def test_build_main_contract_series_picks_highest_open_interest() -> None:
    df = pd.DataFrame(
        [
            {"trading_date": "2026-03-17", "product_id": "IF", "instrument_id": "IF2604", "contract_month": "2604", "close_price": 3800, "open_interest": 1000, "volume": 200, "open_price": 3790, "high_price": 3810, "low_price": 3780},
            {"trading_date": "2026-03-17", "product_id": "IF", "instrument_id": "IF2606", "contract_month": "2606", "close_price": 3810, "open_interest": 2000, "volume": 150, "open_price": 3800, "high_price": 3820, "low_price": 3795},
            {"trading_date": "2026-03-18", "product_id": "IF", "instrument_id": "IF2606", "contract_month": "2606", "close_price": 3825, "open_interest": 2100, "volume": 300, "open_price": 3815, "high_price": 3830, "low_price": 3810},
        ]
    )
    df["trading_date"] = pd.to_datetime(df["trading_date"])
    result = build_main_contract_series(df)
    assert result.iloc[0]["instrument_id"] == "IF2606"
    assert result.iloc[-1]["daily_return"] > 0


def test_historical_var_returns_positive_value() -> None:
    df = pd.DataFrame(
        {
            "trading_date": pd.date_range("2026-01-01", periods=80, freq="B"),
            "product_id": ["IF"] * 80,
            "instrument_id": ["IF2606"] * 80,
            "daily_return": [0.01 if i % 3 else -0.02 for i in range(80)],
            "close_price": [3800 + i for i in range(80)],
        }
    )
    result = historical_var(df, lookback=60, confidence=0.95)
    assert not result.empty
    assert result.iloc[0]["var_value"] > 0


def test_volatility_forecast_builds_expected_columns() -> None:
    trading_dates = pd.date_range("2026-01-01", periods=120, freq="B")
    close_prices = 3800 + np.cumsum(np.where(np.arange(120) % 5 == 0, -18, 11))
    df = pd.DataFrame(
        {
            "trading_date": trading_dates,
            "product_id": ["IF"] * 120,
            "instrument_id": ["IF2606"] * 120,
            "contract_month": ["2606"] * 120,
            "close_price": close_prices,
            "open_price": close_prices - 5,
            "high_price": close_prices + 8,
            "low_price": close_prices - 12,
            "open_interest": np.linspace(1000, 3000, 120),
            "volume": np.linspace(200, 600, 120),
        }
    )
    main = build_main_contract_series(df)
    forecast = build_volatility_forecast(main)
    snapshot = build_analysis_snapshot(main, volatility_forecast=forecast)

    assert not forecast.empty
    assert {"forecast_vol_5d", "future_realized_vol_5d", "forecast_signal", "vol_regime"}.issubset(forecast.columns)
    assert forecast["forecast_vol_5d"].dropna().iloc[-1] > 0
    assert "forecast_vol_5d" in snapshot.columns
