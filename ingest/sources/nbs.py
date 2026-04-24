from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup

from ingest.common import build_session, persist_raw_bytes, timestamp_utc
from project_config import LICENSE_NOTE, NBS_BASE_URL


LIST_PATH = "/sj/zxfb/"


class NbsClient:
    def __init__(self) -> None:
        self.session = build_session()

    def fetch_macro_series(self, limit_per_series: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
        list_url = urljoin(NBS_BASE_URL, LIST_PATH)
        response = self.session.get(list_url, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"
        html = response.text
        persist_raw_bytes("nbs", "list/index.html", html.encode("utf-8"))

        targets = {
            "cpi_yoy": "居民消费价格同比上涨",
            "ppi_yoy": "工业生产者出厂价格",
            "industrial_output_yoy": "规模以上工业增加值增长",
        }

        all_links = self._extract_links(html)
        frames: list[pd.DataFrame] = []
        logs: list[dict[str, object]] = []
        for series_name, keyword in targets.items():
            series_links = [item for item in all_links if keyword in item[0]][:limit_per_series]
            for title, href in series_links:
                article_url = urljoin(list_url, href)
                article_response = self.session.get(article_url, timeout=30)
                article_response.raise_for_status()
                article_response.encoding = "utf-8"
                article_html = article_response.text
                persist_raw_bytes(
                    "nbs",
                    f"reports/{series_name}_{_sanitize_title(title)}.html",
                    article_html.encode("utf-8", errors="ignore"),
                )
                parsed = self._parse_article(series_name, title, article_url, article_html)
                frames.append(parsed)
                logs.append(
                    {
                        "source_name": "NBS",
                        "dataset_name": series_name,
                        "request_url": article_url,
                        "status": "success",
                        "record_count": int(len(parsed)),
                        "trading_date": pd.NaT,
                        "fetch_time": timestamp_utc(),
                    }
                )

        combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        return combined.sort_values(["series_name", "observation_date"]), pd.DataFrame(logs)

    def _extract_links(self, html: str) -> list[tuple[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        links: list[tuple[str, str]] = []
        seen: set[str] = set()
        for anchor in soup.find_all("a", href=True):
            title = " ".join(anchor.get_text(" ", strip=True).split())
            href = anchor["href"].strip()
            if not title or not href.startswith("./20"):
                continue
            if href in seen:
                continue
            seen.add(href)
            links.append((title, href))
        return links

    def _parse_article(self, series_name: str, title: str, article_url: str, html: str) -> pd.DataFrame:
        text = " ".join(BeautifulSoup(html, "html.parser").get_text(" ", strip=True).split())
        observation_date = _month_end_from_title(title)
        fetch_time = timestamp_utc()
        patterns = {
            "cpi_yoy": r"居民消费价格同比上涨([-\d.]+)%",
            "ppi_yoy": r"工业生产者出厂价格同比(?:上涨|下降|降幅收窄)?\s*([-\d.]+)%",
            "industrial_output_yoy": r"规模以上工业增加值增长([-\d.]+)%",
        }
        match = re.search(patterns[series_name], text)
        rows = []
        if match:
            rows.append(
                {
                    "series_name": series_name,
                    "series_group": "NBS",
                    "observation_date": observation_date,
                    "value": float(match.group(1)),
                    "unit": "%",
                    "source": "NBS",
                    "source_url": article_url,
                    "fetch_time": fetch_time,
                    "license_note": LICENSE_NOTE,
                }
            )
        return pd.DataFrame(rows)


def _month_end_from_title(title: str) -> pd.Timestamp:
    match = re.search(r"(\d{4})年(\d{1,2})(?:—\d{1,2})?月份?", title)
    if not match:
        return pd.Timestamp(datetime.utcnow().date())
    year = int(match.group(1))
    month = int(match.group(2))
    return pd.Timestamp(pd.Period(f"{year}-{month:02d}", freq="M").end_time.date())


def _sanitize_title(title: str) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", title)
    return cleaned[:80]
