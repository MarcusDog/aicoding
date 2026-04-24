from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import joblib
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from fraud_detection.evaluation import compute_metrics, optimize_threshold
from fraud_detection.preprocess import get_feature_columns, make_sampler


@dataclass
class ExperimentSpec:
    name: str
    model_name: str
    sampling: str = "none"
    weighted: bool = False


DEFAULT_EXPERIMENTS = [
    ExperimentSpec(name="logreg_baseline", model_name="logreg", sampling="none", weighted=False),
    ExperimentSpec(name="rf_weighted", model_name="random_forest", sampling="none", weighted=True),
    ExperimentSpec(name="lightgbm_baseline", model_name="lightgbm", sampling="none", weighted=False),
    ExperimentSpec(name="lightgbm_undersample", model_name="lightgbm", sampling="undersample", weighted=False),
    ExperimentSpec(name="lightgbm_weighted", model_name="lightgbm", sampling="none", weighted=True),
]

FULL_EXPERIMENTS = DEFAULT_EXPERIMENTS + [
    ExperimentSpec(name="logreg_smote", model_name="logreg", sampling="smote", weighted=False),
    ExperimentSpec(name="lightgbm_smote", model_name="lightgbm", sampling="smote", weighted=False),
]


def _class_weight_ratio(y: pd.Series) -> float:
    positive = float(y.sum())
    negative = float(len(y) - positive)
    return 1.0 if positive == 0 else negative / positive


def build_estimator(model_name: str, weighted: bool, class_weight_ratio: float, random_state: int = 42):
    if model_name == "logreg":
        class_weight = "balanced" if weighted else None
        return Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000, class_weight=class_weight, random_state=random_state)),
            ]
        )

    if model_name == "random_forest":
        class_weight = "balanced_subsample" if weighted else None
        return RandomForestClassifier(
            n_estimators=120,
            max_depth=8,
            n_jobs=-1,
            random_state=random_state,
            class_weight=class_weight,
        )

    if model_name == "lightgbm":
        kwargs: dict[str, Any] = {
            "n_estimators": 250,
            "learning_rate": 0.05,
            "num_leaves": 63,
            "subsample": 0.9,
            "colsample_bytree": 0.8,
            "objective": "binary",
            "random_state": random_state,
            "n_jobs": -1,
            "verbosity": -1,
        }
        if weighted:
            kwargs["scale_pos_weight"] = class_weight_ratio
        return LGBMClassifier(**kwargs)

    raise ValueError(f"Unsupported model: {model_name}")


def _robust_summary(frame: pd.DataFrame) -> dict[str, dict[str, float]]:
    summary = {}
    for column in frame.columns:
        q1 = float(frame[column].quantile(0.25))
        q3 = float(frame[column].quantile(0.75))
        summary[column] = {
            "median": float(frame[column].median()),
            "iqr": max(q3 - q1, 1e-9),
        }
    return summary


def run_experiment(
    spec: ExperimentSpec,
    train_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    test_df: pd.DataFrame,
    fixed_fpr: float = 0.01,
    random_state: int = 42,
) -> dict[str, Any]:
    target_col = "Class"
    feature_columns = get_feature_columns(train_df, target_col=target_col)

    X_train = train_df[feature_columns]
    y_train = train_df[target_col]
    X_valid = valid_df[feature_columns]
    y_valid = valid_df[target_col].to_numpy()
    X_test = test_df[feature_columns]
    y_test = test_df[target_col].to_numpy()

    sampler = make_sampler(spec.sampling, random_state=random_state)
    if sampler is not None:
        X_resampled, y_resampled = sampler.fit_resample(X_train, y_train)
        X_train_fit = pd.DataFrame(X_resampled, columns=feature_columns)
        y_train_fit = pd.Series(y_resampled)
    else:
        X_train_fit = X_train.copy()
        y_train_fit = y_train.copy()

    class_weight_ratio = _class_weight_ratio(y_train)
    estimator = build_estimator(spec.model_name, spec.weighted, class_weight_ratio, random_state=random_state)
    estimator.fit(X_train_fit, y_train_fit)

    valid_scores = estimator.predict_proba(X_valid)[:, 1]
    threshold, valid_snapshot = optimize_threshold(y_valid, valid_scores, max_fpr=fixed_fpr)

    test_scores = estimator.predict_proba(X_test)[:, 1]
    metrics = compute_metrics(y_test, test_scores, threshold=threshold, max_fpr=fixed_fpr)
    feature_summary = _robust_summary(X_train)

    return {
        "name": spec.name,
        "model_name": spec.model_name,
        "sampling": spec.sampling,
        "weighted": spec.weighted,
        **metrics,
        "valid_precision": valid_snapshot["precision"],
        "valid_recall": valid_snapshot["recall"],
        "valid_f1": valid_snapshot["f1"],
        "valid_fpr": valid_snapshot["fpr"],
        "estimator": estimator,
        "feature_columns": feature_columns,
        "feature_summary": feature_summary,
        "test_scores": test_scores,
        "y_test": y_test,
    }


def save_model_bundle(output_path, result: dict[str, Any]) -> None:
    bundle = {
        "estimator": result["estimator"],
        "feature_columns": result["feature_columns"],
        "threshold": result["threshold"],
        "metrics": {key: value for key, value in result.items() if isinstance(value, (int, float, str, bool))},
        "feature_summary": result["feature_summary"],
        "model_name": result["model_name"],
        "sampling": result["sampling"],
        "weighted": result["weighted"],
    }
    joblib.dump(bundle, output_path)
