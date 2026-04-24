from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.main import _build_homepage_metrics, _module_entries, DataBundle, build_display_recommendations
from src.model.labeling import build_label_template, merge_manual_labels
from src.model.predict import predict
from src.model.rule_baseline import build_rule_score
from src.model.train import train_model
from src.pipeline.cleaning import clean_calendar, clean_candidate_points, clean_complaints, clean_weather
from src.pipeline.features import build_hotspots, build_point_features


def _write_minimal_raw_dataset(base: Path) -> None:
    raw = base / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        [
            {
                "id": "c1",
                "created_at": "2025-01-01 18:00:00",
                "category": "占道经营",
                "content": "摊位占道影响通行。",
                "address": "点位A",
                "lon": 121.5200,
                "lat": 31.2900,
            },
            {
                "id": "c2",
                "created_at": "2025-01-02 19:00:00",
                "category": "油烟扰民",
                "content": "夜间油烟扰民。",
                "address": "点位B",
                "lon": 121.5250,
                "lat": 31.2910,
            },
        ]
    ).to_csv(raw / "complaints.csv", index=False)

    pd.DataFrame(
        [
            {"point_id": "p1", "point_name": "点位A", "lon": 121.5203, "lat": 31.2902, "source": "transit", "label": 1},
            {"point_id": "p2", "point_name": "点位B", "lon": 121.5251, "lat": 31.2911, "source": "mall", "label": 0},
            {"point_id": "p3", "point_name": "点位C", "lon": 121.5300, "lat": 31.2920, "source": "university", "label": 1},
            {"point_id": "p4", "point_name": "点位D", "lon": 121.5350, "lat": 31.2930, "source": "community", "label": 0},
            {"point_id": "p5", "point_name": "点位E", "lon": 121.5400, "lat": 31.2940, "source": "mall", "label": 1},
            {"point_id": "p6", "point_name": "点位F", "lon": 121.5450, "lat": 31.2950, "source": "community", "label": 0},
        ]
    ).to_csv(raw / "candidate_points.csv", index=False)

    pd.DataFrame(
        [
            {"date": "2025-01-01", "is_holiday": 1, "is_weekend": 0, "holiday_name": "new_year"},
            {"date": "2025-01-02", "is_holiday": 0, "is_weekend": 0, "holiday_name": ""},
        ]
    ).to_csv(raw / "calendar.csv", index=False)

    pd.DataFrame(
        [
            {"date": "2025-01-01", "weather_code": 1, "weather_text": "cloudy"},
            {"date": "2025-01-02", "weather_code": 61, "weather_text": "light_rain"},
        ]
    ).to_csv(raw / "weather.csv", index=False)


def test_feature_and_prediction_pipeline(tmp_path: Path) -> None:
    _write_minimal_raw_dataset(tmp_path)
    raw = tmp_path / "raw"

    complaints, _ = clean_complaints(pd.read_csv(raw / "complaints.csv"))
    points = clean_candidate_points(pd.read_csv(raw / "candidate_points.csv"))
    calendar = clean_calendar(pd.read_csv(raw / "calendar.csv"))
    weather = clean_weather(pd.read_csv(raw / "weather.csv"))

    features = build_point_features(complaints, points, calendar, weather)
    hotspots = build_hotspots(complaints)
    features = build_rule_score(features)

    assert not features.empty
    assert not hotspots.empty
    assert {"point_id", "activity_proxy", "complaint_risk", "grid_id"}.issubset(features.columns)
    assert {"activity_component", "flow_component", "low_complaint_component"}.issubset(features.columns)

    labels = build_label_template(points, features, None)
    labels.loc[labels["point_id"] == "p1", "label"] = 1
    labels.loc[labels["point_id"] == "p2", "label"] = 0
    labels.loc[labels["point_id"] == "p3", "label"] = 1
    labels.loc[labels["point_id"] == "p4", "label"] = 0
    labels.loc[labels["point_id"] == "p5", "label"] = 1
    labels.loc[labels["point_id"] == "p6", "label"] = 0
    labeled_features = merge_manual_labels(features, labels)
    assert int(labeled_features["label"].isin([0, 1]).sum()) == 6

    model_payload, metrics = train_model(labeled_features)
    assert metrics["model_source"] in {"logistic_regression", "rule_baseline_only"}

    artifacts = tmp_path / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    if model_payload:
        import joblib

        joblib.dump(model_payload, artifacts / "ranking_model.joblib")

    predictions, meta = predict(labeled_features, artifacts)
    assert not predictions.empty
    assert predictions["score"].notna().all()
    assert meta["prediction_rows"] == len(predictions)
    assert {"activity_component", "low_complaint_component", "label"}.issubset(predictions.columns)

    bundle = DataBundle(
        complaints=complaints,
        candidates=points,
        features=labeled_features,
        predictions=predictions,
        sources={"complaints": "test", "candidates": "test", "features": "test", "predictions": "test"},
        demo_mode=False,
    )
    recommendations = build_display_recommendations(bundle, complaints)
    metrics_frame = _build_homepage_metrics(bundle, complaints, recommendations)
    assert {"label", "value", "hint"}.issubset(metrics_frame.columns)
    assert len(metrics_frame) >= 6

    modules = _module_entries()
    assert len(modules) == 6
    assert {"title", "summary", "target"}.issubset(pd.DataFrame(modules).columns)
