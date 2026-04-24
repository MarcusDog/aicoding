from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.pipeline.io_utils import raw_dir, read_csv, write_csv


LABEL_COLUMNS = [
    "point_id",
    "point_name",
    "source",
    "score",
    "complaint_risk",
    "activity_proxy",
    "label",
    "label_source",
    "label_notes",
    "labeled_by",
    "labeled_at",
]


def manual_labels_path() -> Path:
    return raw_dir() / "manual_labels.csv"


def empty_manual_labels() -> pd.DataFrame:
    return pd.DataFrame(columns=LABEL_COLUMNS)


def read_manual_labels(path: Path | None = None) -> pd.DataFrame:
    target = path or manual_labels_path()
    if not target.exists():
        return empty_manual_labels()

    labels = read_csv(target).copy()
    for col in LABEL_COLUMNS:
        if col not in labels.columns:
            labels[col] = pd.NA

    labels["point_id"] = labels["point_id"].fillna("").astype(str).str.strip()
    labels["point_name"] = labels["point_name"].fillna("").astype(str).str.strip()
    labels["source"] = labels["source"].fillna("").astype(str).str.strip()
    labels["label_source"] = labels["label_source"].fillna("").astype(str).str.strip()
    labels["label_notes"] = labels["label_notes"].fillna("").astype(str).str.strip()
    labels["labeled_by"] = labels["labeled_by"].fillna("").astype(str).str.strip()
    labels["labeled_at"] = pd.to_datetime(labels["labeled_at"], errors="coerce")
    labels["label"] = pd.to_numeric(labels["label"], errors="coerce")
    labels = labels[labels["label"].isin([0, 1]) | labels["label"].isna()].copy()
    return labels[LABEL_COLUMNS].copy()


def _base_label_frame(
    candidates: pd.DataFrame,
    features: pd.DataFrame | None = None,
    predictions: pd.DataFrame | None = None,
) -> pd.DataFrame:
    base_columns = [col for col in ["point_id", "point_name", "source"] if col in candidates.columns]
    base = candidates[base_columns].drop_duplicates(subset=["point_id"]).copy()

    if features is not None and not features.empty:
        feature_cols = [col for col in ["point_id", "complaint_risk", "activity_proxy"] if col in features.columns]
        feature_view = features[feature_cols].drop_duplicates(subset=["point_id"]).copy()
        base = base.merge(feature_view, on="point_id", how="left")
    else:
        base["complaint_risk"] = pd.NA
        base["activity_proxy"] = pd.NA

    if predictions is not None and not predictions.empty:
        score_cols = [col for col in ["point_id", "score"] if col in predictions.columns]
        score_view = predictions[score_cols].drop_duplicates(subset=["point_id"]).copy()
        base = base.merge(score_view, on="point_id", how="left")
    else:
        base["score"] = pd.NA

    for col in ["label", "label_source", "label_notes", "labeled_by", "labeled_at"]:
        if col not in base.columns:
            base[col] = pd.NA
    return base


def build_label_template(
    candidates: pd.DataFrame,
    features: pd.DataFrame | None = None,
    predictions: pd.DataFrame | None = None,
    existing_labels: pd.DataFrame | None = None,
) -> pd.DataFrame:
    template = _base_label_frame(candidates, features, predictions)
    existing = existing_labels if existing_labels is not None else empty_manual_labels()
    if not existing.empty:
        existing = existing.copy()
        existing["point_id"] = existing["point_id"].fillna("").astype(str).str.strip()
        existing["labeled_at"] = pd.to_datetime(existing["labeled_at"], errors="coerce")
        existing = existing.sort_values("labeled_at", ascending=False)
        existing = existing.drop_duplicates(subset=["point_id"], keep="first")
        template = template.drop(columns=[col for col in ["label", "label_source", "label_notes", "labeled_by", "labeled_at"] if col in template.columns])
        template = template.merge(
            existing[["point_id", "label", "label_source", "label_notes", "labeled_by", "labeled_at"]],
            on="point_id",
            how="left",
        )

    for col in LABEL_COLUMNS:
        if col not in template.columns:
            template[col] = pd.NA
    return template[LABEL_COLUMNS].copy()


