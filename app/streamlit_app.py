from __future__ import annotations

from urllib.parse import urlencode

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analysis.service import AnalysisService


PAGES = [
    ("home", "产品首页"),
    ("overview", "市场总览"),
    ("market", "合约行情"),
    ("trend", "趋势与波动"),
    ("risk", "相关性与风险"),
    ("sources", "数据来源"),
]
PAGE_SLUG_TO_LABEL = {slug: label for slug, label in PAGES}

st.set_page_config(page_title="中国股指期货盘后分析系统", layout="wide")
service = AnalysisService()


def query_value(name: str, default: str = "") -> str:
    value = st.query_params.get(name, default)
    if isinstance(value, list):
        return value[0] if value else default
    return value or default


def build_href(page: str, product: str = "IF", compare: str = "IF,IH,IC,IM", mode: str = "") -> str:
    params = {"page": page, "product": product, "compare": compare}
    if mode:
        params["mode"] = mode
    return f"?{urlencode(params)}"


def pct(value: object, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "--"
    return f"{float(value) * 100:.{digits}f}%"


def num(value: object, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "--"
    return f"{float(value):,.{digits}f}"


def inject_styles(thesis_mode: bool) -> None:
    extra = ""
    if thesis_mode:
        extra = """
        header[data-testid="stHeader"] { display: none; }
        .block-container { padding-top: 1.2rem; }
        """

    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            display: none;
        }}
        [data-testid="collapsedControl"] {{
            display: none;
        }}
        :root {{
            --ink: #16212b;
            --muted: #5f6e79;
            --line: rgba(22,33,43,0.08);
            --accent: #ba8736;
            --panel: rgba(255,251,246,0.94);
            --deep: #17232c;
            --deep-2: #2f3f4b;
        }}
        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(186,135,54,0.16), transparent 24%),
                radial-gradient(circle at right top, rgba(23,35,44,0.07), transparent 18%),
                linear-gradient(180deg, #f7f2ea 0%, #f1ebe1 100%);
        }}
        .block-container {{
            padding-top: 1.6rem;
            padding-bottom: 2rem;
        }}
        .topbar {{
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:18px;
            padding: 8px 0 20px 0;
        }}
        .brand {{
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 0.8px;
            color: var(--ink);
            text-transform: uppercase;
        }}
        .navlinks {{
            display:flex;
            gap:10px;
            flex-wrap:wrap;
        }}
        .navlinks a {{
            text-decoration:none;
            color: var(--muted);
            padding: 9px 14px;
            border-radius: 999px;
            border: 1px solid var(--line);
            background: rgba(255,255,255,0.55);
            font-size: 13px;
        }}
        .navlinks a.active {{
            color: white;
            background: var(--deep);
            border-color: var(--deep);
        }}
        .hero {{
            padding: 34px;
            border-radius: 28px;
            background: linear-gradient(135deg, rgba(23,35,44,0.98), rgba(82,54,33,0.95));
            color: white;
            box-shadow: 0 22px 52px rgba(23,35,44,0.18);
            margin-bottom: 22px;
        }}
        .eyebrow {{
            font-size: 12px;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            color: rgba(255,255,255,0.68);
            margin-bottom: 10px;
        }}
        .hero h1 {{
            margin: 0 0 12px 0;
            font-size: 40px;
            line-height: 1.15;
        }}
        .hero p {{
            margin: 0;
            font-size: 15px;
            line-height: 1.75;
            color: rgba(255,255,255,0.84);
            max-width: 680px;
        }}
        .cta-row {{
            display:flex;
            gap:12px;
            flex-wrap:wrap;
            margin-top:20px;
        }}
        .cta-row a {{
            text-decoration:none;
            padding: 12px 18px;
            border-radius: 999px;
            font-size: 14px;
            font-weight: 600;
        }}
        .cta-primary {{
            background: #f5ede1;
            color: var(--deep);
        }}
        .cta-secondary {{
            background: rgba(255,255,255,0.12);
            color: white;
            border: 1px solid rgba(255,255,255,0.18);
        }}
        .section-title {{
            font-size: 26px;
            color: var(--ink);
            margin: 10px 0 14px 0;
            font-weight: 800;
        }}
        .section-subtitle {{
            color: var(--muted);
            font-size: 14px;
            line-height: 1.7;
            margin-bottom: 14px;
        }}
        .panel {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 18px 20px;
            box-shadow: 0 10px 28px rgba(23,35,44,0.05);
        }}
        .metric-card {{
            background: rgba(255,255,255,0.62);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 18px;
            min-height: 128px;
            box-shadow: 0 10px 24px rgba(23,35,44,0.04);
        }}
        .metric-label {{
            color: var(--muted);
            font-size: 12px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 30px;
            font-weight: 800;
            color: var(--ink);
            margin: 10px 0 8px 0;
        }}
        .metric-meta {{
            color: #7a4624;
            font-size: 13px;
            line-height: 1.65;
        }}
        .cap-grid {{
            display:grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            margin-top: 8px;
            margin-bottom: 12px;
        }}
        .cap-card {{
            background: rgba(255,255,255,0.66);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 18px;
            min-height: 188px;
        }}
        .cap-kicker {{
            color: var(--accent);
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        .cap-card h3 {{
            margin: 0 0 10px 0;
            color: var(--ink);
            font-size: 19px;
        }}
        .cap-card p {{
            margin: 0;
            color: var(--muted);
            font-size: 14px;
            line-height: 1.7;
        }}
        .trust-list {{
            display:grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
        }}
        .trust-item {{
            background: rgba(255,255,255,0.66);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 16px;
        }}
        .trust-item h4 {{
            margin: 0 0 8px 0;
            color: var(--ink);
            font-size: 17px;
        }}
        .trust-item p {{
            margin: 0;
            color: var(--muted);
            font-size: 14px;
            line-height: 1.7;
        }}
        .footer-box {{
            margin-top: 20px;
            padding: 18px 22px;
            border-radius: 20px;
            background: rgba(23,35,44,0.96);
            color: rgba(255,255,255,0.86);
        }}
        .footer-box strong {{
            color: white;
        }}
        .module-grid {{
            display:grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-top: 8px;
        }}
        .module-card {{
            background: rgba(255,255,255,0.66);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 18px;
            min-height: 180px;
        }}
        .module-card h3 {{
            margin: 0 0 8px 0;
            color: var(--ink);
            font-size: 18px;
        }}
        .module-card p {{
            margin: 0 0 14px 0;
            color: var(--muted);
            font-size: 14px;
            line-height: 1.7;
        }}
        .module-card a {{
            text-decoration:none;
            color: var(--deep);
            font-weight: 700;
            font-size: 13px;
        }}
        .flow-grid {{
            display:grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
        }}
        .flow-card {{
            background: rgba(23,35,44,0.96);
            color: rgba(255,255,255,0.9);
            border-radius: 20px;
            padding: 18px;
            min-height: 158px;
        }}
        .flow-card .step {{
            display:inline-flex;
            align-items:center;
            justify-content:center;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: rgba(255,255,255,0.1);
            color: #f5ede1;
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 12px;
        }}
        .flow-card h3 {{
            margin: 0 0 8px 0;
            font-size: 18px;
        }}
        .flow-card p {{
            margin: 0;
            font-size: 14px;
            line-height: 1.7;
            color: rgba(255,255,255,0.76);
        }}
        {extra}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=300)
def load_data() -> dict[str, object]:
    return {
        "health": service.get_system_health(),
        "snapshot": service.get_analysis_snapshot(),
        "contracts": service.get_contracts(),
        "sources": service.get_source_metadata(),
        "quality": service.get_quality_report(),
        "overview": service.get_market_overview(),
        "comparison": service.get_comparison_frame(),
        "notices": service.get_notice_summary(limit=30),
    }


def render_top_nav(current_page: str, selected_product: str, compare_products: list[str], thesis_mode: bool) -> None:
    compare = ",".join(compare_products) if compare_products else "IF,IH,IC,IM"
    nav_html = "".join(
        f'<a class="{"active" if slug == current_page else ""}" href="{build_href(slug, selected_product, compare, "thesis" if thesis_mode else "")}">{label}</a>'
        for slug, label in PAGES
    )
    st.markdown(
        f"""
        <div class="topbar">
            <div class="brand">China Futures Analytics Platform</div>
            <div class="navlinks">{nav_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(snapshot: pd.DataFrame) -> None:
    if snapshot.empty:
        return
    columns = st.columns(len(snapshot))
    for idx, (_, row) in enumerate(snapshot.sort_values("product_id").iterrows()):
        columns[idx].markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{row["product_id"]} 主力合约</div>
                <div class="metric-value">{num(row["close_price"])}</div>
                <div class="metric-meta">
                    日收益 {pct(row["daily_return"])}<br/>
                    20日波动率 {pct(row["rolling_vol_20"])}<br/>
                    未来5日预测波动率 {pct(row.get("forecast_vol_5d"))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_empty_state(health: dict[str, object]) -> None:
    st.error("当前数据尚未准备完成，系统还不能展示分析结果。")
    st.markdown("### 启动步骤")
    for step in health.get("startup_steps", []):
        st.code(step, language="powershell")
    tables = pd.DataFrame(health.get("tables", []))
    if not tables.empty:
        st.dataframe(tables, use_container_width=True, hide_index=True)


def render_home_page(
    snapshot: pd.DataFrame,
    overview: pd.DataFrame,
    comparison: pd.DataFrame,
    sources: pd.DataFrame,
    quality: pd.DataFrame,
    health: dict[str, object],
    thesis_mode: bool,
) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">Chinese Index Futures Analytics Platform</div>
            <h1>整合真实公开数据，形成可视化分析平台</h1>
            <p>
                面向中国股指期货市场，统一接入 CFFEX、PBC、NBS 公开数据，
                提供趋势分析、波动率预测、相关性分析、VaR 风险评估和系统化展示，
                将真实数据链路、分析能力和展示能力整合为一个可运行的平台产品。
            </p>
            <div class="cta-row">
                <a class="cta-primary" href="{build_href('overview', mode='thesis' if thesis_mode else '')}">查看功能全景</a>
                <a class="cta-secondary" href="{build_href('market', mode='thesis' if thesis_mode else '')}">进入系统展示</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    hero_left, hero_right = st.columns([1.45, 1.0])
    with hero_left:
        st.markdown('<div class="section-title">平台状态概览</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">首屏直接展示平台已接入的真实数据与当前分析状态，首页不是静态介绍页，而是系统能力的公开入口。</div>',
            unsafe_allow_html=True,
        )
        render_metric_cards(snapshot)
    with hero_right:
        st.markdown('<div class="section-title">系统预览</div>', unsafe_allow_html=True)
        preview = overview.copy()
        if not preview.empty:
            preview["daily_return"] = preview["daily_return"].map(pct)
            preview["forecast_vol_5d"] = preview["forecast_vol_5d"].map(pct)
            st.dataframe(
                preview[
                    [
                        "product_id",
                        "instrument_id",
                        "daily_return",
                        "forecast_vol_5d",
                        "forecast_signal",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
        st.markdown(
            f"""
            <div class="panel" style="margin-top: 10px;">
                <div class="metric-label">系统健康状态</div>
                <div class="metric-value" style="font-size:22px;">{health.get("status", "--").upper()}</div>
                <div class="metric-meta">
                    最新交易日 {health.get("latest_trading_date") or "--"}<br/>
                    已就绪数据表 {health.get("ready_table_count", 0)} / {health.get("required_table_count", 0)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">核心能力</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">首页直接映射开题报告中的核心功能，不再用学校项目式叙述，而是用平台能力语言表达。</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="cap-grid">
            <div class="cap-card">
                <div class="cap-kicker">01</div>
                <h3>真实公开数据接入</h3>
                <p>统一接入 CFFEX、PBC、NBS 官方公开数据，保留来源、抓取时间和许可说明，支持后续数据追溯。</p>
            </div>
            <div class="cap-card">
                <div class="cap-kicker">02</div>
                <h3>趋势与波动分析</h3>
                <p>支持主力连续、均线、回撤、滚动波动率和未来 5 日波动率预测，满足盘后研判场景。</p>
            </div>
            <div class="cap-card">
                <div class="cap-kicker">03</div>
                <h3>相关性与风险评估</h3>
                <p>支持股指与宏观因子相关性分析、历史模拟法 VaR 和预测误差观察，兼顾研究与风控表达。</p>
            </div>
            <div class="cap-card">
                <div class="cap-kicker">04</div>
                <h3>系统化展示与答辩复用</h3>
                <p>同一套产品既能作为系统展示页运行，也能输出论文截图、结构图和实验图，降低交付分裂。</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">功能全景</div>', unsafe_allow_html=True)
    feature_left, feature_right = st.columns([1.4, 1.0])
    with feature_left:
        compare_df = comparison[comparison["product_id"].isin(["IF", "IH", "IC", "IM"])].copy()
        fig = px.line(
            compare_df,
            x="trading_date",
            y="normalized_close",
            color="product_id",
            title="四类股指期货主力连续归一化走势",
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.78)", legend_title_text="品种")
        st.plotly_chart(fig, use_container_width=True)
    with feature_right:
        st.markdown(
            f"""
            <div class="panel">
                <div class="metric-label">系统模块入口</div>
                <div class="metric-meta">
                    <a href="{build_href('overview', mode='thesis' if thesis_mode else '')}">市场总览</a><br/>
                    <a href="{build_href('market', mode='thesis' if thesis_mode else '')}">合约行情</a><br/>
                    <a href="{build_href('trend', mode='thesis' if thesis_mode else '')}">趋势与波动</a><br/>
                    <a href="{build_href('risk', mode='thesis' if thesis_mode else '')}">相关性与风险</a><br/>
                    <a href="{build_href('sources', mode='thesis' if thesis_mode else '')}">数据来源</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not overview.empty:
            view = overview.copy()
            view["rolling_vol_20"] = view["rolling_vol_20"].map(pct)
            view["forecast_vol_5d"] = view["forecast_vol_5d"].map(pct)
            st.dataframe(
                view[["product_id", "rolling_vol_20", "forecast_vol_5d", "trend_signal"]],
                use_container_width=True,
                hide_index=True,
            )

    render_module_directory(thesis_mode)
    render_home_showcase(overview, comparison, quality)
    render_platform_flow()

    st.markdown('<div class="section-title">可信数据与平台边界</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="trust-list">
            <div class="trust-item">
                <h4>真实数据来源</h4>
                <p>平台当前接入中金所官方盘后统计、人民银行宏观金融数据与国家统计局宏观统计数据。</p>
            </div>
            <div class="trust-item">
                <h4>数据可追溯</h4>
                <p>每条原始记录保留 source、source_url、fetch_time、license_note 字段，支持结果追溯。</p>
            </div>
            <div class="trust-item">
                <h4>合规边界明确</h4>
                <p>平台定位为盘后分析与研究展示，不做未授权实时行情分发，也不做自动交易执行。</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    bottom_left, bottom_right = st.columns([1.0, 1.0])
    with bottom_left:
        if not sources.empty:
            st.dataframe(sources, use_container_width=True, hide_index=True)
    with bottom_right:
        quality_view = quality.copy()
        if not quality_view.empty:
            quality_view["missing_ratio"] = quality_view["missing_ratio"].map(lambda value: f"{value * 100:.2f}%")
            quality_view["success_rate"] = quality_view["success_rate"].map(lambda value: f"{value * 100:.2f}%")
            st.dataframe(
                quality_view[["dataset_name", "row_count", "date_end", "missing_ratio", "success_rate"]],
                use_container_width=True,
                hide_index=True,
            )

    st.markdown(
        """
        <div class="footer-box">
            <strong>产品定位：</strong> 中国股指期货盘后分析平台。<br/>
            <strong>核心价值：</strong> 把真实公开数据、分析模型和系统展示打通成一个可运行的平台产品。<br/>
            <strong>适用场景：</strong> 运营监测、研究展示、教学实验、毕业设计答辩与论文配图。
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_controls(product_options: list[str], selected_product: str, compare_products: list[str]) -> tuple[str, list[str]]:
    col1, col2 = st.columns([1.0, 1.4])
    with col1:
        product = st.selectbox("主分析品种", product_options, index=product_options.index(selected_product))
    with col2:
        compare = st.multiselect("对比品种", product_options, default=compare_products)
    compare = compare or product_options[:4]
    if product != selected_product or compare != compare_products:
        st.query_params.update({"page": query_value("page", "overview"), "product": product, "compare": ",".join(compare), "mode": query_value("mode", "")})
    return product, compare


def render_module_directory(thesis_mode: bool) -> None:
    st.markdown('<div class="section-title">系统模块导览</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">这里把整个网站和系统页面串起来。你后面如果要改站点结构，直接从这一组模块卡片开始改就可以。</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="module-grid">
            <div class="module-card">
                <h3>市场总览</h3>
                <p>查看四类股指期货主力合约状态、收益变化、滚动波动率与预测信号，是整套系统的总入口。</p>
                <a href="{build_href('overview', mode='thesis' if thesis_mode else '')}">进入页面</a>
            </div>
            <div class="module-card">
                <h3>合约行情</h3>
                <p>查看主力连续 K 线、成交量、持仓量与原始合约表，适合展示具体品种的盘后行情结构。</p>
                <a href="{build_href('market', mode='thesis' if thesis_mode else '')}">进入页面</a>
            </div>
            <div class="module-card">
                <h3>趋势与波动</h3>
                <p>查看均线、回撤、滚动波动率与未来 5 日波动率预测，是开题报告中最核心的分析页面之一。</p>
                <a href="{build_href('trend', mode='thesis' if thesis_mode else '')}">进入页面</a>
            </div>
            <div class="module-card">
                <h3>相关性与风险</h3>
                <p>查看 VaR、宏观相关性矩阵与预测误差表现，形成研究与风控一体化的风险分析区。</p>
                <a href="{build_href('risk', mode='thesis' if thesis_mode else '')}">进入页面</a>
            </div>
            <div class="module-card">
                <h3>数据来源</h3>
                <p>说明数据来源、抓取质量和合规边界，保证整套系统不仅能看，还能解释数据来自哪里。</p>
                <a href="{build_href('sources', mode='thesis' if thesis_mode else '')}">进入页面</a>
            </div>
            <div class="module-card">
                <h3>本机运行与答辩复用</h3>
                <p>当前站点同时支持本机演示、系统截图、论文配图和页面二次修改，适合作为完整毕业设计站点使用。</p>
                <a href="{build_href('home', mode='thesis' if thesis_mode else '')}">返回首页</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_platform_flow() -> None:
    st.markdown('<div class="section-title">平台运行流程</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">这部分直接对应开题报告中的“数据采集、存储、处理、分析和可视化”全过程，让网站不仅像展示页，也像完整系统说明页。</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="flow-grid">
            <div class="flow-card">
                <div class="step">01</div>
                <h3>采集与落库</h3>
                <p>系统从 CFFEX、PBC、NBS 官方公开页面抓取原始数据，落入原始层与标准层数据表。</p>
            </div>
            <div class="flow-card">
                <div class="step">02</div>
                <h3>分析与建模</h3>
                <p>构建主力连续序列，计算收益率、回撤、滚动波动率、波动率预测、相关性矩阵与 VaR。</p>
            </div>
            <div class="flow-card">
                <div class="step">03</div>
                <h3>展示与复用</h3>
                <p>通过首页和系统展示页统一呈现结果，同时支持 API 查询、截图输出与论文配图复用。</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home_showcase(overview: pd.DataFrame, comparison: pd.DataFrame, quality: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">展示页面预览</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">首页下面直接嵌入系统展示预览，让整个网站不是“介绍页 + 另一个系统”，而是一个完整连贯的展示站。</div>',
        unsafe_allow_html=True,
    )
    tabs = st.tabs(["市场走势", "风险结果", "数据质量"])
    with tabs[0]:
        if not comparison.empty:
            fig = px.line(
                comparison[comparison["product_id"].isin(["IF", "IH", "IC", "IM"])],
                x="trading_date",
                y="cum_return_pct",
                color="product_id",
                title="系统预览：累计收益率走势",
            )
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.78)", legend_title_text="品种")
            st.plotly_chart(fig, use_container_width=True)
    with tabs[1]:
        if not overview.empty:
            view = overview.copy()
            view["daily_return"] = view["daily_return"].map(pct)
            view["rolling_vol_20"] = view["rolling_vol_20"].map(pct)
            view["forecast_vol_5d"] = view["forecast_vol_5d"].map(pct)
            st.dataframe(
                view[
                    [
                        "product_id",
                        "daily_return",
                        "rolling_vol_20",
                        "forecast_vol_5d",
                        "risk_level",
                        "forecast_signal",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
    with tabs[2]:
        if not quality.empty:
            view = quality.copy()
            view["missing_ratio"] = view["missing_ratio"].map(lambda value: f"{value * 100:.2f}%")
            view["success_rate"] = view["success_rate"].map(lambda value: f"{value * 100:.2f}%")
            st.dataframe(view, use_container_width=True, hide_index=True)


def render_overview_page(snapshot: pd.DataFrame, overview: pd.DataFrame, comparison: pd.DataFrame, compare_products: list[str]) -> None:
    st.markdown('<div class="section-title">市场总览</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">这里是系统展示区的总览入口，承接首页“查看功能全景”的主按钮。</div>', unsafe_allow_html=True)
    render_metric_cards(snapshot)
    compare_df = comparison[comparison["product_id"].isin(compare_products)].copy()
    fig = px.line(compare_df, x="trading_date", y="cum_return_pct", color="product_id", title="累计收益率对比（%）")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.78)")
    st.plotly_chart(fig, use_container_width=True)
    if not overview.empty:
        view = overview.copy()
        for column in ["daily_return", "rolling_vol_20", "forecast_vol_5d", "drawdown"]:
            if column in view.columns:
                view[column] = view[column].map(pct)
        st.dataframe(view, use_container_width=True, hide_index=True)


def render_market_page(selected_product: str, contracts: pd.DataFrame) -> None:
    st.markdown(f'<div class="section-title">{selected_product} 合约行情</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">展示主力连续 K 线、成交量、持仓量与原始合约数据，是产品中的行情展示模块。</div>', unsafe_allow_html=True)
    main_df = service.get_market_daily(product_id=selected_product, main_only=True, limit=180)
    raw_df = service.get_market_daily(product_id=selected_product, main_only=False, limit=360)
    if main_df.empty:
        st.warning("该品种暂无可展示数据。")
        return

    main_df["trading_date"] = pd.to_datetime(main_df["trading_date"])
    top_left, top_right = st.columns([2.0, 1.0])
    with top_left:
        candle = go.Figure(
            data=[
                go.Candlestick(
                    x=main_df["trading_date"],
                    open=main_df["open_price"],
                    high=main_df["high_price"],
                    low=main_df["low_price"],
                    close=main_df["close_price"],
                    name=selected_product,
                )
            ]
        )
        candle.update_layout(title=f"{selected_product} 主力连续 K 线", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.78)")
        st.plotly_chart(candle, use_container_width=True)
    with top_right:
        latest = main_df.sort_values("trading_date").tail(1).iloc[0]
        st.markdown(
            f"""
            <div class="panel">
                <div class="metric-label">当前主力</div>
                <div class="metric-value" style="font-size:24px;">{latest["instrument_id"]}</div>
                <div class="metric-meta">
                    收盘价 {num(latest["close_price"])}<br/>
                    持仓量 {num(latest["open_interest"], 0)}<br/>
                    成交量 {num(latest["volume"], 0)}<br/>
                    持仓变化 {num(latest["open_interest_change"], 0)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(contracts[contracts["product_id"] == selected_product], use_container_width=True, hide_index=True)

    sub_left, sub_right = st.columns(2)
    with sub_left:
        volume_fig = px.bar(main_df.tail(60), x="trading_date", y="volume", title="近60日成交量")
        volume_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.78)")
        st.plotly_chart(volume_fig, use_container_width=True)
    with sub_right:
        oi_fig = px.line(main_df.tail(60), x="trading_date", y="open_interest", title="近60日持仓量")
        oi_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.78)")
        st.plotly_chart(oi_fig, use_container_width=True)

    st.dataframe(raw_df.sort_values(["trading_date", "instrument_id"], ascending=[False, True]).head(160), use_container_width=True, hide_index=True)


def render_trend_page(selected_product: str) -> None:
    st.markdown(f'<div class="section-title">{selected_product} 趋势与波动</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">承接首页能力模块，聚焦趋势分析、回撤、滚动波动率与未来 5 日波动率预测。</div>', unsafe_allow_html=True)
    trend = service.get_trend(selected_product, window=20)
    volatility = service.get_volatility(selected_product, window=20)
    trend_df = pd.DataFrame(trend.get("series", []))
    vol_df = pd.DataFrame(volatility.get("series", []))
    if trend_df.empty or vol_df.empty:
        st.warning("该品种暂无趋势分析结果。")
        return

    top_left, top_right = st.columns([1.6, 1.0])
    with top_left:
        trend_fig = px.line(trend_df, x="trading_date", y=["close_price", "moving_average"], title=f"{selected_product} 收盘价与20日均线")
        trend_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.78)")
        st.plotly_chart(trend_fig, use_container_width=True)
    with top_right:
        latest = trend_df.tail(1).iloc[0]
        st.markdown(
            f"""
            <div class="panel">
                <div class="metric-label">趋势结论</div>
                <div class="metric-value" style="font-size:24px;">{'偏强' if float(latest['close_price']) >= float(latest['moving_average']) else '偏弱'}</div>
                <div class="metric-meta">
                    日收益 {pct(latest['daily_return'])}<br/>
                    累计收益 {pct(latest['cum_return'])}<br/>
                    当前回撤 {pct(latest['drawdown'])}<br/>
                    未来5日波动预测 {pct(volatility.get('latest_forecast_vol_5d'))}<br/>
                    预测信号 {volatility.get('latest_signal') or '--'}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    row_two_left, row_two_right = st.columns(2)
    with row_two_left:
        drawdown_fig = px.area(trend_df, x="trading_date", y="drawdown", title="回撤曲线")
        drawdown_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.78)")
        st.plotly_chart(drawdown_fig, use_container_width=True)
    with row_two_right:
        rolling_fig = px.line(vol_df, x="trading_date", y="rolling_volatility", title="20日滚动年化波动率")
        rolling_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.78)")
        st.plotly_chart(rolling_fig, use_container_width=True)

    forecast_fig = px.line(vol_df, x="trading_date", y=["forecast_vol_5d", "future_realized_vol_5d"], title=f"{selected_product} 波动率预测与未来5日实现波动率")
    forecast_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.78)")
    st.plotly_chart(forecast_fig, use_container_width=True)


def render_risk_page(selected_product: str, quality: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">相关性与风险</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">展示 VaR、相关性矩阵与预测误差，是产品风险分析模块的集中展示页。</div>', unsafe_allow_html=True)
    var_df = service.get_var()
    corr_df = service.get_correlation()
    forecast_df = service.get_volatility_forecast(limit=240)

    top_left, top_right = st.columns([1.3, 1.0])
    with top_left:
        if not var_df.empty:
            view = var_df.copy()
            view["var_value"] = view["var_value"].map(pct)
            st.dataframe(view, use_container_width=True, hide_index=True)
    with top_right:
        if not quality.empty:
            view = quality.copy()
            view["missing_ratio"] = view["missing_ratio"].map(lambda value: f"{value * 100:.2f}%")
            view["success_rate"] = view["success_rate"].map(lambda value: f"{value * 100:.2f}%")
            st.dataframe(view, use_container_width=True, hide_index=True)

    if not corr_df.empty:
        heatmap_df = corr_df.set_index("series")
        heatmap = px.imshow(heatmap_df, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r", title="股指期货与宏观指标月度相关性矩阵")
        heatmap.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(heatmap, use_container_width=True)

    if not forecast_df.empty:
        product_forecast = forecast_df[forecast_df["product_id"] == selected_product].tail(60).copy()
        if not product_forecast.empty:
            error_fig = px.bar(product_forecast, x="trading_date", y="forecast_error", color="forecast_signal", title=f"{selected_product} 波动率预测误差")
            error_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.78)")
            st.plotly_chart(error_fig, use_container_width=True)


def render_sources_page(sources: pd.DataFrame, quality: pd.DataFrame, notices: pd.DataFrame, health: dict[str, object]) -> None:
    st.markdown('<div class="section-title">数据来源</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">面向运营方公开说明平台数据来源、质量情况和合规边界。</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.dataframe(sources, use_container_width=True, hide_index=True)
    with right:
        quality_view = quality.copy()
        if not quality_view.empty:
            quality_view["missing_ratio"] = quality_view["missing_ratio"].map(lambda value: f"{value * 100:.2f}%")
            quality_view["success_rate"] = quality_view["success_rate"].map(lambda value: f"{value * 100:.2f}%")
            st.dataframe(quality_view, use_container_width=True, hide_index=True)

    notice_view = notices.copy()
    if not notice_view.empty:
        notice_view["published_date"] = pd.to_datetime(notice_view["published_date"]).dt.strftime("%Y-%m-%d")
        st.dataframe(notice_view[["published_date", "tag", "category", "title", "url"]].head(15), use_container_width=True, hide_index=True)

    st.markdown(
        f"""
        <div class="panel" style="margin-top: 14px;">
            <div class="metric-label">平台说明</div>
            <div class="metric-meta">
                当前状态：{health.get("status", "--")}<br/>
                最新交易日：{health.get("latest_trading_date") or "--"}<br/>
                行情数据基于中金所官方盘后统计，不提供未授权实时行情分发。<br/>
                宏观数据来自人民银行和国家统计局公开页面，适合研究、监测和展示场景。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    thesis_mode = query_value("mode", "") == "thesis"
    inject_styles(thesis_mode)

    data = load_data()
    health = data["health"]
    if health.get("status") == "empty":
        render_empty_state(health)
        return

    snapshot = data["snapshot"]
    contracts = data["contracts"]
    sources = data["sources"]
    quality = data["quality"]
    overview = data["overview"]
    comparison = data["comparison"]
    notices = data["notices"]

    product_options = sorted(contracts["product_id"].dropna().unique()) if not contracts.empty else ["IF"]
    current_page = query_value("page", "home")
    if current_page not in PAGE_SLUG_TO_LABEL:
        current_page = "home"

    selected_product = query_value("product", product_options[0])
    if selected_product not in product_options:
        selected_product = product_options[0]

    compare_products = [item for item in query_value("compare", ",".join(product_options[:4])).split(",") if item in product_options]
    compare_products = compare_products or product_options[:4]

    render_top_nav(current_page, selected_product, compare_products, thesis_mode)

    if current_page != "home":
        selected_product, compare_products = render_page_controls(product_options, selected_product, compare_products)

    if current_page == "home":
        render_home_page(snapshot, overview, comparison, sources, quality, health, thesis_mode)
    elif current_page == "overview":
        render_overview_page(snapshot, overview, comparison, compare_products)
    elif current_page == "market":
        render_market_page(selected_product, contracts)
    elif current_page == "trend":
        render_trend_page(selected_product)
    elif current_page == "risk":
        render_risk_page(selected_product, quality)
    elif current_page == "sources":
        render_sources_page(sources, quality, notices, health)


if __name__ == "__main__":
    main()
