from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
ARTIFACTS = ROOT / "artifacts"
FIGURE_DIR = ROOT / "evidence" / "figures"
CAPTION_PATH = ROOT / "thesis" / "figure-captions.md"


def _configure_matplotlib() -> None:
    matplotlib.use("Agg")
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _save_current(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def _barh(df: pd.DataFrame, label_col: str, value_col: str, title: str, xlabel: str, path: Path, color: str) -> None:
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df[label_col].astype(str), pd.to_numeric(df[value_col], errors="coerce"), color=color, alpha=0.9)
    ax.set_title(title, fontsize=15, pad=14)
    ax.set_xlabel(xlabel)
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    ax.invert_yaxis()
    _save_current(fig, path)


def export_category_distribution(complaints: pd.DataFrame) -> Path | None:
    if complaints.empty or "category" not in complaints.columns:
        return None
    counts = (
        complaints["category"].astype(str).value_counts().head(10).rename_axis("category").reset_index(name="count")
    )
    output = FIGURE_DIR / "figure-01-complaint-category-distribution.png"
    _barh(counts, "category", "count", "杨浦区投诉替代集类别分布", "投诉数量", output, "#c2410c")
    return output


def export_hotspot_chart(hotspots: pd.DataFrame) -> Path | None:
    if hotspots.empty:
        return None
    ranked = hotspots.sort_values("complaint_count", ascending=False).head(10).copy()
    output = FIGURE_DIR / "figure-02-hotspot-top10.png"
    _barh(ranked, "grid_id", "complaint_count", "投诉热点网格 Top10", "投诉数量", output, "#0f766e")
    return output


def export_recommendation_chart(predictions: pd.DataFrame) -> Path | None:
    if predictions.empty:
        return None
    ranked = predictions.sort_values("score", ascending=False).head(10).copy()
    ranked["label"] = ranked["point_name"].astype(str) + " (" + ranked["source"].astype(str) + ")"
    output = FIGURE_DIR / "figure-03-recommendation-top10.png"
    _barh(ranked, "label", "score", "候选点综合推荐得分 Top10", "综合得分", output, "#1d4ed8")
    return output


def export_component_chart(predictions: pd.DataFrame) -> Path | None:
    if predictions.empty:
        return None
    top3 = predictions.sort_values("score", ascending=False).head(3).copy()
    component_columns = [
        ("activity_component", "活动活跃"),
        ("flow_component", "流量代理"),
        ("temporal_component", "时段机会"),
        ("stability_component", "天气稳定"),
        ("low_complaint_component", "低投诉压力"),
        ("street_friendly_component", "道路友好"),
    ]
    rows: list[dict[str, object]] = []
    for _, row in top3.iterrows():
        for column, label in component_columns:
            value = pd.to_numeric(row.get(column, 0.0), errors="coerce")
            rows.append(
                {
                    "point_name": str(row.get("point_name", "")),
                    "component": label,
                    "value": 0.0 if pd.isna(value) else float(value),
                }
            )
    chart = pd.DataFrame(rows)
    if chart.empty:
        return None
    pivot = chart.pivot(index="component", columns="point_name", values="value").fillna(0.0)
    output = FIGURE_DIR / "figure-04-score-components-top3.png"
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot.plot(kind="bar", ax=ax, width=0.78)
    ax.set_title("Top3 候选点得分构成对比", fontsize=15, pad=14)
    ax.set_xlabel("评分组件")
    ax.set_ylabel("组件分值")
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    ax.legend(title="点位")
    _save_current(fig, output)
    return output


def export_label_summary(predictions: pd.DataFrame, metrics: dict[str, object]) -> Path | None:
    labeled_rows = int(metrics.get("labeled_rows", 0) or 0)
    positive = int(metrics.get("positive_labels", 0) or 0)
    negative = int(metrics.get("negative_labels", 0) or 0)
    unlabeled = max(int(len(predictions)) - positive - negative, 0)
    if labeled_rows <= 0 and unlabeled <= 0:
        return None

    output = FIGURE_DIR / "figure-05-label-summary.png"
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    labels = ["适宜", "不适宜", "未标注"]
    values = [positive, negative, unlabeled]
    colors = ["#0f766e", "#b91c1c", "#94a3b8"]
    ax.pie(values, labels=labels, autopct="%1.0f", startangle=90, colors=colors, wedgeprops={"linewidth": 1, "edgecolor": "white"})
    ax.set_title("人工标注样本覆盖情况", fontsize=15, pad=14)
    _save_current(fig, output)
    return output


def write_captions(paths: list[Path], metrics: dict[str, object]) -> None:
    lines = [
        "# 论文配图说明",
        "",
        "以下图片由 `scripts/export_thesis_assets.py` 自动生成，可直接用于论文或答辩材料。",
        "",
    ]
    captions = {
        "figure-01-complaint-category-distribution.png": "图 1 投诉替代集类别分布，用于说明当前公开治理数据的主要问题类型。",
        "figure-02-hotspot-top10.png": "图 2 投诉热点网格 Top10，用于展示投诉在杨浦区范围内的空间聚集特征。",
        "figure-03-recommendation-top10.png": "图 3 候选点综合推荐得分 Top10，用于展示系统排序结果。",
        "figure-04-score-components-top3.png": "图 4 Top3 候选点得分构成对比，用于解释规则评分的组成部分。",
        "figure-05-label-summary.png": "图 5 人工标注样本覆盖情况，用于说明模型监督样本的当前规模。",
    }
    for path in paths:
        lines.append(f"- `{path.name}`: {captions.get(path.name, '自动导出的论文配图。')}")
    lines.extend(
        [
            "",
            "## 当前模型状态",
            "",
            f"- 模型来源: `{metrics.get('model_source', 'unknown')}`",
            f"- 有效标注数: `{metrics.get('labeled_rows', 0)}`",
            f"- 准确率: `{metrics.get('accuracy')}`",
            f"- F1: `{metrics.get('f1')}`",
            "",
        ]
    )
    CAPTION_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    _configure_matplotlib()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    complaints = _read_csv(PROCESSED / "complaints_cleaned.csv")
    hotspots = _read_csv(PROCESSED / "hotspots.csv")
    predictions = _read_csv(PROCESSED / "predictions.csv")
    metrics_path = ARTIFACTS / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}

    outputs = [
        export_category_distribution(complaints),
        export_hotspot_chart(hotspots),
        export_recommendation_chart(predictions),
        export_component_chart(predictions),
        export_label_summary(predictions, metrics),
    ]
    written = [path for path in outputs if path is not None]
    write_captions(written, metrics)
    print(f"generated_figures={len(written)}")
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
