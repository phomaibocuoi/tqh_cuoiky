from pathlib import Path

import pandas as pd
import streamlit as st

from tqh_cuoiki.tabs import overview, price_management


ROOT = Path(__file__).resolve().parents[2]


def _inject_styles() -> None:
    st.markdown(
        """
<style>
    :root {
        --bg: #FFFFFF;
        --panel: #FFFFFF;
        --sidebar: #0B1849;
        --sidebar-active: #EAE0CF;
        --text: #0B1849;
        --muted: #4B5694;
        --brand: #0B1849;
        --accent: #C2540A;
        --red: #C0362C;
        --green: #2E7D4F;
        --line: #E2E8F0;

        --fuel-1: #0B1849;
        --fuel-2: #4B5694;
        --fuel-3: #7288AE;
        --fuel-4: #C1B49A;
    }

    header[data-testid="stHeader"] {
        background-color: var(--bg) !important;
        border: none !important;
        box-shadow: none !important;
    }

    .stApp {
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    div.block-container {
        padding-top: 3.25rem;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 1rem;
    }

    section[data-testid="stSidebar"] {
        background: rgba(11, 24, 73, 0.88) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    section[data-testid="stSidebar"] > div {
        background-color: transparent !important;
    }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
        background-color: var(--sidebar-active) !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        height: 38px !important;
        text-align: left !important;
        padding-left: 14px !important;
        width: 100% !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] p,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] span,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] div {
        color: #0B1849 !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"] {
        background-color: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        height: 38px !important;
        text-align: left !important;
        padding-left: 14px !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"] p,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"] span,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"] div {
        color: rgba(255, 255, 255, 0.85) !important;
        font-weight: 500 !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.08) !important;
    }

    .hero-title {
        font-size: 32px;
        font-weight: 800;
        color: var(--brand) !important;
        letter-spacing: -0.5px;
        margin: 0;
    }

    .hero-subtitle {
        color: var(--muted) !important;
        margin-top: 4px;
        margin-bottom: 16px;
        font-size: 14px;
    }

    .kpi-card {
        background-color: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px;
        padding: 12px 14px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.01), 0 10px 15px -3px rgba(0, 0, 0, 0.02);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 116px !important;
        box-sizing: border-box !important;
        margin-bottom: 8px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(30, 58, 95, 0.08);
    }

    .kpi-card p, .kpi-card div, .kpi-card span {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }

    .kpi-card-1, .kpi-card-2, .kpi-card-3, .kpi-card-4, .kpi-card-5 {
        border-top: 1px solid var(--line) !important;
    }

    .kpi-title {
        font-size: 11px;
        color: var(--muted) !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 20px;
        color: var(--brand) !important;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .kpi-trend {
        font-size: 12px;
        font-weight: 600;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .kpi-trend-up {
        color: var(--green) !important;
    }
    .kpi-trend-down {
        color: var(--red) !important;
    }

    .section-header {
        font-size: 14px;
        font-weight: 700;
        color: var(--brand) !important;
        border-bottom: 2px solid var(--line) !important;
        padding-bottom: 6px;
        margin-top: 12px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    div[data-testid="stPlotlyChart"] {
        background-color: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        padding: 8px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02) !important;
    }

    div[data-testid="stDataFrame"] {
        background-color: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02) !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label,
    section[data-testid="stSidebar"] div[data-testid="stCheckbox"] label {
        color: rgba(255, 255, 255, 0.85) !important;
        font-weight: 600 !important;
        font-size: 12px !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.15) !important;
        margin: 12px 0 !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
        border-radius: 6px !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #FFFFFF !important;
    }
</style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "vn_fuel_price_2018_present.csv")
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
    return df.sort_values("date").reset_index(drop=True)


def run_app() -> None:
    st.set_page_config(
        page_title="Dashboard Giá Xăng Dầu Việt Nam",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _inject_styles()

    try:
        df = load_data()
    except Exception as exc:
        st.error(f"Không thể đọc data/vn_fuel_price_2018_present.csv: {exc}")
        st.stop()

    if "page" not in st.session_state:
        st.session_state.page = "Tổng quan"

    st.sidebar.markdown("<div style='padding: 8px 2px 2px 2px; text-align: left;'><div style='font-size: 20px; font-weight: 900; color: #FFFFFF; line-height: 1.2; letter-spacing: -0.5px;'>PHÂN TÍCH XĂNG DẦU</div></div>", unsafe_allow_html=True)
    st.sidebar.markdown("<hr style='border-top: 1px solid rgba(255,255,255,0.16); margin: 14px 0;'>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-weight: 700; color: #64748B; margin-bottom: 8px; font-size: 11px; letter-spacing: 0.5px;'>DANH MỤC TRANG</p>", unsafe_allow_html=True)

    if st.sidebar.button(
        "Tổng quan thị trường",
        width="stretch",
        type="primary" if st.session_state.page == "Tổng quan" else "secondary",
    ):
        st.session_state.page = "Tổng quan"
        st.rerun()

    if st.sidebar.button(
        "Cơ chế điều hành giá",
        width="stretch",
        type="primary" if st.session_state.page == "Cơ chế điều hành" else "secondary",
    ):
        st.session_state.page = "Cơ chế điều hành"
        st.rerun()

    st.sidebar.markdown("<hr style='border-top: 1px solid #1E293B; margin: 15px 0;'>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-weight: 700; color: #64748B; margin-bottom: 8px; font-size: 11px; letter-spacing: 0.5px;'>BỘ LỌC HIỂN THỊ</p>", unsafe_allow_html=True)

    years_list = ["Tất cả các năm"] + sorted(list(df["date"].dt.year.unique().astype(str)))
    selected_year = st.sidebar.selectbox("Chọn năm phân tích:", years_list)

    st.sidebar.markdown("<p style='font-weight: 700; color: #64748B; margin-top: 15px; margin-bottom: 8px; font-size: 11px; letter-spacing: 0.5px;'>LOẠI NHIÊN LIỆU PHÂN TÍCH</p>", unsafe_allow_html=True)
    fuel_option = st.sidebar.selectbox(
        "Chọn loại xăng dầu:",
        ["Tất cả nhiên liệu", "Xăng RON 95", "Xăng E5 RON 92", "Dầu Diesel"],
        key="fuel_selectbox",
    )

    if fuel_option == "Tất cả nhiên liệu":
        selected_fuels = ["Xăng RON 95", "Xăng E5 RON 92", "Dầu Diesel"]
    else:
        selected_fuels = [fuel_option]

    if selected_year == "Tất cả các năm":
        filtered_df = df.copy()
    else:
        filtered_df = df[df["date"].dt.year == int(selected_year)].copy()

    if st.session_state.page == "Tổng quan":
        overview.render(filtered_df, selected_fuels)
    else:
        price_management.render(filtered_df, selected_fuels, selected_year, df)