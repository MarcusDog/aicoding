from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from collections.abc import Callable
from pathlib import Path
from typing import Any

import requests


BASE_URL = "https://restapi.amap.com"


@dataclass
class AmapClient:
    api_key: str
    timeout: int = 20
    cache_path: Path | None = None
    _cache: dict[str, dict[str, Any]] = field(default_factory=dict, init=False, repr=False)

    @classmethod
    def from_env(cls) -> "AmapClient | None":
        api_key = os.getenv("AMAP_API_KEY", "").strip()
        if not api_key:
            return None
        cache_path = os.getenv("AMAP_CACHE_PATH", "").strip()
        if cache_path:
            resolved = Path(cache_path)
        else:
            resolved = Path(__file__).resolve().parents[2] / "artifacts" / "amap_cache.json"
        return cls(api_key=api_key, cache_path=resolved)

    def __post_init__(self) -> None:
        if self.cache_path is None:
            return
        try:
            if self.cache_path.exists():
                self._cache = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except Exception:
            self._cache = {}

    def _cache_key(self, path: str, params: dict[str, Any]) -> str:
        normalized = {str(key): params[key] for key in sorted(params)}
        return json.dumps({"path": path, "params": normalized}, ensure_ascii=False, sort_keys=True)

    def _write_cache(self) -> None:
        if self.cache_path is None:
            return
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps(self._cache, ensure_ascii=False, indent=2), encoding="utf-8")

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        cache_key = self._cache_key(path, params)
        cached = self._cache.get(cache_key)
        if isinstance(cached, dict):
            return cached
        response = requests.get(
            f"{BASE_URL}{path}",
            params={**params, "key": self.api_key},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if str(payload.get("status")) != "1":
            raise RuntimeError(payload.get("info", "Amap request failed"))
        self._cache[cache_key] = payload
        self._write_cache()
        return payload

    def geocode(self, address: str, city: str | None = None) -> tuple[float, float] | None:
        payload = self._get(
            "/v3/geocode/geo",
            {"address": address, "city": city or os.getenv("DEFAULT_CITY_NAME", "")},
        )
        geocodes = payload.get("geocodes") or []
        if not geocodes:
            return None
        location = geocodes[0].get("location", "")
        if not location or "," not in location:
            return None
        lon_str, lat_str = location.split(",", 1)
        return float(lon_str), float(lat_str)

    def place_text_search(
        self,
        keywords: str,
        region: str | None = None,
        page_size: int = 5,
        city_limit: bool = True,
    ) -> list[dict[str, Any]]:
        payload = self._get(
            "/v5/place/text",
            {
                "keywords": keywords,
                "region": region or os.getenv("DEFAULT_CITY_NAME", ""),
                "page_size": page_size,
                "city_limit": "true" if city_limit else "false",
            },
        )
        return payload.get("pois") or []

    def place_around(self, lon: float, lat: float, keywords: str, radius: int = 500) -> list[dict[str, Any]]:
        payload = self._get(
            "/v5/place/around",
            {
                "location": f"{lon},{lat}",
                "keywords": keywords,
                "radius": radius,
                "page_size": 25,
            },
        )
        return payload.get("pois") or []

    def resolve_address(
        self,
        address_candidates: list[str],
        city: str | None = None,
        validator: Callable[[float, float], bool] | None = None,
    ) -> tuple[float, float] | None:
        seen: set[str] = set()
        for candidate in address_candidates:
            query = str(candidate).strip()
            if not query or query in seen:
                continue
            seen.add(query)

            try:
                point = self.geocode(query, city)
            except Exception:
                point = None
            if point and (validator is None or validator(point[0], point[1])):
                return point

            try:
                pois = self.place_text_search(query, region=city, page_size=3, city_limit=True)
            except Exception:
                pois = []
            for poi in pois:
                location = str(poi.get("location", "")).strip()
                if not location or "," not in location:
                    continue
                lon_str, lat_str = location.split(",", 1)
                try:
                    lon = float(lon_str)
                    lat = float(lat_str)
                except ValueError:
                    continue
                if validator is None or validator(lon, lat):
                    return lon, lat
        return None

    def weather(self, city: str) -> dict[str, Any]:
        payload = self._get("/v3/weather/weatherInfo", {"city": city, "extensions": "base"})
        records = payload.get("lives") or []
        return records[0] if records else {}

    def poi_count(self, lon: float, lat: float, keywords: list[str], radius: int = 500) -> int:
        total = 0
        for keyword in keywords:
            total += len(self.place_around(lon, lat, keywords=keyword, radius=radius))
        return total
