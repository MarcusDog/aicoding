from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable

import pandas as pd
from bs4 import BeautifulSoup

from ingest.common import build_session, fetch_from_bases, persist_raw_bytes, timestamp_utc
from project_config import LICENSE_NOTE, PRODUCT_NAMES, SUPPORTED_PRODUCTS


CONTRACT_PATTERN = re.compile(r"^(IF|IH|IC|IM)(\d{4})$")


@dataclass
class CffexFetchResult:
    daily: pd.DataFrame
    contracts: pd.DataFrame
    trade_calendar: pd.DataFrame
    notices: pd.DataFrame
    ingestion_log: pd.DataFrame


class CffexClient:
    def __init__(self) -> None:
        self.session = build_session()

    def fetch_daily_xml(self, trading_day: date) -> tuple[str, bytes]:
        relative_path = f"/sj/hqsj/rtj/{trading_day:%Y%m}/{trading_day:%d}/index.xml"
        url, payload = fetch_from_bases(self.session, relative_path)
        persist_raw_bytes("cffex", f"rtj/{trading_day:%Y%m}/{trading_day:%d}.xml", payload)
        return url, payload

    def parse_daily_xml(self, xml_bytes: bytes, source_url: str) -> pd.DataFrame:
        root = ET.fromstring(xml_bytes)
        records: list[dict[str, object]] = []
        fetched_at = timestamp_utc()

        for node in root.findall(".//dailydata"):
            record = {child.tag: (child.text or "").strip() for child in node}
            product_id = record.get("productid", "")
            instrument_id = record.get("instrumentid", "")
            if product_id not in SUPPORTED_PRODUCTS:
                continue
            match = CONTRACT_PATTERN.match(instrument_id)
            if not match:
                continue

            contract_month = match.group(2)
            open_interest = _to_float(record.get("openinterest"))
            pre_open_interest = _to_float(record.get("preopeninterest"))
            records.append(
                {
                    "trading_date": pd.to_datetime(record.get("tradingday"), format="%Y%m%d"),
                    "product_id": product_id,
                    "product_name": PRODUCT_NAMES[product_id],
                    "instrument_id": instrument_id,
                    "contract_month": contract_month,
                    "open_price": _to_float(record.get("openprice")),
                    "high_price": _to_float(record.get("highestprice")),
                    "low_price": _to_float(record.get("lowestprice")),
                    "close_price": _to_float(record.get("closeprice")),
                    "settlement_price": _to_float(record.get("settlementprice")),
                    "pre_settlement_price": _to_float(record.get("presettlementprice")),
                    "volume": _to_float(record.get("volume")),
                    "turnover": _to_float(record.get("turnover")),
                    "open_interest": open_interest,
                    "open_interest_change": open_interest - pre_open_interest,
                    "source": "CFFEX",
                    "source_url": source_url,
                    "fetch_time": fetched_at,
                    "license_note": LICENSE_NOTE,
                }
            )

        return pd.DataFrame(records)

    def fetch_daily_range(self, start_date: date, end_date: date) -> tuple[pd.DataFrame, pd.DataFrame]:
        current = start_date
        daily_frames: list[pd.DataFrame] = []
        logs: list[dict[str, object]] = []

        while current <= end_date:
            if current.weekday() >= 5:
                logs.append(
                    {
                        "source_name": "CFFEX",
                        "dataset_name": "daily_statistics",
                        "request_url": "",
                        "status": "skip_weekend",
                        "record_count": 0,
                        "trading_date": pd.Timestamp(current),
                        "fetch_time": timestamp_utc(),
                    }
                )
                current += timedelta(days=1)
                continue

            try:
                request_url, payload = self.fetch_daily_xml(current)
                parsed = self.parse_daily_xml(payload, request_url)
                if not parsed.empty:
                    daily_frames.append(parsed)
                logs.append(
                    {
                        "source_name": "CFFEX",
                        "dataset_name": "daily_statistics",
                        "request_url": request_url,
                        "status": "success",
                        "record_count": int(len(parsed)),
                        "trading_date": pd.Timestamp(current),
                        "fetch_time": timestamp_utc(),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                logs.append(
                    {
                        "source_name": "CFFEX",
                        "dataset_name": "daily_statistics",
                        "request_url": "",
                        "status": f"error:{exc.__class__.__name__}",
                        "record_count": 0,
                        "trading_date": pd.Timestamp(current),
                        "fetch_time": timestamp_utc(),
                    }
                )
            current += timedelta(days=1)

        daily = pd.concat(daily_frames, ignore_index=True) if daily_frames else pd.DataFrame()
        return daily, pd.DataFrame(logs)

    def build_contracts(self, daily_df: pd.DataFrame) -> pd.DataFrame:
        if daily_df.empty:
            return pd.DataFrame(
                columns=[
                    "instrument_id",
                    "product_id",
                    "product_name",
                    "contract_month",
                    "first_trade_date",
                    "last_trade_date",
                    "latest_open_interest",
                    "latest_close_price",
                ]
            )
        ordered = daily_df.sort_values(["instrument_id", "trading_date"])
        latest = (
            ordered.groupby("instrument_id", as_index=False)
            .tail(1)[["instrument_id", "open_interest", "close_price"]]
            .rename(
                columns={
                    "open_interest": "latest_open_interest",
                    "close_price": "latest_close_price",
                }
            )
        )
        contracts = (
            ordered.groupby(["instrument_id", "product_id", "product_name", "contract_month"], as_index=False)
            .agg(first_trade_date=("trading_date", "min"), last_trade_date=("trading_date", "max"))
            .merge(latest, on="instrument_id", how="left")
        )
        return contracts.sort_values(["product_id", "contract_month"])

    def build_trade_calendar(self, log_df: pd.DataFrame) -> pd.DataFrame:
        if log_df.empty:
            return pd.DataFrame(columns=["trading_date", "is_trading_day", "source"])
        calendar = log_df[["trading_date", "status"]].copy()
        calendar["is_trading_day"] = calendar["status"].eq("success")
        calendar["source"] = "CFFEX daily statistics"
        return calendar[["trading_date", "is_trading_day", "source"]].sort_values("trading_date")

    def fetch_notices(self, categories: Iterable[str] = ("jystz", "jysgg")) -> pd.DataFrame:
        frames = []
        for category in categories:
            relative_path = f"/{category}/"
            request_url, payload = fetch_from_bases(self.session, relative_path)
            persist_raw_bytes("cffex", f"{category}/index.html", payload)
            frames.append(self._parse_notice_list(payload, request_url, category))
        if not frames:
            return pd.DataFrame()
        notices = pd.concat(frames, ignore_index=True)
        notices = notices.drop_duplicates(subset=["title", "published_date", "category", "url"])
        return notices.sort_values("published_date", ascending=False)

    def _parse_notice_list(self, html_bytes: bytes, request_url: str, category: str) -> pd.DataFrame:
        soup = BeautifulSoup(html_bytes.decode("utf-8", errors="ignore"), "html.parser")
        items: list[dict[str, object]] = []
        fetched_at = timestamp_utc()
        for li in soup.select(".notice_list li"):
            title_link = li.find("a", class_="list_a_text")
            date_link = li.find("a", class_="time")
            if not title_link or not date_link:
                continue
            href = title_link.get("href", "").strip()
            title = " ".join(title_link.get_text(" ", strip=True).split())
            published_date = pd.to_datetime(date_link.get_text(strip=True), errors="coerce")
            if not href or not title or pd.isna(published_date):
                continue
            items.append(
                {
                    "category": category,
                    "title": title,
                    "published_date": published_date,
                    "url": f"http://www.cffex.com.cn{href}",
                    "source": "CFFEX",
                    "source_url": request_url,
                    "fetch_time": fetched_at,
                    "license_note": LICENSE_NOTE,
                }
            )
        return pd.DataFrame(items)

    def fetch_dataset(self, start_date: date, end_date: date) -> CffexFetchResult:
        daily, logs = self.fetch_daily_range(start_date, end_date)
        notices = self.fetch_notices()
        contracts = self.build_contracts(daily)
        trade_calendar = self.build_trade_calendar(logs)
        return CffexFetchResult(
            daily=daily,
            contracts=contracts,
            trade_calendar=trade_calendar,
            notices=notices,
            ingestion_log=logs,
        )


def _to_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
