import pandas as pd

from fraud_detection.site_presenter import build_dashboard_frame, build_case_frame, build_dashboard_summary


def test_build_dashboard_frame_normalizes_stream_scores_to_display_levels():
    stream_frame = pd.DataFrame(
        [
            {"transaction_id": "txn-1", "fraud_score": 1.0e-8, "reason": "['V1 deviation=1.0']"},
            {"transaction_id": "txn-2", "fraud_score": 8.0e-8, "reason": "['V2 deviation=1.2']"},
            {"transaction_id": "txn-3", "fraud_score": 3.0e-4, "reason": "['V3 deviation=1.6']"},
        ]
    )
    prediction_frame = pd.DataFrame(
        {
            "fraud_score": [1.0e-8, 2.0e-8, 4.0e-8, 8.0e-8, 1.0e-4, 1.0e-2],
            "predicted_class": [0, 0, 0, 0, 1, 1],
            "Class": [0, 0, 0, 0, 1, 1],
        }
    )

    frame = build_dashboard_frame(stream_frame, prediction_frame)

    assert "risk_index" in frame.columns
    assert "display_risk_level" in frame.columns
    assert set(frame["display_risk_level"]) == {"low", "medium", "high"}


def test_build_case_frame_includes_source_and_top_risk_examples():
    stream_frame = pd.DataFrame(
        [
            {"transaction_id": "txn-1", "fraud_score": 1.0e-8, "reason": "['V1 deviation=1.0']"},
            {"transaction_id": "txn-2", "fraud_score": 8.0e-8, "reason": "['V2 deviation=1.2']"},
        ]
    )
    prediction_frame = pd.DataFrame(
        {
            "fraud_score": [1.0e-8, 2.0e-8, 1.0, 0.9],
            "predicted_class": [0, 0, 1, 1],
            "Class": [0, 0, 1, 0],
            "V1": [0.1, 0.2, 4.1, 3.8],
            "V2": [0.1, 0.2, 5.1, 4.8],
        }
    )
    bundle = {
        "feature_columns": ["V1", "V2"],
        "feature_summary": {
            "V1": {"median": 0.0, "iqr": 1.0},
            "V2": {"median": 0.0, "iqr": 1.0},
        },
    }

    frame = build_case_frame(stream_frame, prediction_frame, bundle, limit=4)

    assert "source" in frame.columns
    assert "reason_display" in frame.columns
    assert frame.iloc[0]["source"] == "离线测试"
    assert frame["risk_index"].max() == 100.0


def test_build_dashboard_summary_uses_risk_index_average():
    frame = pd.DataFrame(
        {
            "risk_index": [20.0, 55.0, 93.0],
            "display_risk_level": ["low", "medium", "high"],
        }
    )

    summary = build_dashboard_summary(frame, batch_id=4)

    assert summary["batch_id"] == 4
    assert summary["event_count"] == 3
    assert summary["high_risk_count"] == 1
    assert summary["average_risk_index"] == 56.0
