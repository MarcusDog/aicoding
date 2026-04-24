from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import feedparser
import pandas as pd
import requests
from bs4 import BeautifulSoup

from ..config import Config
from ..utils.text import extract_keywords, hash_text, normalize_spaces

DEFAULT_SOURCE_CATALOG = Config.PROJECT_ROOT / "backend" / "config" / "source_catalog.json"
CATALOG_KEYS = (
    "rss_sources",
    "web_sources",
    "partner_api_sources",
    "social_sources",
    "app_sources",
    "mini_program_sources",
)


def empty_catalog() -> dict[str, Any]:
    return {"metadata": {"version": "1.0"}, **{key: [] for key in CATALOG_KEYS}}


def load_source_catalog(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or DEFAULT_SOURCE_CATALOG
    if not catalog_path.exists():
        return empty_catalog()
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    for key in CATALOG_KEYS:
        catalog.setdefault(key, [])
    catalog.setdefault("metadata", {"version": "1.0"})
    return catalog


def flatten_source_catalog(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for section in CATALOG_KEYS:
        for source in catalog.get(section, []):
            item = dict(source)
            item["catalog_section"] = section
            rows.append(item)
    return rows


def source_priority(source: dict[str, Any]) -> tuple[int, int, str]:
    priority = int(source.get("priority", 0) or 0)
    weight = 1 if source.get("enabled", False) else 0
    return (-priority, -weight, source.get("name", ""))


def list_collectable_sources(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    collectable_adapters = {
        "rss",
        "atom",
        "web",
        "hot_news_api",
        "guardian_api",
        "hackernews_api",
        "lobsters_api",
        "gdelt_doc_api",
    }
    items = [
        source
        for source in flatten_source_catalog(catalog)
        if source.get("adapter") in collectable_adapters and source.get("enabled", False)
    ]
    return sorted(items, key=source_priority)


def capped_source_limit(requested_limit: int, source: dict[str, Any]) -> int:
    cap = int(source.get("max_items_per_run", 0) or 0)
    if cap > 0:
        return min(requested_limit, cap)
    return requested_limit


class DatasetImporter:
    @staticmethod
    def load(path: Path) -> list[dict[str, Any]]:
        if path.suffix.lower() == ".json":
            return json.loads(path.read_text(encoding="utf-8"))
        if path.suffix.lower() == ".jsonl":
            rows = []
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
            return rows
        if path.suffix.lower() == ".csv":
            return pd.read_csv(path).fillna("").to_dict(orient="records")
        raise ValueError(f"unsupported dataset format: {path.suffix}")

    @staticmethod
    def load_many(paths: list[Path]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for path in paths:
            records.extend(DatasetImporter.load(path))
        return records

    @staticmethod
    def discover_paths(dataset_dir: Path | None = None, dataset_paths: list[Path] | None = None) -> list[Path]:
        files: list[Path] = []
        if dataset_dir and dataset_dir.exists():
            files.extend(
                sorted(
                    path
                    for path in dataset_dir.rglob("*")
                    if path.is_file() and path.suffix.lower() in {".json", ".jsonl", ".csv"}
                )
            )
        if dataset_paths:
            files.extend([path for path in dataset_paths if path.exists()])
        unique_files: list[Path] = []
        seen: set[str] = set()
        for path in files:
            path_key = str(path.resolve())
            if path_key not in seen:
                seen.add(path_key)
                unique_files.append(path)
        return unique_files


class RSSCollector:
    def __init__(self) -> None:
        self.headers = {"User-Agent": "Mozilla/5.0 NewsMonitor/1.0"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def collect_source(self, source: dict[str, Any], limit_per_source: int) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        effective_limit = capped_source_limit(limit_per_source, source)
        timeout = float(source.get("timeout_seconds", 8) or 8)
        try:
            response = self.session.get(source["url"], timeout=timeout)
            response.raise_for_status()
            parsed = feedparser.parse(response.content)
        except (requests.RequestException, Exception):
            return results
        if getattr(parsed, "bozo", False) and not getattr(parsed, "entries", []):
            return results
        for entry in parsed.entries[:effective_limit]:
            title = normalize_spaces(entry.get("title", ""))
            if not title:
                continue
            summary_html = entry.get("summary", "") or entry.get("description", "")
            summary = BeautifulSoup(summary_html, "html.parser").get_text(" ", strip=True)
            link = entry.get("link", "")
            publish_time = entry.get("published") or entry.get("updated")
            results.append(
                {
                    "news_id": hash_text(f"{source['name']}|{link}|{title}"),
                    "title": title,
                    "content": summary,
                    "summary": summary,
                    "url": link,
                    "source": source["name"],
                    "source_type": source.get("adapter", "rss"),
                    "platform": source.get("platform", source["name"]),
                    "publish_time": publish_time,
                    "crawl_time": datetime.utcnow().isoformat(),
                    "author": entry.get("author", ""),
                    "category": source.get("category", ""),
                    "region": source.get("region", ""),
                    "keywords": extract_keywords(f"{title} {summary}"),
                    "raw_html": summary_html,
                    "lang": source.get("lang", "zh"),
                    "like_count": 0,
                    "comment_count": 0,
                    "share_count": 0,
                    "view_count": 0,
                    "interaction_total": 0,
                    "_collect_group": "rss",
                }
            )
        return results

    def collect(self, limit_per_source: int = 20, sources: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        if sources is None:
            catalog = load_source_catalog()
            sources = [source for source in catalog.get("rss_sources", []) if source.get("enabled", True)]
        results: list[dict[str, Any]] = []
        max_workers = min(8, max(len(sources), 1))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.collect_source, source, limit_per_source) for source in sources]
            for future in as_completed(futures):
                try:
                    results.extend(future.result())
                except Exception:
                    continue
        return results


class WebCollector:
    DEFAULT_LINK_HINTS = ("article", "news", "p/", "a/", ".html", "content", "detail")

    def __init__(self) -> None:
        self.headers = {"User-Agent": "Mozilla/5.0 Codex News Monitor/1.0"}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def fetch_soup(self, url: str, timeout: int = 15) -> BeautifulSoup | None:
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException:
            return None
        if response.apparent_encoding:
            response.encoding = response.apparent_encoding
        return BeautifulSoup(response.text, "html.parser")

    def allowed_domains(self, source: dict[str, Any]) -> list[str]:
        configured = source.get("allowed_domains") or []
        if configured:
            return configured
        hostname = urlparse(source["url"]).netloc
        return [hostname] if hostname else []

    def is_probable_article_link(self, href: str, source: dict[str, Any]) -> bool:
        if not href or href.startswith("#") or href.startswith("javascript:"):
            return False
        absolute = urljoin(source["url"], href)
        parsed = urlparse(absolute)
        allowed = self.allowed_domains(source)
        if allowed and parsed.netloc not in allowed:
            return False
        hints = source.get("article_path_keywords") or list(self.DEFAULT_LINK_HINTS)
        path = absolute.lower()
        if any(keyword.lower() in path for keyword in hints):
            return True
        return False

    def discover_article_links(self, source: dict[str, Any], timeout: int = 15, article_limit_override: int | None = None) -> list[str]:
        soup = self.fetch_soup(source["url"], timeout=timeout)
        if soup is None:
            return []
        links: list[str] = []
        for tag in soup.select("a[href]"):
            href = tag.get("href", "").strip()
            if not self.is_probable_article_link(href, source):
                continue
            absolute = urljoin(source["url"], href)
            if absolute not in links:
                links.append(absolute)
        max_articles = article_limit_override or int(source.get("max_articles", 5))
        return links[:max_articles]

    def extract_title(self, soup: BeautifulSoup) -> str:
        candidates = [
            "meta[property='og:title']",
            "meta[name='og:title']",
            "h1",
            "title",
        ]
        for selector in candidates:
            node = soup.select_one(selector)
            if node is None:
                continue
            if node.name == "meta":
                content = node.get("content", "")
                if content:
                    return normalize_spaces(content)
            text = node.get_text(" ", strip=True)
            if text:
                return normalize_spaces(text)
        return ""

    def extract_publish_time(self, soup: BeautifulSoup) -> str:
        candidates = [
            "meta[property='article:published_time']",
            "meta[name='pubdate']",
            "meta[name='publishdate']",
            "meta[name='date']",
            "time[datetime]",
        ]
        for selector in candidates:
            node = soup.select_one(selector)
            if node is None:
                continue
            if node.name == "time":
                value = node.get("datetime", "")
            else:
                value = node.get("content", "")
            if value:
                return normalize_spaces(value)
        return datetime.utcnow().isoformat()

    def extract_content(self, soup: BeautifulSoup) -> str:
        selectors = [
            "article",
            "main",
            "[class*='article']",
            "[class*='content']",
            "[id*='article']",
            "[id*='content']",
            "body",
        ]
        for selector in selectors:
            node = soup.select_one(selector)
            if node is None:
                continue
            text = normalize_spaces(node.get_text(" ", strip=True))
            if len(text) >= 60:
                return text
        return ""

    def collect_source(self, source: dict[str, Any], timeout: int = 8, article_limit_override: int | None = None) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for article_url in self.discover_article_links(
            source,
            timeout=timeout,
            article_limit_override=article_limit_override,
        ):
            soup = self.fetch_soup(article_url, timeout=timeout)
            if soup is None:
                continue
            title = self.extract_title(soup) or article_url
            content = self.extract_content(soup)
            if not content:
                continue
            summary = normalize_spaces(content[:160])
            records.append(
                {
                    "news_id": hash_text(f"web|{article_url}|{title}"),
                    "title": title,
                    "content": content,
                    "summary": summary,
                    "url": article_url,
                    "source": source.get("name") or urlparse(article_url).netloc,
                    "source_type": "web",
                    "platform": source.get("platform") or source.get("name") or urlparse(article_url).netloc,
                    "publish_time": self.extract_publish_time(soup),
                    "crawl_time": datetime.utcnow().isoformat(),
                    "author": "",
                    "category": source.get("category", ""),
                    "region": source.get("region", ""),
                    "keywords": extract_keywords(f"{title} {summary}"),
                    "raw_html": str(soup),
                    "lang": source.get("lang", "zh"),
                    "like_count": 0,
                    "comment_count": 0,
                    "share_count": 0,
                    "view_count": 0,
                    "interaction_total": 0,
                    "_collect_group": "web",
                }
            )
        return records

    def collect(
        self,
        sources: list[dict[str, Any]],
        limit: int | None = None,
        timeout: int = 15,
        article_limit_override: int | None = None,
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        selected_sources = sources[:limit] if limit else sources
        max_workers = min(4, max(len(selected_sources), 1))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.collect_source, source, min(timeout, 8), article_limit_override)
                for source in selected_sources
            ]
            for future in as_completed(futures):
                try:
                    records.extend(future.result())
                except Exception:
                    continue
        return records


class OpenAPICollector:
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": "Mozilla/5.0 Codex News Monitor/1.0",
            "Accept": "application/json,text/plain,*/*",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def request_json(self, url: str, timeout: int = 20) -> dict[str, Any]:
        response = self.session.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()

    def collect_hot_news(self, source: dict[str, Any], limit: int = 50) -> list[dict[str, Any]]:
        try:
            payload = self.request_json(source["url"])
        except requests.RequestException:
            return []
        rows = payload.get("data", [])[:limit]
        records: list[dict[str, Any]] = []
        for item in rows:
            title = normalize_spaces(item.get("title", ""))
            content = normalize_spaces(item.get("content", "") or title)
            publish_time = item.get("publish_time") or datetime.utcnow().isoformat()
            url = item.get("url", "")
            score = int(item.get("score", 0) or 0)
            rank = int(item.get("rank", 0) or 0)
            records.append(
                {
                    "news_id": hash_text(f"{source['name']}|{url}|{title}"),
                    "title": title,
                    "content": content,
                    "summary": content[:160],
                    "url": url,
                    "source": source["name"],
                    "source_type": "open_api",
                    "platform": source.get("platform", source["name"]),
                    "publish_time": publish_time,
                    "crawl_time": datetime.utcnow().isoformat(),
                    "author": "",
                    "category": source.get("category", ""),
                    "region": source.get("region", ""),
                    "keywords": extract_keywords(f"{title} {content}"),
                    "raw_html": "",
                    "lang": source.get("lang", "zh"),
                    "like_count": score,
                    "comment_count": 0,
                    "share_count": 0,
                    "view_count": max(score, 0),
                    "interaction_total": score + max(0, 100 - rank),
                    "_collect_group": "api",
                }
            )
        return records

    def collect_guardian(self, source: dict[str, Any], limit: int = 50) -> list[dict[str, Any]]:
        try:
            payload = self.request_json(source["url"])
        except requests.RequestException:
            return []
        rows = payload.get("response", {}).get("results", [])[:limit]
        records: list[dict[str, Any]] = []
        for item in rows:
            fields = item.get("fields", {})
            title = normalize_spaces(fields.get("headline") or item.get("webTitle", ""))
            content = normalize_spaces(fields.get("bodyText") or fields.get("trailText") or title)
            url = item.get("webUrl", "")
            records.append(
                {
                    "news_id": hash_text(f"{source['name']}|{url}|{title}"),
                    "title": title,
                    "content": content,
                    "summary": normalize_spaces(fields.get("trailText", "") or content[:160]),
                    "url": url,
                    "source": source["name"],
                    "source_type": "open_api",
                    "platform": source.get("platform", source["name"]),
                    "publish_time": item.get("webPublicationDate") or datetime.utcnow().isoformat(),
                    "crawl_time": datetime.utcnow().isoformat(),
                    "author": normalize_spaces(fields.get("byline", "")),
                    "category": source.get("category", "") or item.get("sectionName", ""),
                    "region": source.get("region", ""),
                    "keywords": extract_keywords(f"{title} {content}"),
                    "raw_html": "",
                    "lang": source.get("lang", "en"),
                    "like_count": 0,
                    "comment_count": 0,
                    "share_count": 0,
                    "view_count": 0,
                    "interaction_total": 0,
                    "_collect_group": "api",
                }
            )
        return records

    def collect_hackernews(self, source: dict[str, Any], limit: int = 50) -> list[dict[str, Any]]:
        try:
            story_ids = self.session.get(source["url"], timeout=12).json()[:limit]
        except requests.RequestException:
            return []

        def fetch_item(story_id: int) -> dict[str, Any] | None:
            try:
                return self.request_json(source["item_url_template"].format(item_id=story_id), timeout=8)
            except requests.RequestException:
                return None

        records: list[dict[str, Any]] = []
        max_workers = min(8, max(len(story_ids), 1))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_item, story_id): story_id for story_id in story_ids}
            for future in as_completed(futures):
                item = future.result()
                if not item:
                    continue
                story_id = futures[future]
                title = normalize_spaces(item.get("title", ""))
                url = item.get("url", "") or f"https://news.ycombinator.com/item?id={story_id}"
                publish_time = datetime.utcfromtimestamp(item.get("time", int(datetime.utcnow().timestamp()))).isoformat()
                score = int(item.get("score", 0) or 0)
                comments = int(item.get("descendants", 0) or 0)
                records.append(
                    {
                        "news_id": hash_text(f"{source['name']}|{story_id}|{title}"),
                        "title": title,
                        "content": normalize_spaces(title),
                        "summary": normalize_spaces(title),
                        "url": url,
                        "source": source["name"],
                        "source_type": "open_api",
                        "platform": source.get("platform", "Hacker News"),
                        "publish_time": publish_time,
                        "crawl_time": datetime.utcnow().isoformat(),
                        "author": item.get("by", ""),
                        "category": source.get("category", ""),
                        "region": source.get("region", ""),
                        "keywords": extract_keywords(title),
                        "raw_html": "",
                        "lang": source.get("lang", "en"),
                        "like_count": score,
                        "comment_count": comments,
                        "share_count": 0,
                        "view_count": 0,
                        "interaction_total": score + comments,
                        "_collect_group": "api",
                    }
                )
        return records

    def collect_lobsters(self, source: dict[str, Any], limit: int = 50) -> list[dict[str, Any]]:
        try:
            rows = self.request_json(source["url"])[:limit]
        except requests.RequestException:
            return []
        records: list[dict[str, Any]] = []
        for item in rows:
            title = normalize_spaces(item.get("title", ""))
            url = item.get("url", "") or item.get("comments_url", "")
            score = int(item.get("score", 0) or 0)
            comments = int(item.get("comment_count", 0) or 0)
            submitter = item.get("submitter_user", "")
            if isinstance(submitter, dict):
                author = submitter.get("username", "")
            else:
                author = str(submitter or "")
            records.append(
                {
                    "news_id": hash_text(f"{source['name']}|{url}|{title}"),
                    "title": title,
                    "content": normalize_spaces(item.get("description", "") or title),
                    "summary": normalize_spaces(item.get("description", "") or title)[:160],
                    "url": url,
                    "source": source["name"],
                    "source_type": "open_api",
                    "platform": source.get("platform", "Lobsters"),
                    "publish_time": item.get("created_at") or datetime.utcnow().isoformat(),
                    "crawl_time": datetime.utcnow().isoformat(),
                    "author": author,
                    "category": source.get("category", ""),
                    "region": source.get("region", ""),
                    "keywords": extract_keywords(f"{title} {item.get('description', '')}"),
                    "raw_html": "",
                    "lang": source.get("lang", "en"),
                    "like_count": score,
                    "comment_count": comments,
                    "share_count": 0,
                    "view_count": 0,
                    "interaction_total": score + comments,
                    "_collect_group": "api",
                }
            )
        return records

    def collect_gdelt(self, source: dict[str, Any], limit: int = 50) -> list[dict[str, Any]]:
        url = source["url"]
        if "maxrecords=" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}maxrecords={limit}"
        try:
            payload = self.request_json(url, timeout=25)
        except requests.RequestException:
            return []

        rows = payload.get("articles", [])[:limit]
        records: list[dict[str, Any]] = []
        for item in rows:
            title = normalize_spaces(item.get("title", ""))
            if not title:
                continue
            url = item.get("url", "")
            content = normalize_spaces(item.get("seendate", "") + " " + item.get("sourcecountry", "") + " " + title)
            publish_time = item.get("seendate") or datetime.utcnow().isoformat()
            records.append(
                {
                    "news_id": hash_text(f"{source['name']}|{url}|{title}"),
                    "title": title,
                    "content": content or title,
                    "summary": title[:160],
                    "url": url,
                    "source": source["name"],
                    "source_type": "open_api",
                    "platform": source.get("platform", "GDELT"),
                    "publish_time": publish_time,
                    "crawl_time": datetime.utcnow().isoformat(),
                    "author": "",
                    "category": source.get("category", ""),
                    "region": source.get("region", item.get("sourcecountry", "")),
                    "keywords": extract_keywords(title),
                    "raw_html": "",
                    "lang": source.get("lang", "en"),
                    "like_count": 0,
                    "comment_count": 0,
                    "share_count": 0,
                    "view_count": 0,
                    "interaction_total": 0,
                    "_collect_group": "api",
                }
            )
        return records

    def collect_source(self, source: dict[str, Any], limit_per_source: int = 50) -> list[dict[str, Any]]:
        effective_limit = capped_source_limit(limit_per_source, source)
        adapter = source.get("adapter")
        if adapter == "hot_news_api":
            records = self.collect_hot_news(source, limit=effective_limit)
        elif adapter == "guardian_api":
            records = self.collect_guardian(source, limit=effective_limit)
        elif adapter == "hackernews_api":
            records = self.collect_hackernews(source, limit=effective_limit)
        elif adapter == "lobsters_api":
            records = self.collect_lobsters(source, limit=effective_limit)
        elif adapter == "gdelt_doc_api":
            records = self.collect_gdelt(source, limit=effective_limit)
        else:
            records = []
        throttle_seconds = float(source.get("throttle_seconds", 0) or 0)
        if throttle_seconds > 0:
            time.sleep(throttle_seconds)
        return records

    def collect(self, sources: list[dict[str, Any]], limit_per_source: int = 50) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        max_workers = min(10, max(len(sources), 1))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.collect_source, source, limit_per_source) for source in sources]
            for future in as_completed(futures):
                try:
                    records.extend(future.result())
                except Exception:
                    continue
        return records


