from __future__ import annotations

import streamlit as st

from fraud_detection.site_content import build_primary_nav_items


def get_primary_nav_items() -> list[dict[str, str]]:
    return build_primary_nav_items()


def inject_site_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --page-bg: #f4f8fc;
            --card-bg: rgba(255, 255, 255, 0.88);
            --line: rgba(148, 163, 184, 0.24);
            --ink: #0f172a;
            --muted: #475569;
            --brand: #1d4ed8;
            --brand-soft: rgba(29, 78, 216, 0.12);
        }

        [data-testid="stSidebar"],
        [data-testid="collapsedControl"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        #MainMenu,
        footer {
            display: none !important;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(29, 78, 216, 0.12), transparent 24%),
                linear-gradient(180deg, #f8fbff 0%, #eef4fa 52%, #f8fafc 100%);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 1.1rem;
            padding-bottom: 2rem;
        }

        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.9rem 1rem;
            border-radius: 18px;
            border: 1px solid var(--line);
            background: rgba(255, 255, 255, 0.78);
            backdrop-filter: blur(12px);
            box-shadow: 0 18px 36px rgba(15, 23, 42, 0.05);
        }

        .brand-wrap {
            display: flex;
            flex-direction: column;
            gap: 0.15rem;
        }

        .brand-title {
            color: var(--ink);
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: 0.04em;
        }

        .brand-subtitle {
            color: var(--muted);
            font-size: 0.82rem;
        }

        .nav-links {
            display: flex;
            gap: 0.65rem;
            flex-wrap: wrap;
        }

        .nav-link {
            color: var(--muted);
            font-size: 0.92rem;
            font-weight: 600;
            text-decoration: none;
            padding: 0.45rem 0.85rem;
            border-radius: 999px;
            transition: all 0.18s ease;
        }

        .nav-link:hover,
        .nav-link-active {
            color: var(--brand);
            background: var(--brand-soft);
        }

        .hero {
            margin-top: 1rem;
            padding: 1.8rem 1.9rem;
            border-radius: 28px;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(29, 78, 216, 0.92));
            color: #eff6ff;
            box-shadow: 0 26px 56px rgba(15, 23, 42, 0.15);
        }

        .hero-title {
            font-size: 2.18rem;
            line-height: 1.16;
            font-weight: 700;
            margin-bottom: 0.7rem;
        }

        .hero-copy {
            max-width: 44rem;
            font-size: 1rem;
            line-height: 1.8;
            opacity: 0.92;
            margin-bottom: 0.7rem;
        }

        .hero-meta {
            color: #bfdbfe;
            font-size: 0.92rem;
            font-weight: 600;
        }

        .page-hero {
            margin-top: 1rem;
            margin-bottom: 0.8rem;
            padding: 1.3rem 1.4rem;
            border-radius: 24px;
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid var(--line);
            box-shadow: 0 16px 36px rgba(15, 23, 42, 0.05);
        }

        .page-title {
            color: var(--ink);
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 0.4rem;
        }

        .page-copy {
            color: var(--muted);
            line-height: 1.8;
            font-size: 0.98rem;
        }

        .page-meta {
            margin-top: 0.55rem;
            color: var(--brand);
            font-size: 0.88rem;
            font-weight: 600;
        }

        .section-title {
            margin-top: 2rem;
            margin-bottom: 0.75rem;
            color: var(--ink);
            font-size: 1.3rem;
            font-weight: 700;
        }

        .summary-card {
            padding: 1rem 1.05rem;
            border-radius: 18px;
            border: 1px solid var(--line);
            background: var(--card-bg);
            box-shadow: 0 14px 34px rgba(15, 23, 42, 0.05);
        }

        .summary-label {
            color: var(--muted);
            font-size: 0.9rem;
            margin-bottom: 0.35rem;
        }

        .summary-value {
            color: var(--ink);
            font-size: 1.55rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .panel {
            padding: 1rem;
            border-radius: 20px;
            border: 1px solid var(--line);
            background: rgba(255, 255, 255, 0.82);
            box-shadow: 0 16px 36px rgba(15, 23, 42, 0.04);
        }

        @media (max-width: 840px) {
            .topbar {
                flex-direction: column;
                align-items: flex-start;
            }

            .hero-title {
                font-size: 1.8rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_primary_topbar(current_page: str) -> None:
    links = []
    for item in get_primary_nav_items():
        active = " nav-link-active" if item["page"] == current_page else ""
        links.append(
            f'<a class="nav-link{active}" href="?page={item["page"]}">{item["label"]}</a>'
        )
    st.markdown(
        f"""
        <div class="topbar">
            <div class="brand-wrap">
                <div class="brand-title">金融交易风险驾驶舱</div>
                <div class="brand-subtitle">金融欺诈检测展示系统</div>
            </div>
            <div class="nav-links">{''.join(links)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, description: str, meta: str | None = None) -> None:
    meta_html = f'<div class="hero-meta">{meta}</div>' if meta else ""
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">{title}</div>
            <div class="hero-copy">{description}</div>
            {meta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_intro(title: str, description: str, meta: str | None = None) -> None:
    meta_html = f'<div class="page-meta">{meta}</div>' if meta else ""
    st.markdown(
        f"""
        <div class="page-hero">
            <div class="page-title">{title}</div>
            <div class="page-copy">{description}</div>
            {meta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-label">{label}</div>
            <div class="summary-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_title(title: str) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
