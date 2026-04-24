from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fraud_detection.data import load_creditcard_data  # noqa: E402
from fraud_detection.evaluation import (  # noqa: E402
    plot_confusion_matrix,
    plot_curves,
    plot_threshold_tradeoff,
    save_experiment_results,
    save_json,
)
from fraud_detection.modeling import DEFAULT_EXPERIMENTS, FULL_EXPERIMENTS, run_experiment, save_model_bundle  # noqa: E402
from fraud_detection.preprocess import split_data  # noqa: E402
from fraud_detection.settings import FIGURES_DIR, METRICS_DIR, MODELS_DIR, PROCESSED_DATA_DIR, ensure_directories  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Train fraud detection models.")
    parser.add_argument("--full", action="store_true", help="Run the slower full experiment set including SMOTE.")
    parser.add_argument(
        "--split-strategy",
        choices=["temporal", "stratified"],
        default="temporal",
        help="Dataset split strategy.",
    )
    parser.add_argument(
        "--max-train-rows",
        type=int,
        default=0,
        help="Optional cap for training rows to speed up local iteration. 0 means full data.",
    )
    args = parser.parse_args()

    ensure_directories()
    frame = load_creditcard_data()
    splits = split_data(frame, strategy=args.split_strategy)

    if args.max_train_rows and len(splits.train) > args.max_train_rows:
        fraud_rows = splits.train[splits.train["Class"] == 1]
        normal_rows = splits.train[splits.train["Class"] == 0].sample(
            n=max(args.max_train_rows - len(fraud_rows), 1),
            random_state=42,
        )
        splits.train = (
            pd.concat([fraud_rows, normal_rows], ignore_index=True)
            .sample(frac=1.0, random_state=42)
            .reset_index(drop=True)
        )

    split_dir = PROCESSED_DATA_DIR / "splits"
    split_dir.mkdir(parents=True, exist_ok=True)
    splits.train.to_csv(split_dir / "train.csv", index=False)
    splits.valid.to_csv(split_dir / "valid.csv", index=False)
    splits.test.to_csv(split_dir / "test.csv", index=False)

    results = []
    raw_results = []
    experiment_specs = FULL_EXPERIMENTS if args.full else DEFAULT_EXPERIMENTS

    for spec in experiment_specs:
        result = run_experiment(spec, splits.train, splits.valid, splits.test)
        raw_results.append(result)
        results.append(
            {
                key: value
                for key, value in result.items()
                if key not in {"estimator", "feature_columns", "feature_summary", "test_scores", "y_test"}
            }
        )
        print(
            f"{spec.name}: PR-AUC={result['pr_auc']:.4f}, "
            f"Recall={result['recall']:.4f}, FPR={result['fpr']:.4f}"
        )
        save_experiment_results(results, METRICS_DIR / "experiment_results.partial.csv")

    result_frame = save_experiment_results(results, METRICS_DIR / "experiment_results.csv")
    best_name = result_frame.iloc[0]["name"]
    best_result = next(item for item in raw_results if item["name"] == best_name)

    save_json(METRICS_DIR / "best_metrics.json", result_frame.iloc[0].to_dict())
    save_model_bundle(MODELS_DIR / "best_model.joblib", best_result)
    save_json(
        METRICS_DIR / "training_summary.json",
        {
            "split_strategy": args.split_strategy,
            "train_rows": int(len(splits.train)),
            "valid_rows": int(len(splits.valid)),
            "test_rows": int(len(splits.test)),
            "experiment_count": len(experiment_specs),
            "best_experiment": best_name,
        },
    )

    test_predictions = splits.test.copy()
    test_predictions["fraud_score"] = best_result["test_scores"]
    test_predictions["predicted_class"] = (best_result["test_scores"] >= best_result["threshold"]).astype(int)
    test_predictions.to_csv(METRICS_DIR / "test_predictions.csv", index=False)

    plot_curves(best_result["y_test"], best_result["test_scores"], FIGURES_DIR, prefix="best_model")
    plot_threshold_tradeoff(best_result["y_test"], best_result["test_scores"], FIGURES_DIR, prefix="best_model")
    plot_confusion_matrix(
        best_result["y_test"],
        best_result["test_scores"],
        best_result["threshold"],
        FIGURES_DIR,
        prefix="best_model",
    )

    estimator = best_result["estimator"]
    if hasattr(estimator, "feature_importances_"):
        feature_importance = pd.DataFrame(
            {
                "feature": best_result["feature_columns"],
                "importance": estimator.feature_importances_,
            }
        ).sort_values("importance", ascending=False)
        feature_importance.to_csv(METRICS_DIR / "feature_importance.csv", index=False, encoding="utf-8-sig")
        plt.figure(figsize=(8, 6))
        top_n = feature_importance.head(15).iloc[::-1]
        plt.barh(top_n["feature"], top_n["importance"])
        plt.title("Top Feature Importances")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "best_model_feature_importance.png", dpi=200)
        plt.close()

    print(f"Best experiment: {best_name}")
    print(f"Saved model to: {MODELS_DIR / 'best_model.joblib'}")


if __name__ == "__main__":
    main()