def load_sample_news(limit: int | None = None) -> list[dict[str, Any]]:
    sample_path = Config.RAW_DIR / "sample_news.json"
    records = DatasetImporter.load(sample_path)
    selected = records[:limit] if limit else records
    for record in selected:
        record["_collect_group"] = "sample"
    return selected


def load_batch_datasets(dataset_dir: Path | None = None, dataset_paths: list[Path] | None = None) -> list[dict[str, Any]]:
    paths = DatasetImporter.discover_paths(dataset_dir=dataset_dir, dataset_paths=dataset_paths)
    if not paths:
        return []
    records = DatasetImporter.load_many(paths)
    for record in records:
        record["_collect_group"] = "batch"
    return records


def collect_news(
    mode: str = "hybrid",
    sample_limit: int = 80,
    rss_limit: int = 20,
    source_config_path: Path | None = None,
    dataset_dir: Path | None = None,
    dataset_paths: list[Path] | None = None,
    web_limit: int = 0,
    api_limit: int = 50,
    include_sample: bool | None = None,
    include_batch: bool | None = None,
    include_rss: bool | None = None,
    include_web: bool | None = None,
    include_api: bool | None = None,
    api_adapters: list[str] | None = None,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    catalog = load_source_catalog(source_config_path)

    should_include_sample = include_sample if include_sample is not None else mode in {"sample", "hybrid", "full"}
    should_include_batch = include_batch if include_batch is not None else mode in {"batch", "hybrid", "full"}
    should_include_rss = include_rss if include_rss is not None else mode in {"rss", "hybrid", "full"}
    should_include_web = include_web if include_web is not None else mode in {"web", "full"}
    should_include_api = include_api if include_api is not None else mode in {"hybrid", "full"}

    if should_include_sample and sample_limit > 0:
        records.extend(load_sample_news(sample_limit))
    if should_include_batch:
        import_dir = dataset_dir or (Config.RAW_DIR / "imports")
        records.extend(load_batch_datasets(dataset_dir=import_dir, dataset_paths=dataset_paths))
    if should_include_rss and rss_limit > 0:
        rss_sources = sorted(
            [source for source in catalog.get("rss_sources", []) if source.get("enabled", True)],
            key=source_priority,
        )
        records.extend(RSSCollector().collect(limit_per_source=rss_limit, sources=rss_sources))
    if should_include_web and web_limit > 0:
        web_sources = sorted(
            [source for source in catalog.get("web_sources", []) if source.get("enabled", False)],
            key=source_priority,
        )
        records.extend(WebCollector().collect(web_sources, limit=None, timeout=15, article_limit_override=web_limit))
    if should_include_api and api_limit > 0:
        api_sources = sorted(
            [source for source in catalog.get("partner_api_sources", []) if source.get("enabled", False)],
            key=source_priority,
        )
        if api_adapters:
            allowed = set(api_adapters)
            api_sources = [source for source in api_sources if source.get("adapter") in allowed]
        records.extend(OpenAPICollector().collect(api_sources, limit_per_source=api_limit))
    return records
