from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

import requests

from project_config import CFFEX_BASE_URLS, RAW_DIR, USER_AGENT


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Connection": "keep-alive",
        }
    )
    return session


def fetch_from_bases(
    session: requests.Session,
    relative_path: str,
    bases: Iterable[str] = CFFEX_BASE_URLS,
    timeout: int = 30,
) -> tuple[str, bytes]:
    errors: list[str] = []
    for base in bases:
        url = f"{base.rstrip('/')}/{relative_path.lstrip('/')}"
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return url, response.content
        except requests.RequestException as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("Unable to fetch source. " + " | ".join(errors))


def persist_raw_bytes(source_name: str, relative_name: str, payload: bytes) -> Path:
    target = RAW_DIR / source_name / relative_name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return target


def timestamp_utc() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
