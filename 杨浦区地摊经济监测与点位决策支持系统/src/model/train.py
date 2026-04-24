from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.model.rule_baseline import build_rule_score
from src.pipeline.io_utils import artifacts_dir, processed_dir, read_csv, write_csv, write_json


FEATURE_COLUMNS = [
    "complaint_risk",
    "activity_proxy",
    "flow_proxy_score",
    "weekend_complaint_ratio",
    "holiday_complaint_ratio",
    "bad_weather_ratio",
    "poi_score",
    "road_occupation_ratio",
    "activity_component",
    "flow_component",
    "temporal_component",
    "stability_component",
    "low_complaint_component",
    "street_friendly_component",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the ranking model when labels are available.")
    parser.add_argument("--features", default=str(processed_dir() / "features.csv"))
    parser.add_argument("--artifacts-dir", default=str(artifacts_dir()))
    return parser.parse_args()


def build_training_frame(features: pd.DataFrame) -> pd.DataFrame:
    scored = build_rule_score(features)
    if "label" not in scored.columns:
        scored["label"] = pd.NA
    return scored


def train_model(features: pd.DataFrame) -> tuple[dict[str, object], dict[str, float | int | str | None]]:
    trainable = build_training_frame(features)
    trainable["label"] = pd.to_numeric(trainable["label"], errors="coerce")
    labeled = trainable[trainable["label"].isin([0, 1])].copy()
    if labeled["label"].nunique() < 2 or len(labeled) < 6:
        metrics = {
            "model_source": "rule_baseline_only",
            "labeled_rows": int(len(labeled)),
            "accuracy": None,
            "f1": None,
            "feature_columns": [],
            "positive_labels": int((labeled["label"] == 1).sum()),
            "negative_labels": int((labeled["label"] == 0).sum()),
        }
        return {}, metrics

    model_features = [col for col in FEATURE_COLUMNS if col in labeled.columns]
    preprocess = ColumnTransformer(
        [
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                model_features,
            )
        ]
    )
    estimator = Pipeline(
        [
            ("preprocess", preprocess),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )

    folds = min(5, int(labeled["label"].value_counts().min()), len(labeled))
    folds = max(2, folds)
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
    preds = cross_val_predict(estimator, labeled[model_features], labeled["label"], cv=cv)
    accuracy = float(accuracy_score(labeled["label"], preds))
    f1 = float(f1_score(labeled["label"], preds))

    estimator.fit(labeled[model_features], labeled["label"])
    clf = estimator.named_steps["clf"]
    coefficients = {
        feature: float(weight)
        for feature, weight in zip(model_features, clf.coef_[0], strict=False)
    }
    payload = {"model": estimator, "feature_columns": model_features, "coefficients": coefficients}
    metrics = {
        "model_source": "logistic_regression",
        "labeled_rows": int(len(labeled)),
        "accuracy": accuracy,
        "f1": f1,
        "feature_columns": model_features,
        "positive_labels": int((labeled["label"] == 1).sum()),
        "negative_labels": int((labeled["label"] == 0).sum()),
    }
    return payload, metrics


def main() -> None:
    args = parse_args()
    features = read_csv(Path(args.features))
    model_payload, metrics = train_model(features)

    artifact_root = Path(args.artifacts_dir)
    artifact_root.mkdir(parents=True, exist_ok=True)
    if model_payload:
        joblib.dump(model_payload, artifact_root / "ranking_model.joblib")
        coefficients = model_payload.get("coefficients", {})
        if coefficients:
            coef_df = (
                pd.DataFrame({"feature": list(coefficients.keys()), "coefficient": list(coefficients.values())})
                .sort_values("coefficient", ascending=False)
                .reset_index(drop=True)
            )
            write_csv(coef_df, artifact_root / "feature_coefficients.csv")
    write_json(metrics, artifact_root / "metrics.json")
    print(f"model_source={metrics['model_source']}, labeled_rows={metrics['labeled_rows']}")


if __name__ == "__main__":
    main()