def save_manual_labels(labels: pd.DataFrame, path: Path | None = None) -> Path:
    target = path or manual_labels_path()
    out = labels.copy()
    for col in LABEL_COLUMNS:
        if col not in out.columns:
            out[col] = pd.NA
    out["label"] = pd.to_numeric(out["label"], errors="coerce")
    out = out[out["label"].isin([0, 1])].copy()
    out["label_source"] = out["label_source"].fillna("manual").astype(str).str.strip()
    out["label_notes"] = out["label_notes"].fillna("").astype(str).str.strip()
    out["labeled_by"] = out["labeled_by"].fillna("").astype(str).str.strip()
    out["labeled_at"] = out["labeled_at"].fillna(datetime.now().isoformat()).astype(str)
    write_csv(out[LABEL_COLUMNS], target)
    return target


def merge_manual_labels(features: pd.DataFrame, manual_labels: pd.DataFrame) -> pd.DataFrame:
    out = features.copy()
    valid_labels = manual_labels.copy()
    valid_labels["label"] = pd.to_numeric(valid_labels["label"], errors="coerce")
    valid_labels = valid_labels[valid_labels["label"].isin([0, 1])].copy()

    if valid_labels.empty:
        if "label" not in out.columns:
            out["label"] = pd.NA
        if "label_source" not in out.columns:
            out["label_source"] = pd.NA
        if "label_notes" not in out.columns:
            out["label_notes"] = pd.NA
        if "labeled_by" not in out.columns:
            out["labeled_by"] = pd.NA
        if "labeled_at" not in out.columns:
            out["labeled_at"] = pd.NaT
        return out

    labels = valid_labels.copy()
    labels["point_id"] = labels["point_id"].fillna("").astype(str).str.strip()
    labels["point_name"] = labels["point_name"].fillna("").astype(str).str.strip()
    labels["labeled_at"] = pd.to_datetime(labels["labeled_at"], errors="coerce")
    labels = labels.sort_values("labeled_at", ascending=False)

    for col in ["label", "label_source", "label_notes", "labeled_by", "labeled_at"]:
        if col in out.columns:
            out = out.drop(columns=col)

    merged = out.merge(
        labels[["point_id", "label", "label_source", "label_notes", "labeled_by", "labeled_at"]].drop_duplicates(subset=["point_id"]),
        on="point_id",
        how="left",
    )

    missing = merged["label"].isna()
    if missing.any() and "point_name" in merged.columns:
        by_name = (
            labels[labels["point_name"].ne("")]
            [["point_name", "label", "label_source", "label_notes", "labeled_by", "labeled_at"]]
            .drop_duplicates(subset=["point_name"])
            .rename(columns={col: f"{col}_by_name" for col in ["label", "label_source", "label_notes", "labeled_by", "labeled_at"]})
        )
        merged = merged.merge(by_name, on="point_name", how="left")
        for col in ["label", "label_source", "label_notes", "labeled_by", "labeled_at"]:
            merged[col] = merged[col].where(merged[col].notna(), merged.get(f"{col}_by_name"))
        merged = merged.drop(columns=[col for col in merged.columns if col.endswith("_by_name")])

    merged["label"] = pd.to_numeric(merged["label"], errors="coerce")
    return merged


def label_summary(manual_labels: pd.DataFrame) -> dict[str, int]:
    labels = manual_labels.copy()
    labels["label"] = pd.to_numeric(labels["label"], errors="coerce")
    valid = labels[labels["label"].isin([0, 1])]
    return {
        "labeled_rows": int(len(valid)),
        "positive_labels": int((valid["label"] == 1).sum()),
        "negative_labels": int((valid["label"] == 0).sum()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage manual labels for candidate points.")
    parser.add_argument("--candidates", type=Path, default=raw_dir() / "candidate_points.csv")
    parser.add_argument("--features", type=Path, default=Path("data/processed/features.csv"))
    parser.add_argument("--predictions", type=Path, default=Path("data/processed/predictions.csv"))
    parser.add_argument("--output", type=Path, default=manual_labels_path())
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = read_csv(args.candidates)
    features = read_csv(args.features) if args.features.exists() else pd.DataFrame()
    predictions = read_csv(args.predictions) if args.predictions.exists() else pd.DataFrame()
    existing = read_manual_labels(args.output)
    template = build_label_template(candidates, features, predictions, existing)
    if not args.output.exists():
        write_csv(template, args.output)
        print(f"created_label_template={args.output}")
    else:
        print(f"label_file_exists={args.output}")
        print(label_summary(existing))


if __name__ == "__main__":
    main()
