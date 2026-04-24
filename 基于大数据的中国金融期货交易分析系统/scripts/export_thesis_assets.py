from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from warehouse.storage import WarehouseStore


ASSET_DIR = ROOT / "artifacts" / "thesis"
FIGURE_DIR = ASSET_DIR / "figures"
DIAGRAM_DIR = ASSET_DIR / "diagrams"


def ensure_dirs() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)


def save_comparison_chart(store: WarehouseStore) -> str:
    df = store.read_table("comparison_frame")
    fig, ax = plt.subplots(figsize=(11, 6))
    for product_id, group in df.groupby("product_id"):
        group = group.sort_values("trading_date")
        ax.plot(pd.to_datetime(group["trading_date"]), group["normalized_close"], label=product_id, linewidth=2.2)
    ax.set_title("图 6-1 四类股指期货主力连续归一化走势", fontsize=14)
    ax.set_ylabel("归一化价格指数")
    ax.set_xlabel("交易日期")
    ax.grid(alpha=0.25)
    ax.legend()
    path = FIGURE_DIR / "fig_6_1_product_comparison.png"
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return str(path)


def save_if_trend_chart(store: WarehouseStore) -> str:
    df = store.read_table("main_contract_daily")
    df = df[df["product_id"] == "IF"].sort_values("trading_date")
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(pd.to_datetime(df["trading_date"]), df["close_price"], label="IF主力收盘价", linewidth=2.2)
    ax.plot(pd.to_datetime(df["trading_date"]), df["rolling_ma_20"], label="20日均线", linewidth=1.8, linestyle="--")
    ax.set_title("图 6-2 IF 主力连续收盘价与20日均线", fontsize=14)
    ax.set_xlabel("交易日期")
    ax.set_ylabel("价格")
    ax.grid(alpha=0.25)
    ax.legend()
    path = FIGURE_DIR / "fig_6_2_if_trend_ma20.png"
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return str(path)


def save_if_drawdown_vol_chart(store: WarehouseStore) -> str:
    df = store.read_table("main_contract_daily")
    df = df[df["product_id"] == "IF"].sort_values("trading_date")
    dates = pd.to_datetime(df["trading_date"])
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    axes[0].fill_between(dates, df["drawdown"].fillna(0), color="#9b2c2c", alpha=0.4)
    axes[0].plot(dates, df["drawdown"].fillna(0), color="#9b2c2c", linewidth=1.8)
    axes[0].set_title("图 6-3 IF 主力连续回撤曲线", fontsize=13)
    axes[0].set_ylabel("回撤")
    axes[0].grid(alpha=0.2)

    axes[1].plot(dates, df["rolling_vol_20"], color="#b8842f", linewidth=2)
    axes[1].set_title("图 6-4 IF 20日滚动年化波动率", fontsize=13)
    axes[1].set_xlabel("交易日期")
    axes[1].set_ylabel("年化波动率")
    axes[1].grid(alpha=0.2)
    path = FIGURE_DIR / "fig_6_3_if_drawdown_volatility.png"
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return str(path)


def save_var_chart(store: WarehouseStore) -> str:
    df = store.read_table("analysis_snapshot").sort_values("product_id")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(df["product_id"], df["var_95_hist_60"] * 100, color=["#7d3d1f", "#9b2c2c", "#b8842f", "#1d2a33"])
    ax.set_title("图 6-5 各股指期货60日历史模拟VaR", fontsize=14)
    ax.set_ylabel("VaR (%)")
    for idx, value in enumerate(df["var_95_hist_60"] * 100):
        ax.text(idx, value + 0.05, f"{value:.2f}", ha="center", va="bottom", fontsize=10)
    path = FIGURE_DIR / "fig_6_4_var_bar.png"
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return str(path)


def save_correlation_heatmap(store: WarehouseStore) -> str:
    corr = store.read_table("correlation_matrix").set_index("series")
    labels = list(corr.columns)
    data = corr.values.astype(float)
    fig, ax = plt.subplots(figsize=(9, 7))
    im = ax.imshow(data, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(corr.index.tolist())
    ax.set_title("图 6-6 股指期货与宏观指标月度相关性矩阵", fontsize=14)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            value = data[i, j]
            if math.isnan(value):
                continue
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=8, color="black")
    fig.colorbar(im, ax=ax, shrink=0.8)
    path = FIGURE_DIR / "fig_6_5_correlation_heatmap.png"
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return str(path)


def save_quality_chart(store: WarehouseStore) -> str:
    df = store.read_table("quality_report").sort_values("dataset_name")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    axes[0].bar(df["dataset_name"], df["row_count"], color=["#1d2a33", "#b8842f", "#9b2c2c"])
    axes[0].set_title("图 6-7 数据集记录量")
    axes[0].tick_params(axis="x", rotation=20)
    axes[1].bar(df["dataset_name"], df["success_rate"] * 100, color=["#1d2a33", "#b8842f", "#9b2c2c"])
    axes[1].set_title("图 6-8 数据抓取成功率")
    axes[1].set_ylim(0, 105)
    axes[1].tick_params(axis="x", rotation=20)
    path = FIGURE_DIR / "fig_6_6_quality_overview.png"
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return str(path)


def rect(x: int, y: int, width: int, height: int, text: str) -> str:
    lines = text.split("\n")
    text_svg = []
    for idx, line_text in enumerate(lines):
        text_svg.append(
            f'<text x="{x + width / 2}" y="{y + 28 + idx * 20}" text-anchor="middle" font-size="16" fill="#1d2a33">{line_text}</text>'
        )
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="16" fill="#fffaf3" stroke="#b8842f" stroke-width="2"/>{"".join(text_svg)}'


