from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd

from src.model.rule_baseline import build_explanations, build_rule_score, minmax
from src.pipeline.io_utils import artifacts_dir, processed_dir, read_csv, write_csv, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate explainable ranking predictions.")
    parser.add_argument("--features", default=str(processed_dir() / "features.csv"))
    parser.add_argument("--artifacts-dir", default=str(artifacts_dir()))
    parser.add_argument("--output", default=str(processed_dir() / "predictions.csv"))
    return parser.parse_args()


def predict(features: pd.DataFrame, artifact_root: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    scored = build_rule_score(features)
    model_path = artifact_root / "ranking_model.joblib"
    model_source = "rule_baseline"

    if model_path.exists():
        payload = joblib.load(model_path)
        model = payload["model"]
        feature_columns = payload["feature_columns"]
        probs = model.predict_proba(scored[feature_columns])[:, 1]
        scored["model_probability"] = probs
        scored["score"] = 0.65 * minmax(pd.Series(probs, index=scored.index)) + 0.35 * scored["rule_score"]
        model_source = "hybrid_rule_lr"
    else:
        scored["model_probability"] = scored["rule_score"]
        scored["score"] = scored["rule_score"]

    scored = build_explanations(scored)
    scored = scored.sort_values(["score", "complaint_risk"], ascending=[False, True]).reset_index(drop=True)
    scored["rank"] = range(1, len(scored) + 1)

    keep_cols = [
        "grid_id",
        "point_id",
        "point_name",
        "lon",
        "lat",
        "source",
        "score",
        "rank",
        "rule_score",
        "model_probability",
        "complaint_risk",
        "activity_proxy",
        "flow_proxy_score",
        "activity_component",
        "flow_component",
        "temporal_component",
        "stability_component",
        "low_complaint_component",
        "street_friendly_component",
        "temporal_opportunity",
        "weather_stability",
        "street_friendly_score",
        "label",
        "label_source",
        "label_notes",
        "reason_1",
        "reason_2",
        "risk_level",
        "explanation_text",
    ]
    predictions = scored[[col for col in keep_cols if col in scored.columns]].copy()
    meta = {"model_source": model_source, "prediction_rows": int(len(predictions))}
    return predictions, meta


def main() -> None:
    args = parse_args()
    features = read_csv(Path(args.features))
    predictions, meta = predict(features, Path(args.artifacts_dir))
    write_csv(predictions, Path(args.output))
    write_json(meta, processed_dir() / "prediction_report.json")
    print(f"prediction_rows={meta['prediction_rows']}, model_source={meta['model_source']}")


if __name__ == "__main__":
    main()
