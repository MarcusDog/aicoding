from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup

from ingest.common import build_session, persist_raw_bytes, timestamp_utc
from project_config import LICENSE_NOTE, PBC_BASE_URL


LIST_PATH = "/diaochatongjisi/116219/116225/index.html"


class PbcClient:
    def __init__(self) -> None:
        self.session = build_session()

    def fetch_macro_series(self, limit: int = 6) -> tuple[pd.DataFrame, pd.DataFrame]:
        list_url = urljoin(PBC_BASE_URL, LIST_PATH)
        response = self.session.get(list_url, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"
        html = response.text
        persist_raw_bytes("pbc", "list/index.html", html.encode("utf-8"))

        links = self._extract_report_links(html)
        logs: list[dict[str, object]] = []
        series_frames: list[pd.DataFrame] = []
        for title, href in links[:limit]:
            article_url = urljoin(PBC_BASE_URL, href)
            article_response = self.session.get(article_url, timeout=30)
            article_response.raise_for_status()
            article_response.encoding = "utf-8"
            article_html = article_response.text
            persist_raw_bytes(
                "pbc",
                f"reports/{_sanitize_title(title)}.html",
                article_html.encode("utf-8", errors="ignore"),
            )
            series_frames.append(self._parse_article(title, article_url, article_html))
            logs.append(
                {
                    "source_name": "PBC",
                    "dataset_name": "macro_series",
                    "request_url": article_url,
                    "status": "success",
                    "record_count": int(len(series_frames[-1])),
                    "trading_date": pd.NaT,
                    "fetch_time": timestamp_utc(),
                }
            )
        combined = pd.concat(series_frames, ignore_index=True) if series_frames else pd.DataFrame()
        return combined.sort_values(["series_name", "observation_date"]), pd.DataFrame(logs)

    def _extract_report_links(self, html: str) -> list[tuple[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        seen: set[str] = set()
        links: list[tuple[str, str]] = []
        for anchor in soup.find_all("a", href=True):
            title = " ".join(anchor.get_text(" ", strip=True).split())
            href = anchor["href"].strip()
            if "金融统计数据报告" not in title:
                continue
            if href in seen:
                continue
            seen.add(href)
            links.append((title, href))
        return links

    def _parse_article(self, title: str, article_url: str, html: str) -> pd.DataFrame:
        text = " ".join(BeautifulSoup(html, "html.parser").get_text(" ", strip=True).split())
        observation_date = _month_end_from_title(title)
        fetch_time = timestamp_utc()
        metrics = {
            "social_financing_stock_yoy": re.search(r"社会融资规模存量.*?同比增长([-\d.]+)%", text),
            "m2_yoy": re.search(r"广义货币\(M2\)余额.*?同比增长([-\d.]+)%", text),
            "m1_yoy": re.search(r"狭义货币\(M1\)余额.*?同比增长([-\d.]+)%", text),
            "loan_yoy": re.search(r"人民币贷款余额.*?同比增长([-\d.]+)%", text),
            "interbank_rate": re.search(r"同业拆借月加权平均利率为([-\d.]+)%", text),
        }
        rows = []
        for series_name, match in metrics.items():
            if not match:
                continue
            rows.append(
                {
                    "series_name": series_name,
                    "series_group": "PBC",
                    "observation_date": observation_date,
                    "value": float(match.group(1)),
                    "unit": "%",
                    "source": "PBC",
                    "source_url": article_url,
                    "fetch_time": fetch_time,
                    "license_note": LICENSE_NOTE,
                }
            )
        return pd.DataFrame(rows)


def _month_end_from_title(title: str) -> pd.Timestamp:
    match = re.search(r"(\d{4})年(\d{1,2})月", title)
    if not match:
        return pd.Timestamp(datetime.utcnow().date())
    year = int(match.group(1))
    month = int(match.group(2))
    return pd.Timestamp(pd.Period(f"{year}-{month:02d}", freq="M").end_time.date())


def _sanitize_title(title: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff-]+", "_", title)[:80]
