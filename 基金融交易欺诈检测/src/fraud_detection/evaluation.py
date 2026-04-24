from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    auc,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def false_positive_rate(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    denominator = fp + tn
    return 0.0 if denominator == 0 else fp / denominator


def recall_at_fixed_fpr(y_true: np.ndarray, scores: np.ndarray, max_fpr: float = 0.01) -> float:
    fpr, tpr, _ = roc_curve(y_true, scores)
    valid = tpr[fpr <= max_fpr]
    if valid.size == 0:
        return 0.0
    return float(valid.max())


def optimize_threshold(
    y_true: np.ndarray,
    scores: np.ndarray,
    max_fpr: float = 0.01,
) -> tuple[float, dict[str, float]]:
    quantile_grid = np.linspace(0.0, 1.0, 513)
    thresholds = np.unique(np.quantile(scores, quantile_grid))
    thresholds = np.unique(np.concatenate(([0.0], thresholds, [1.0])))
    best_threshold = 0.5
    best_snapshot: dict[str, float] | None = None

    for threshold in thresholds:
        predictions = (scores >= threshold).astype(int)
        fpr = false_positive_rate(y_true, predictions)
        precision = precision_score(y_true, predictions, zero_division=0)
        recall = recall_score(y_true, predictions, zero_division=0)
        f1 = f1_score(y_true, predictions, zero_division=0)
        snapshot = {
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "fpr": float(fpr),
        }
        if fpr <= max_fpr:
            if best_snapshot is None or recall > best_snapshot["recall"] or (
                recall == best_snapshot["recall"] and precision > best_snapshot["precision"]
            ):
                best_threshold = float(threshold)
                best_snapshot = snapshot

    if best_snapshot is None:
        scores_table = []
        for threshold in thresholds:
            predictions = (scores >= threshold).astype(int)
            scores_table.append((f1_score(y_true, predictions, zero_division=0), float(threshold)))
        _, best_threshold = max(scores_table, key=lambda item: item[0])
        predictions = (scores >= best_threshold).astype(int)
        best_snapshot = {
            "precision": float(precision_score(y_true, predictions, zero_division=0)),
            "recall": float(recall_score(y_true, predictions, zero_division=0)),
            "f1": float(f1_score(y_true, predictions, zero_division=0)),
            "fpr": float(false_positive_rate(y_true, predictions)),
        }

    return best_threshold, best_snapshot


def compute_metrics(
    y_true: np.ndarray,
    scores: np.ndarray,
    threshold: float,
    max_fpr: float = 0.01,
) -> dict[str, float]:
    predictions = (scores >= threshold).astype(int)
    precision, recall, _ = precision_recall_curve(y_true, scores)
    pr_auc = auc(recall, precision)
    return {
        "threshold": float(threshold),
        "pr_auc": float(pr_auc),
        "average_precision": float(average_precision_score(y_true, scores)),
        "roc_auc": float(roc_auc_score(y_true, scores)),
        "precision": float(precision_score(y_true, predictions, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, zero_division=0)),
        "f1": float(f1_score(y_true, predictions, zero_division=0)),
        "fpr": float(false_positive_rate(y_true, predictions)),
        "recall_at_fixed_fpr": float(recall_at_fixed_fpr(y_true, scores, max_fpr=max_fpr)),
    }


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def save_experiment_results(results: list[dict[str, Any]], output_path: Path) -> pd.DataFrame:
    frame = pd.DataFrame(results).sort_values(["pr_auc", "recall_at_fixed_fpr"], ascending=False)
    frame.to_csv(output_path, index=False, encoding="utf-8-sig")
    return frame


def plot_curves(y_true: np.ndarray, scores: np.ndarray, figures_dir: Path, prefix: str) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)

    precision, recall, _ = precision_recall_curve(y_true, scores)
    plt.figure(figsize=(6, 4))
    plt.plot(recall, precision, label="PR curve")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / f"{prefix}_pr_curve.png", dpi=200)
    plt.close()

    fpr, tpr, _ = roc_curve(y_true, scores)
    plt.figure(figsize=(6, 4))
    plt.plot(fpr, tpr, label="ROC curve")
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / f"{prefix}_roc_curve.png", dpi=200)
    plt.close()


def plot_threshold_tradeoff(y_true: np.ndarray, scores: np.ndarray, figures_dir: Path, prefix: str) -> None:
    thresholds = np.unique(np.quantile(scores, np.linspace(0.0, 1.0, 257)))
    thresholds = np.unique(np.concatenate(([0.0], thresholds, [1.0])))
    rows = []
    for threshold in thresholds[:: max(1, len(thresholds) // 200)]:
        predictions = (scores >= threshold).astype(int)
        rows.append(
            {
                "threshold": threshold,
                "recall": recall_score(y_true, predictions, zero_division=0),
                "precision": precision_score(y_true, predictions, zero_division=0),
                "fpr": false_positive_rate(y_true, predictions),
            }
        )
    tradeoff = pd.DataFrame(rows)
    plt.figure(figsize=(7, 4))
    plt.plot(tradeoff["threshold"], tradeoff["recall"], label="Recall")
    plt.plot(tradeoff["threshold"], tradeoff["precision"], label="Precision")
    plt.plot(tradeoff["threshold"], tradeoff["fpr"], label="FPR")
    plt.xlabel("Threshold")
    plt.ylabel("Metric")
    plt.title("Threshold Trade-off")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / f"{prefix}_threshold_tradeoff.png", dpi=200)
    plt.close()


def plot_confusion_matrix(
    y_true: np.ndarray,
    scores: np.ndarray,
    threshold: float,
    figures_dir: Path,
    prefix: str,
) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    predictions = (scores >= threshold).astype(int)
    matrix = confusion_matrix(y_true, predictions, labels=[0, 1])
    plt.figure(figsize=(4.5, 4))
    plt.imshow(matrix, cmap="Blues")
    plt.title("Confusion Matrix")
    plt.colorbar()
    ticks = [0, 1]
    labels = ["Normal", "Fraud"]
    plt.xticks(ticks, labels)
    plt.yticks(ticks, labels)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    for row_idx in range(matrix.shape[0]):
        for col_idx in range(matrix.shape[1]):
            plt.text(col_idx, row_idx, str(matrix[row_idx, col_idx]), ha="center", va="center", color="black")
    plt.tight_layout()
    plt.savefig(figures_dir / f"{prefix}_confusion_matrix.png", dpi=200)
    plt.close()
