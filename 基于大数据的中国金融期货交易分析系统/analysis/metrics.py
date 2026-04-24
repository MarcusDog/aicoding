from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS_PER_YEAR = 252
EWMA_LAMBDA = 0.94


def build_main_contract_series(futures_daily: pd.DataFrame) -> pd.DataFrame:
    if futures_daily.empty:
        return pd.DataFrame()

    ranked = futures_daily.sort_values(
        ["trading_date", "product_id", "open_interest", "volume", "contract_month"],
        ascending=[True, True, False, False, False],
    ).copy()
    main = ranked.groupby(["trading_date", "product_id"], as_index=False).head(1).copy()
    main = main.sort_values(["product_id", "trading_date"]).reset_index(drop=True)

    grouped = main.groupby("product_id")
    main["daily_return"] = grouped["close_price"].pct_change()
    main["rolling_ma_5"] = grouped["close_price"].transform(lambda series: series.rolling(5, min_periods=2).mean())
    main["rolling_ma_20"] = grouped["close_price"].transform(lambda series: series.rolling(20, min_periods=5).mean())
    main["rolling_ma_60"] = grouped["close_price"].transform(lambda series: series.rolling(60, min_periods=20).mean())
    main["rolling_vol_5"] = grouped["daily_return"].transform(lambda series: _annualized_rolling_vol(series, 5))
    main["rolling_vol_20"] = grouped["daily_return"].transform(lambda series: _annualized_rolling_vol(series, 20))
    main["rolling_vol_60"] = grouped["daily_return"].transform(lambda series: _annualized_rolling_vol(series, 60))
    main["ewma_vol_20"] = grouped["daily_return"].transform(_ewma_volatility)
    main["cum_return"] = grouped["daily_return"].transform(lambda series: (1 + series.fillna(0)).cumprod() - 1)
    main["drawdown"] = grouped["close_price"].transform(_drawdown)
    main["volume_zscore_20"] = grouped["volume"].transform(_rolling_zscore)
    return main


def build_volatility_forecast(main_contract_daily: pd.DataFrame, horizon: int = 5) -> pd.DataFrame:
    if main_contract_daily.empty:
        return pd.DataFrame()

    df = _prepare_main_contract(main_contract_daily)[
        [
            "trading_date",
            "product_id",
            "instrument_id",
            "daily_return",
            "rolling_vol_5",
            "rolling_vol_20",
            "rolling_vol_60",
            "ewma_vol_20",
        ]
    ].copy()

    df["forecast_vol_5d"] = (
        0.45 * df["ewma_vol_20"].fillna(df["rolling_vol_20"])
        + 0.35 * df["rolling_vol_5"].fillna(df["rolling_vol_20"])
        + 0.20 * df["rolling_vol_20"].fillna(df["rolling_vol_60"])
    )
    df["future_realized_vol_5d"] = df.groupby("product_id")["daily_return"].transform(
        lambda series: _forward_realized_vol(series, horizon=horizon)
    )
    df["forecast_error"] = df["forecast_vol_5d"] - df["future_realized_vol_5d"]
    df["abs_error"] = df["forecast_error"].abs()
    df["model_mae_60"] = df.groupby("product_id")["abs_error"].transform(lambda series: series.rolling(60, min_periods=10).mean())
    df["vol_regime"] = pd.cut(
        df["forecast_vol_5d"],
        bins=[-np.inf, 0.12, 0.20, np.inf],
        labels=["低波动", "中波动", "高波动"],
    ).astype("string")
    df["forecast_signal"] = np.select(
        [
            df["forecast_vol_5d"] > df["rolling_vol_20"] * 1.05,
            df["forecast_vol_5d"] < df["rolling_vol_20"] * 0.95,
        ],
        ["波动可能上升", "波动可能回落"],
        default="波动大体平稳",
    )
    return df.sort_values(["product_id", "trading_date"]).reset_index(drop=True)


