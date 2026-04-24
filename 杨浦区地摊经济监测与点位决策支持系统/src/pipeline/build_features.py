from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from .amap_client import AmapClient
from src.model.labeling import label_summary, merge_manual_labels, read_manual_labels
from .cleaning import clean_calendar, clean_candidate_points, clean_complaints, clean_weather
from .features import build_hotspots, build_point_features, maybe_enrich_candidate_points
from .io_utils import processed_dir, raw_dir, read_csv, write_csv, write_json
from .validation import build_validation_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build cleaned datasets and candidate-point features.")
    parser.add_argument("--raw-dir", default=str(raw_dir()))
    parser.add_argument("--processed-dir", default=str(processed_dir()))
    return parser.parse_args()


def _reuse_previous_complaint_geo(complaints, processed: Path):
    previous_path = processed / "complaints_cleaned.csv"
    if not previous_path.exists():
        return complaints
    previous = read_csv(previous_path)
    required = {"id", "lon", "lat"}
    if not required.issubset(previous.columns):
        return complaints
    merged = complaints.merge(
        previous[["id", "lon", "lat"]].rename(columns={"lon": "prev_lon", "lat": "prev_lat"}),
        on="id",
        how="left",
    )
    for col, prev_col in [("lon", "prev_lon"), ("lat", "prev_lat")]:
        merged[col] = merged[col].fillna(merged[prev_col])
    merged = merged.drop(columns=["prev_lon", "prev_lat"])
    merged["is_located"] = merged["lon"].notna() & merged["lat"].notna()
    return merged


def _reuse_previous_candidate_enrichment(candidate_points, processed: Path):
    previous_path = processed / "candidate_points_cleaned.csv"
    if not previous_path.exists():
        return candidate_points
    previous = read_csv(previous_path)
    if "point_id" not in previous.columns:
        return candidate_points
    keep_columns = [col for col in ["point_id", "lon", "lat", "poi_score"] if col in previous.columns]
    merged = candidate_points.merge(
        previous[keep_columns].rename(
            columns={col: f"prev_{col}" for col in keep_columns if col != "point_id"}
        ),
        on="point_id",
        how="left",
    )
    for col in ["lon", "lat", "poi_score"]:
        prev_col = f"prev_{col}"
        if prev_col in merged.columns:
            merged[col] = merged[col].fillna(merged[prev_col])
            merged = merged.drop(columns=[prev_col])
    return merged


def _hydrate_raw_complaints(raw_complaints, processed: Path):
    previous_path = processed / "complaints_cleaned.csv"
    if not previous_path.exists() or "id" not in raw_complaints.columns:
        return raw_complaints
    previous = read_csv(previous_path)
    required = {"id", "lon", "lat"}
    if not required.issubset(previous.columns):
        return raw_complaints
    merged = raw_complaints.merge(
        previous[["id", "lon", "lat"]].rename(columns={"lon": "prev_lon", "lat": "prev_lat"}),
        on="id",
        how="left",
    )
    for col, prev_col in [("lon", "prev_lon"), ("lat", "prev_lat")]:
        if col not in merged.columns:
            merged[col] = merged[prev_col]
        else:
            merged[col] = merged[col].fillna(merged[prev_col])
    return merged.drop(columns=["prev_lon", "prev_lat"])


def _hydrate_raw_candidates(raw_candidates, processed: Path):
    previous_path = processed / "candidate_points_cleaned.csv"
    if not previous_path.exists():
        return raw_candidates
    previous = read_csv(previous_path)
    if "point_id" not in previous.columns and "id" not in previous.columns:
        return raw_candidates
    previous = previous.rename(columns={"id": "point_id"})
    if "point_id" not in raw_candidates.columns and "id" in raw_candidates.columns:
        raw_candidates = raw_candidates.rename(columns={"id": "point_id"})
    if "point_id" not in raw_candidates.columns:
        return raw_candidates
    keep_columns = [col for col in ["point_id", "lon", "lat", "poi_score"] if col in previous.columns]
    merged = raw_candidates.merge(
        previous[keep_columns].rename(
            columns={col: f"prev_{col}" for col in keep_columns if col != "point_id"}
        ),
        on="point_id",
        how="left",
    )
    for col in ["lon", "lat", "poi_score"]:
        prev_col = f"prev_{col}"
        if prev_col not in merged.columns:
            continue
        if col not in merged.columns:
            merged[col] = merged[prev_col]
        else:
            merged[col] = merged[col].fillna(merged[prev_col])
    drop_columns = [col for col in merged.columns if col.startswith("prev_")]
    return merged.drop(columns=drop_columns)


def main() -> None:
    load_dotenv()
    args = parse_args()
    raw = raw_dir() if args.raw_dir == str(raw_dir()) else Path(os.path.abspath(args.raw_dir))
    processed = processed_dir() if args.processed_dir == str(processed_dir()) else Path(os.path.abspath(args.processed_dir))

    report = build_validation_report(raw)
    write_json(report, processed / "validation_report.json")

    if report["overall_status"] != "ok":
        raise SystemExit("Raw data schema invalid. See data/processed/validation_report.json")

    raw_complaints = _hydrate_raw_complaints(read_csv(raw / "complaints.csv"), processed)
    raw_candidates = _hydrate_raw_candidates(read_csv(raw / "candidate_points.csv"), processed)

    complaints, complaints_report = clean_complaints(
        raw_complaints,
        city_hint=os.getenv("DEFAULT_CITY_NAME"),
    )
    complaints = _reuse_previous_complaint_geo(complaints, processed)
    candidate_points = clean_candidate_points(
        raw_candidates,
        city_hint=os.getenv("DEFAULT_CITY_NAME"),
    )
    candidate_points = _reuse_previous_candidate_enrichment(candidate_points, processed)
    calendar = clean_calendar(read_csv(raw / "calendar.csv"))
    weather = clean_weather(read_csv(raw / "weather.csv"))

    amap = AmapClient.from_env()
    candidate_points = maybe_enrich_candidate_points(candidate_points, amap)

    flow_path = raw / "flow_observation.csv"
    flow_observation = read_csv(flow_path) if flow_path.exists() else None
    manual_labels = read_manual_labels(raw / "manual_labels.csv")

    features = build_point_features(complaints, candidate_points, calendar, weather, flow_observation)
    features = merge_manual_labels(features, manual_labels)
    hotspots = build_hotspots(complaints)

    write_csv(complaints, processed / "complaints_cleaned.csv")
    write_csv(candidate_points, processed / "candidate_points_cleaned.csv")
    write_csv(calendar, processed / "calendar_cleaned.csv")
    write_csv(weather, processed / "weather_cleaned.csv")
    write_csv(features, processed / "features.csv")
    write_csv(hotspots, processed / "hotspots.csv")
    write_json(
        {
            "complaints_cleaning": complaints_report,
            "feature_rows": len(features),
            "manual_label_summary": label_summary(manual_labels),
        },
        processed / "processing_report.json",
    )


if __name__ == "__main__":
    main()