def line(x1: int, y1: int, x2: int, y2: int) -> str:
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#7d3d1f" stroke-width="3" marker-end="url(#arrow)"/>'


def base_svg(title: str, shapes: list[str], connectors: list[str]) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="380" viewBox="0 0 1080 380">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#7d3d1f"/>
  </marker>
</defs>
<rect width="1080" height="380" fill="#f8f4ed"/>
<text x="540" y="36" text-anchor="middle" font-size="24" fill="#1d2a33" font-weight="bold">{title}</text>
{''.join(connectors)}
{''.join(shapes)}
</svg>"""


def write_svg_diagrams() -> list[str]:
    diagrams = {
        "fig_4_1_system_architecture.svg": base_svg(
            "系统总体架构图",
            [
                rect(40, 70, 150, 70, "CFFEX\n日统计"),
                rect(40, 190, 150, 70, "PBC / NBS\n宏观数据"),
                rect(260, 130, 170, 90, "数据采集层\ningest"),
                rect(500, 130, 170, 90, "数据存储层\nDuckDB / Parquet"),
                rect(740, 70, 170, 70, "分析服务层\nFastAPI"),
                rect(740, 190, 170, 70, "展示层\nStreamlit"),
            ],
            [
                line(190, 105, 260, 160),
                line(190, 225, 260, 190),
                line(430, 175, 500, 175),
                line(670, 160, 740, 105),
                line(670, 190, 740, 225),
            ],
        ),
        "fig_4_2_data_flow.svg": base_svg(
            "数据处理流程图",
            [
                rect(40, 130, 150, 60, "原始网页/XML"),
                rect(240, 130, 150, 60, "标准化清洗"),
                rect(440, 130, 150, 60, "主力连续构建"),
                rect(640, 70, 160, 60, "趋势/波动率"),
                rect(640, 190, 160, 60, "相关性/VaR"),
                rect(850, 130, 150, 60, "页面与论文配图"),
            ],
            [
                line(190, 160, 240, 160),
                line(390, 160, 440, 160),
                line(590, 160, 640, 100),
                line(590, 160, 640, 220),
                line(800, 100, 850, 160),
                line(800, 220, 850, 160),
            ],
        ),
        "fig_3_1_data_model.svg": base_svg(
            "核心数据模型图",
            [
                rect(50, 70, 180, 90, "contracts\ninstrument_id\nproduct_id\ncontract_month"),
                rect(50, 220, 180, 110, "futures_daily\ntrading_date\nopen/high/low/close\nvolume/open_interest"),
                rect(320, 220, 180, 110, "main_contract_daily\ndaily_return\nrolling_vol_20\ndrawdown"),
                rect(590, 220, 180, 110, "macro_series\nseries_name\nobservation_date\nvalue"),
                rect(860, 220, 180, 110, "analysis_snapshot\nVaR\ntrend_signal\nrisk_level"),
            ],
            [
                line(140, 160, 140, 220),
                line(230, 275, 320, 275),
                line(500, 275, 590, 275),
                line(770, 275, 860, 275),
            ],
        ),
    }
    paths = []
    for filename, content in diagrams.items():
        path = DIAGRAM_DIR / filename
        path.write_text(content, encoding="utf-8")
        paths.append(str(path))
    return paths


def write_figure_index() -> str:
    path = ASSET_DIR / "thesis_figure_index.md"
    entries = [
        ("图 3-1", "核心数据模型图", "数据库设计章节", "artifacts/thesis/diagrams/fig_3_1_data_model.svg"),
        ("图 4-1", "系统总体架构图", "系统架构设计章节", "artifacts/thesis/diagrams/fig_4_1_system_architecture.svg"),
        ("图 4-2", "数据处理流程图", "系统架构设计章节", "artifacts/thesis/diagrams/fig_4_2_data_flow.svg"),
        ("图 6-1", "四类股指期货主力连续归一化走势", "测试结果分析章节", "artifacts/thesis/figures/fig_6_1_product_comparison.png"),
        ("图 6-2", "IF 主力连续收盘价与20日均线", "趋势分析章节", "artifacts/thesis/figures/fig_6_2_if_trend_ma20.png"),
        ("图 6-3", "IF 主力连续回撤曲线与波动率", "风险分析章节", "artifacts/thesis/figures/fig_6_3_if_drawdown_volatility.png"),
        ("图 6-4", "各股指期货60日历史模拟VaR", "风险分析章节", "artifacts/thesis/figures/fig_6_4_var_bar.png"),
        ("图 6-5", "股指期货与宏观指标月度相关性矩阵", "相关性分析章节", "artifacts/thesis/figures/fig_6_5_correlation_heatmap.png"),
        ("图 6-6", "数据量与抓取成功率统计图", "数据质量与测试章节", "artifacts/thesis/figures/fig_6_6_quality_overview.png"),
    ]
    lines = ["# 论文配图索引", "", "| 编号 | 名称 | 建议章节 | 文件 |", "| --- | --- | --- | --- |"]
    for no, name, chapter, rel in entries:
        lines.append(f"| {no} | {name} | {chapter} | `{rel}` |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


def main() -> None:
    ensure_dirs()
    store = WarehouseStore()
    paths = [
        save_comparison_chart(store),
        save_if_trend_chart(store),
        save_if_drawdown_vol_chart(store),
        save_var_chart(store),
        save_correlation_heatmap(store),
        save_quality_chart(store),
    ]
    paths.extend(write_svg_diagrams())
    index_path = write_figure_index()
    for asset in paths:
        print(asset)
    print(index_path)


if __name__ == "__main__":
    main()
