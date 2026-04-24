from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd

from src.pipeline.amap_client import AmapClient
from src.pipeline.cleaning import clean_candidate_points
from src.pipeline.io_utils import raw_dir, read_csv, write_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch optional Amap context for candidate points.")
    parser.add_argument("--candidate-file", default=str(raw_dir() / "candidate_points.csv"))
    parser.add_argument("--poi-output", default=str(raw_dir() / "poi_snapshot.csv"))
    parser.add_argument("--weather-output", default=str(raw_dir() / "weather_live.csv"))
    parser.add_argument("--city-adcode", default=os.getenv("AMAP_OUTPUT_ADCODE", "310110"))
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    client = AmapClient.from_env()
    if client is None:
        raise SystemExit("Missing AMAP_API_KEY. Set it in .env or the shell environment first.")

    args = parse_args()
    points = clean_candidate_points(read_csv(Path(args.candidate_file)), city_hint=os.getenv("DEFAULT_CITY_NAME"))
    if points.empty:
        raise SystemExit("No valid candidate points found.")

    poi_rows = []
    for _, row in points.iterrows():
        poi_count = client.poi_count(
            float(row["lon"]),
            float(row["lat"]),
            keywords=["地铁站", "商场", "学校", "办公楼", "小吃", "夜市"],
            radius=500,
        )
        poi_rows.append(
            {
                "point_id": row["point_id"],
                "point_name": row["point_name"],
                "lon": row["lon"],
                "lat": row["lat"],
                "poi_count": poi_count,
                "source": "amap-poi-around",
            }
        )

    weather = client.weather(args.city_adcode)
    weather_rows = []
    if weather:
        weather_rows.append(
            {
                "date": pd.Timestamp.utcnow().date().isoformat(),
                "weather_code": weather.get("weather", ""),
                "weather_text": weather.get("weather", ""),
                "temp_low": weather.get("temperature_float", weather.get("temperature")),
                "temp_high": weather.get("temperature_float", weather.get("temperature")),
                "source": "amap-live-weather",
            }
        )

    write_csv(pd.DataFrame(poi_rows), Path(args.poi_output))
    if weather_rows:
        write_csv(pd.DataFrame(weather_rows), Path(args.weather_output))
    print(f"poi_rows={len(poi_rows)}, weather_rows={len(weather_rows)}")


if __name__ == "__main__":
    main()