def build_analysis_snapshot(
    main_contract_daily: pd.DataFrame,
    volatility_forecast: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if main_contract_daily.empty:
        return pd.DataFrame()

    latest = _latest_per_product(main_contract_daily)
    latest_var = historical_var(main_contract_daily, lookback=60, confidence=0.95)
    latest = latest.merge(latest_var[["product_id", "var_value"]], on="product_id", how="left")
    latest = latest.rename(columns={"var_value": "var_95_hist_60"})

    forecast = volatility_forecast if volatility_forecast is not None else build_volatility_forecast(main_contract_daily)
    if not forecast.empty:
        latest_forecast = _latest_per_product(forecast)
        latest = latest.merge(
            latest_forecast[
                [
                    "product_id",
                    "forecast_vol_5d",
                    "future_realized_vol_5d",
                    "model_mae_60",
                    "vol_regime",
                    "forecast_signal",
                ]
            ],
            on="product_id",
            how="left",
        )

    latest["trend_signal"] = np.where(latest["close_price"] >= latest["rolling_ma_20"], "强于20日均线", "弱于20日均线")
    latest["risk_level"] = pd.cut(
        latest["rolling_vol_20"],
        bins=[-np.inf, 0.12, 0.20, np.inf],
        labels=["低", "中", "高"],
    ).astype("string")

    columns = [
        "trading_date",
        "product_id",
        "instrument_id",
        "close_price",
        "daily_return",
        "rolling_ma_5",
        "rolling_ma_20",
        "rolling_vol_20",
        "forecast_vol_5d",
        "future_realized_vol_5d",
        "model_mae_60",
        "vol_regime",
        "forecast_signal",
        "trend_signal",
        "risk_level",
        "var_95_hist_60",
    ]
    return latest[columns].sort_values("product_id").reset_index(drop=True)


def summarize_trend(main_contract_daily: pd.DataFrame, product_id: str, window: int = 20) -> dict[str, object]:
    series = _filter_product(main_contract_daily, product_id).copy()
    series["moving_average"] = series["close_price"].rolling(window, min_periods=max(2, window // 4)).mean()
    series["cum_return"] = (1 + series["daily_return"].fillna(0)).cumprod() - 1
    series["drawdown"] = _drawdown(series["close_price"])
    latest = series.tail(1)
    return {
        "product_id": product_id,
        "window": window,
        "latest_date": _date_value(latest, "trading_date"),
        "latest_close": _scalar(latest, "close_price"),
        "latest_ma": _scalar(latest, "moving_average"),
        "latest_return": _scalar(latest, "daily_return"),
        "latest_drawdown": _scalar(latest, "drawdown"),
        "series": series[
            [
                "trading_date",
                "instrument_id",
                "close_price",
                "daily_return",
                "moving_average",
                "cum_return",
                "drawdown",
            ]
        ].to_dict(orient="records"),
    }


def summarize_volatility(
    main_contract_daily: pd.DataFrame,
    product_id: str,
    window: int = 20,
    volatility_forecast: pd.DataFrame | None = None,
) -> dict[str, object]:
    series = _filter_product(main_contract_daily, product_id).copy()
    series["rolling_volatility"] = _annualized_rolling_vol(series["daily_return"], window)
    series["abs_return"] = series["daily_return"].abs()

    forecast = volatility_forecast if volatility_forecast is not None else build_volatility_forecast(main_contract_daily)
    forecast_series = _filter_product(forecast, product_id)[
        [
            "trading_date",
            "forecast_vol_5d",
            "future_realized_vol_5d",
            "model_mae_60",
            "vol_regime",
            "forecast_signal",
        ]
    ]
    if not forecast_series.empty:
        series = series.merge(forecast_series, on="trading_date", how="left")

    latest = series.tail(1)
    return {
        "product_id": product_id,
        "window": window,
        "latest_date": _date_value(latest, "trading_date"),
        "latest_volatility": _scalar(latest, "rolling_volatility"),
        "latest_forecast_vol_5d": _scalar(latest, "forecast_vol_5d"),
        "latest_regime": _value(latest, "vol_regime"),
        "latest_signal": _value(latest, "forecast_signal"),
        "model_mae_60": _scalar(latest, "model_mae_60"),
        "series": series[
            [
                "trading_date",
                "daily_return",
                "abs_return",
                "rolling_volatility",
                "forecast_vol_5d",
                "future_realized_vol_5d",
                "model_mae_60",
                "vol_regime",
                "forecast_signal",
            ]
        ].to_dict(orient="records"),
    }


def historical_var(main_contract_daily: pd.DataFrame, lookback: int = 60, confidence: float = 0.95) -> pd.DataFrame:
    results: list[dict[str, object]] = []
    prepared = _prepare_main_contract(main_contract_daily)
    for product_id in sorted(prepared["product_id"].dropna().unique()):
        series = _filter_product(prepared, product_id)["daily_return"].dropna().tail(lookback)
        if series.empty:
            continue
        percentile = np.quantile(series, 1 - confidence)
        results.append(
            {
                "product_id": product_id,
                "lookback": lookback,
                "confidence": confidence,
                "var_value": float(abs(percentile)),
                "sample_size": int(series.shape[0]),
            }
        )
    return pd.DataFrame(results)


def build_correlation_matrix(main_contract_daily: pd.DataFrame, macro_series: pd.DataFrame) -> pd.DataFrame:
    if main_contract_daily.empty:
        return pd.DataFrame()

    prepared = _prepare_main_contract(main_contract_daily)
    futures_monthly = (
        prepared.assign(month_end=pd.to_datetime(prepared["trading_date"]).dt.to_period("M").dt.to_timestamp("M"))
        .groupby(["month_end", "product_id"], as_index=False)
        .agg(monthly_return=("daily_return", lambda series: (1 + series.fillna(0)).prod() - 1))
        .pivot_table(index="month_end", columns="product_id", values="monthly_return", aggfunc="last")
        .sort_index()
    )
    if macro_series.empty:
        return futures_monthly.corr().reset_index().rename(columns={"index": "series"})

    macro_monthly = (
        macro_series.assign(month_end=pd.to_datetime(macro_series["observation_date"]).dt.to_period("M").dt.to_timestamp("M"))
        .pivot_table(index="month_end", columns="series_name", values="value", aggfunc="last")
        .sort_index()
    )
    merged = pd.concat([futures_monthly, macro_monthly], axis=1).sort_index()
    valid_columns = [column for column in merged.columns if merged[column].notna().sum() >= 2]
    if not valid_columns:
        return pd.DataFrame()
    return merged[valid_columns].corr().reset_index().rename(columns={"index": "series"})


def build_comparison_frame(main_contract_daily: pd.DataFrame) -> pd.DataFrame:
    if main_contract_daily.empty:
        return pd.DataFrame()
    df = _prepare_main_contract(main_contract_daily)
    df["normalized_close"] = df.groupby("product_id")["close_price"].transform(lambda series: series / series.iloc[0] * 100)
    df["cum_return_pct"] = df["cum_return"] * 100
    return df[
        [
            "trading_date",
            "product_id",
            "instrument_id",
            "close_price",
            "normalized_close",
            "cum_return_pct",
            "drawdown",
            "rolling_vol_20",
            "volume_zscore_20",
        ]
    ]


def build_market_overview(
    main_contract_daily: pd.DataFrame,
    notices: pd.DataFrame | None = None,
    volatility_forecast: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if main_contract_daily.empty:
        return pd.DataFrame()

    latest = _latest_per_product(main_contract_daily)
    latest["trend_signal"] = np.where(latest["close_price"] >= latest["rolling_ma_20"], "强于20日均线", "弱于20日均线")
    latest["risk_level"] = pd.cut(
        latest["rolling_vol_20"],
        bins=[-np.inf, 0.12, 0.20, np.inf],
        labels=["低", "中", "高"],
    ).astype("string")

    notice_count = 0
    latest_date = pd.to_datetime(latest["trading_date"]).max()
    if notices is not None and not notices.empty:
        notice_count = int(notices[pd.to_datetime(notices["published_date"]) >= latest_date - pd.Timedelta(days=14)].shape[0])
    latest["recent_notice_count_14d"] = notice_count

    forecast = volatility_forecast if volatility_forecast is not None else build_volatility_forecast(main_contract_daily)
    if not forecast.empty:
        latest = latest.merge(
            _latest_per_product(forecast)[["product_id", "forecast_vol_5d", "vol_regime", "forecast_signal"]],
            on="product_id",
            how="left",
        )

    return latest[
        [
            "trading_date",
            "product_id",
            "instrument_id",
            "close_price",
            "daily_return",
            "rolling_vol_20",
            "forecast_vol_5d",
            "drawdown",
            "trend_signal",
            "risk_level",
            "vol_regime",
            "forecast_signal",
            "recent_notice_count_14d",
        ]
    ].sort_values("product_id")


def build_quality_report(
    futures_daily: pd.DataFrame,
    macro_series: pd.DataFrame,
    notice_events: pd.DataFrame,
    ingestion_log: pd.DataFrame,
) -> pd.DataFrame:
    records: list[dict[str, object]] = []

    if not futures_daily.empty:
        records.append(
            {
                "dataset_name": "futures_daily",
                "row_count": int(len(futures_daily)),
                "date_start": pd.to_datetime(futures_daily["trading_date"]).min(),
                "date_end": pd.to_datetime(futures_daily["trading_date"]).max(),
                "distinct_entities": int(futures_daily["instrument_id"].nunique()),
                "missing_ratio": float(
                    futures_daily[["open_price", "high_price", "low_price", "close_price"]].isna().mean().mean()
                ),
                "last_fetch_time": pd.to_datetime(futures_daily["fetch_time"]).max(),
                "success_rate": _success_rate(ingestion_log, "daily_statistics"),
            }
        )

    if not macro_series.empty:
        records.append(
            {
                "dataset_name": "macro_series",
                "row_count": int(len(macro_series)),
                "date_start": pd.to_datetime(macro_series["observation_date"]).min(),
                "date_end": pd.to_datetime(macro_series["observation_date"]).max(),
                "distinct_entities": int(macro_series["series_name"].nunique()),
                "missing_ratio": float(macro_series["value"].isna().mean()),
                "last_fetch_time": pd.to_datetime(macro_series["fetch_time"]).max(),
                "success_rate": _success_rate(ingestion_log, None, sources=["PBC", "NBS"]),
            }
        )

    if not notice_events.empty:
        records.append(
            {
                "dataset_name": "notice_events",
                "row_count": int(len(notice_events)),
                "date_start": pd.to_datetime(notice_events["published_date"]).min(),
                "date_end": pd.to_datetime(notice_events["published_date"]).max(),
                "distinct_entities": int(notice_events["title"].nunique()),
                "missing_ratio": 0.0,
                "last_fetch_time": pd.to_datetime(notice_events["fetch_time"]).max(),
                "success_rate": 1.0,
            }
        )

    return pd.DataFrame(records)


def build_notice_summary(notice_events: pd.DataFrame) -> pd.DataFrame:
    if notice_events.empty:
        return pd.DataFrame()
    notice_events = notice_events.copy()
    notice_events["published_date"] = pd.to_datetime(notice_events["published_date"])
    notice_events["tag"] = np.where(
        notice_events["title"].str.contains("股指|沪深300|中证500|中证1000|上证50", regex=True),
        "股指相关",
        "其他",
    )
    return notice_events.sort_values("published_date", ascending=False)


def _prepare_main_contract(main_contract_daily: pd.DataFrame) -> pd.DataFrame:
    if main_contract_daily.empty:
        return main_contract_daily.copy()
    return main_contract_daily.copy().sort_values(["product_id", "trading_date"]).reset_index(drop=True)


def _latest_per_product(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    return df.sort_values(["product_id", "trading_date"]).groupby("product_id", as_index=False).tail(1).reset_index(drop=True)


def _filter_product(df: pd.DataFrame, product_id: str) -> pd.DataFrame:
    if df.empty or "product_id" not in df.columns:
        return pd.DataFrame(columns=df.columns)
    return df[df["product_id"] == product_id].sort_values("trading_date").reset_index(drop=True)


def _annualized_rolling_vol(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window, min_periods=max(2, window // 4)).std() * np.sqrt(TRADING_DAYS_PER_YEAR)


def _ewma_volatility(series: pd.Series, lam: float = EWMA_LAMBDA) -> pd.Series:
    squared = series.fillna(0).pow(2)
    variance = squared.ewm(alpha=1 - lam, adjust=False).mean()
    return np.sqrt(variance) * np.sqrt(TRADING_DAYS_PER_YEAR)


def _forward_realized_vol(series: pd.Series, horizon: int) -> pd.Series:
    values = series.to_numpy(dtype=float)
    results: list[float] = []
    for index in range(len(values)):
        future = values[index + 1 : index + 1 + horizon]
        future = future[~np.isnan(future)]
        if len(future) < max(2, horizon):
            results.append(np.nan)
            continue
        results.append(float(np.std(future, ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)))
    return pd.Series(results, index=series.index)


def _drawdown(series: pd.Series) -> pd.Series:
    running_max = series.cummax()
    return series / running_max - 1


def _rolling_zscore(series: pd.Series, window: int = 20) -> pd.Series:
    mean = series.rolling(window, min_periods=max(2, window // 4)).mean()
    std = series.rolling(window, min_periods=max(2, window // 4)).std()
    return (series - mean) / std.replace(0, np.nan)


def _success_rate(
    ingestion_log: pd.DataFrame,
    dataset_name: str | None,
    sources: list[str] | None = None,
) -> float | None:
    if ingestion_log.empty:
        return None

    subset = ingestion_log.copy()
    if dataset_name is not None:
        subset = subset[subset["dataset_name"] == dataset_name]
    if sources is not None:
        subset = subset[subset["source_name"].isin(sources)]
    subset = subset[~subset["status"].astype(str).str.startswith("skip_")]
    if subset.empty:
        return None
    return float(subset["status"].eq("success").mean())


def _scalar(df: pd.DataFrame, column: str) -> float | None:
    if df.empty or column not in df.columns:
        return None
    value = df[column].iloc[0]
    return None if pd.isna(value) else float(value)


def _value(df: pd.DataFrame, column: str) -> object | None:
    if df.empty or column not in df.columns:
        return None
    value = df[column].iloc[0]
    return None if pd.isna(value) else value


def _date_value(df: pd.DataFrame, column: str) -> str | None:
    value = _value(df, column)
    if value is None:
        return None
    return pd.to_datetime(value).strftime("%Y-%m-%d")
