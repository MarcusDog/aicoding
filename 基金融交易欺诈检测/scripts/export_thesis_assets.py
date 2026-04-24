from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from matplotlib import font_manager


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fraud_detection.settings import FIGURES_DIR, METRICS_DIR, REPORTS_DIR, SCREENSHOTS_DIR, ensure_directories  # noqa: E402


def configure_fonts() -> None:
    available = {font.name for font in font_manager.fontManager.ttflist}
    for candidate in ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial Unicode MS"]:
        if candidate in available:
            plt.rcParams["font.family"] = candidate
            break
    plt.rcParams["axes.unicode_minus"] = False


def add_box(ax, xy, width, height, text, color):
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.5,
        edgecolor="#1f2937",
        facecolor=color,
    )
    ax.add_patch(box)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=11)


def export_architecture_figure() -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    add_box(ax, (0.6, 2.4), 1.8, 1.0, "真实交易数据", "#dbeafe")
    add_box(ax, (3.0, 2.4), 1.8, 1.0, "离线训练与评估", "#dcfce7")
    add_box(ax, (5.4, 2.4), 1.8, 1.0, "模型服务", "#fef3c7")
    add_box(ax, (7.8, 2.4), 1.6, 1.0, "答辩看板", "#fee2e2")

    ax.annotate("", xy=(3.0, 2.9), xytext=(2.4, 2.9), arrowprops=dict(arrowstyle="->", lw=2))
    ax.annotate("", xy=(5.4, 2.9), xytext=(4.8, 2.9), arrowprops=dict(arrowstyle="->", lw=2))
    ax.annotate("", xy=(7.8, 2.9), xytext=(7.2, 2.9), arrowprops=dict(arrowstyle="->", lw=2))
    ax.text(5, 5.2, "图  系统总体架构图", ha="center", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "thesis_system_architecture.png", dpi=220)
    plt.close(fig)


def export_streaming_figure() -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis("off")

    labels = [
        ("交易回放脚本", (0.5, 2.5), "#dbeafe"),
        ("Kafka Topic", (2.6, 2.5), "#fde68a"),
        ("Spark Streaming", (4.8, 2.5), "#dcfce7"),
        ("模型微批打分", (7.0, 2.5), "#fecaca"),
        ("实时结果文件", (9.1, 2.5), "#e9d5ff"),
    ]
    for text, xy, color in labels:
        add_box(ax, xy, 1.5, 1.0, text, color)
    for x0, x1 in [(2.0, 2.6), (4.1, 4.8), (6.3, 7.0), (8.5, 9.1)]:
        ax.annotate("", xy=(x1, 3.0), xytext=(x0, 3.0), arrowprops=dict(arrowstyle="->", lw=2))
    ax.text(5.5, 5.2, "图  Kafka + Spark 准实时风险识别链路图", ha="center", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "thesis_streaming_architecture.png", dpi=220)
    plt.close(fig)


def export_model_comparison_figure() -> None:
    result_path = METRICS_DIR / "experiment_results.csv"
    if not result_path.exists():
        return
    frame = pd.read_csv(result_path)
    top = frame.sort_values("pr_auc", ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(top["name"], top["pr_auc"], color="#2563eb")
    ax.set_ylabel("PR-AUC")
    ax.set_title("图  不同模型方案的 PR-AUC 对比")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "thesis_model_comparison.png", dpi=220)
    plt.close(fig)


def export_manifest() -> None:
    ensure_directories()
    manifest_path = REPORTS_DIR / "thesis_figure_manifest.md"
    metrics = {}
    metrics_path = METRICS_DIR / "best_metrics.json"
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    screenshot_entries = [
        ("defense_overview.png", "答辩看板首页，适合放在“系统实现”章节。"),
        ("defense_offline_prediction.png", "离线预测页面，适合放在“功能实现”章节。"),
        ("defense_streaming_monitor.png", "准实时监控页面，适合放在“系统实现”或“运行效果”章节。"),
    ]

    lines = [
        "# 论文配图清单",
        "",
        "## 建议插图",
        f"- `thesis_system_architecture.png`：系统总体架构图，建议放在“系统设计”章节。",
        f"- `thesis_streaming_architecture.png`：准实时链路图，建议放在“系统实现”章节。",
        f"- `thesis_model_comparison.png`：模型方案对比图，建议放在“实验结果分析”章节。",
        f"- `best_model_pr_curve.png`：PR 曲线图，建议放在“实验结果分析”章节。",
        f"- `best_model_threshold_tradeoff.png`：阈值权衡图，建议放在“实验结果分析”章节。",
        f"- `best_model_confusion_matrix.png`：混淆矩阵图，建议放在“测试结果分析”章节。",
        "",
        "## 当前最佳模型指标",
        f"- 模型：{metrics.get('model_name', '-')}",
        f"- PR-AUC：{metrics.get('pr_auc', 0):.4f}",
        f"- Recall：{metrics.get('recall', 0):.4f}",
        f"- FPR：{metrics.get('fpr', 0):.4f}",
        "",
        "## 截图建议",
    ]
    for filename, description in screenshot_entries:
        screenshot_path = SCREENSHOTS_DIR / filename
        if screenshot_path.exists():
            lines.append(f"- `{filename}`：{description}")
        else:
            lines.append(f"- `{filename}`：尚未生成，可运行 `scripts/capture_dashboard_screenshots.py` 补齐。")
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_directories()
    configure_fonts()
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    export_architecture_figure()
    export_streaming_figure()
    export_model_comparison_figure()
    export_manifest()
    print(f"Exported thesis assets to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
