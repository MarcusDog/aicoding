import numpy as np

from fraud_detection.evaluation import compute_metrics, optimize_threshold


def test_optimize_threshold_returns_valid_metrics():
    y_true = np.array([0, 0, 0, 1, 1])
    scores = np.array([0.1, 0.2, 0.4, 0.8, 0.9])
    threshold, snapshot = optimize_threshold(y_true, scores, max_fpr=0.5)
    metrics = compute_metrics(y_true, scores, threshold)
    assert 0.0 <= threshold <= 1.0
    assert snapshot["recall"] >= 0.0
    assert metrics["pr_auc"] >= 0.0
