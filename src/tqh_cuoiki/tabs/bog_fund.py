import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from tqh_cuoiki.dashboard_utils import progress_svg, sparkline_svg, style_figure


COLORS = {"Petrolimex": "#0B1849", "PVOil": "#C1B49A"}
FUEL_SPENDING_COLS = [
    "ron95_bog_spending",
    "diesel_bog_spending",
    "e5ron92_bog_spending",
    "mazut_bog_spending",
]


def _negative_streaks(series: pd.Series) -> list[int]:
    """Trả về danh sách độ dài của từng đợt giá trị âm liên tục."""
    neg = series < 0
    groups = (neg != neg.shift()).cumsum()
    lengths = []
    for _, sub in neg.groupby(groups):
        if bool(sub.iloc[0]):
            lengths.append(int(sub.sum()))
    return lengths


@st.cache_data(show_spinner=False)
def _price_hold_cycles(df_full: pd.DataFrame) -> pd.DataFrame:
    """Tính độ dài chu kỳ và chi quỹ BOG trung bình/ngày giữa hai kỳ điều chỉnh liên tiếp."""
    d = df_full.sort_values("date").reset_index(drop=True).copy()
    d["total_bog_spending"] = d[FUEL_SPENDING_COLS].sum(axis=1)
    adj_dates = d.loc[d["is_adjustment_day"] == 1, "date"].reset_index(drop=True)

    rows = []
    for i in range(1, len(adj_dates)):
        start, end = adj_dates[i - 1], adj_dates[i]
        mask = (d["date"] >= start) & (d["date"] < end)
        rows.append(
            {
                "length_days": int((end - start).days),
                "avg_spend": d.loc[mask, "total_bog_spending"].mean(),
            }
        )
    return pd.DataFrame(rows)


def _kpi_card(title, value, note, visual):
    st.markdown(
        f'<div class="kpi-card"><div><div class="kpi-title">{title}</div>'
        f'<div class="kpi-value">{value}</div></div><div style="margin:6px 0">{visual}</div>'
        f'<div class="kpi-trend">{note}</div></div>',
        unsafe_allow_html=True,
    )


def render(df: pd.DataFrame, selected_year: str, df_full: pd.DataFrame):
    st.markdown(
        """<div style="display:flex;align-items:center;justify-content:space-between;
        border-bottom:2px solid var(--line);padding-bottom:12px;margin-bottom:20px;width:100%;">
        <div style="font-size:30px;font-weight:800;color:var(--brand);letter-spacing:-0.8px;line-height:1.1;font-family:inherit;">
        Quỹ Bình Ổn Giá <span style="color:var(--muted);font-weight:600;font-family:inherit;">Petrolimex vs PVOil</span>
        </div><span style="background:var(--brand);color:#fff;font-size:10px;font-weight:800;
        padding:4px 10px;border-radius:999px;letter-spacing:.5px;text-transform:uppercase;">
        Biến động số dư quỹ BOG</span></div>""",
        unsafe_allow_html=True,
    )

    data = df.sort_values("date").copy()
    if data.empty:
        st.warning("Không có dữ liệu phù hợp với bộ lọc hiện tại.")
        return

    petro_col, pvoil_col = "petrolimex_bog_ty_dong", "pvoil_bog_ty_dong"
    latest = data.iloc[-1]
    petro_streaks = _negative_streaks(data[petro_col])
    pvoil_streaks = _negative_streaks(data[pvoil_col])
    spread = data[petro_col] - data[pvoil_col]
    cycles_source = df_full if selected_year == "Tất cả các năm" else data
    cycles = _price_hold_cycles(cycles_source)
    valid_cycles = cycles.dropna(subset=["avg_spend", "length_days"]) if not cycles.empty else cycles
    corr = (
        valid_cycles["avg_spend"].corr(valid_cycles["length_days"])
        if len(valid_cycles) >= 2
        else np.nan
    )

    k1, k2, k3, k4, k5 = st.columns(5)
    expected_days = (data["date"].max() - data["date"].min()).days + 1
    coverage = len(data) / expected_days * 100 if expected_days > 0 else 0
    with k1:
        _kpi_card(
            "SỐ NGÀY DỮ LIỆU",
            f"{len(data):,}",
            f"Độ phủ ngày: {coverage:.1f}%",
            progress_svg(coverage),
        )
    with k2:
        _kpi_card(
            "SỐ DƯ QUỸ PETROLIMEX",
            f"{latest[petro_col]:,.0f} tỷ đồng",
            "Cập nhật kỳ cuối",
            sparkline_svg(data[petro_col], COLORS["Petrolimex"], "bog-petro"),
        )
    with k3:
        _kpi_card(
            "SỐ DƯ QUỸ PVOIL",
            f"{latest[pvoil_col]:,.0f} tỷ đồng",
            "Cập nhật kỳ cuối",
            sparkline_svg(data[pvoil_col], COLORS["PVOil"], "bog-pvoil"),
        )
    with k4:
        pct_neg_pvoil = (data[pvoil_col] < 0).mean() * 100
        _kpi_card(
            "% NGÀY PVOIL ÂM QUỸ",
            f"{pct_neg_pvoil:.1f}%",
            f"Đợt dài nhất: {max(pvoil_streaks) if pvoil_streaks else 0} ngày",
            "",
        )
    with k5:
        latest_spread = float(spread.iloc[-1]) if len(spread) else 0.0
        spread_note = "Petrolimex cao hơn" if latest_spread >= 0 else "PVOil cao hơn"
        _kpi_card(
            "CHÊNH LỆCH PETROLIMEX - PVOIL",
            f"{latest_spread:+,.0f} tỷ đồng",
            spread_note,
            sparkline_svg(spread, "#7288AE", "bog-spread"),
        )

    row1_left, row1_right = st.columns([4, 6])

    with row1_left:
        st.markdown("<div class='section-header'>PHÂN PHỐI SỐ DƯ QUỸ (TỶ ĐỒNG)</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(
            go.Box(
                y=data[petro_col],
                name="Petrolimex",
                marker_color=COLORS["Petrolimex"],
                boxmean=True,
            )
        )
        fig.add_trace(
            go.Box(
                y=data[pvoil_col],
                name="PVOil",
                marker_color=COLORS["PVOil"],
                boxmean=True,
            )
        )
        fig.add_hline(y=0, line_color="#94A3B8", line_dash="dash")
        fig.update_layout(
            height=322,
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis=dict(title="Tỷ đồng", zeroline=False),
            showlegend=False,
            margin=dict(l=48, r=20, t=20, b=35),
        )
        style_figure(fig, show_legend=False)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with row1_right:
        st.markdown("<div class='section-header'>DIỄN BIẾN SỐ DƯ QUỸ THEO THỜI GIAN</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data["date"],
                y=data[petro_col],
                name="Petrolimex",
                line=dict(color=COLORS["Petrolimex"], width=2),
                cliponaxis=False,
                hovertemplate="Ngày %{x|%d/%m/%Y}<br>Petrolimex: %{y:,.0f} tỷ<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=data["date"],
                y=data[pvoil_col],
                name="PVOil",
                line=dict(color=COLORS["PVOil"], width=2),
                cliponaxis=False,
                hovertemplate="Ngày %{x|%d/%m/%Y}<br>PVOil: %{y:,.0f} tỷ<extra></extra>",
            )
        )
        fig.add_hline(y=0, line_color="#94A3B8")
        date_padding = pd.Timedelta(days=45)
        fig.update_layout(
            height=322,
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis_title="Tỷ đồng",
            xaxis=dict(range=[data["date"].min() - date_padding, data["date"].max() + date_padding]),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.5),
            hovermode="x unified",
            margin=dict(l=58, r=28, t=48, b=42),
        )
        style_figure(fig)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    row2_left, row2_right = st.columns(2)

    with row2_left:
        st.markdown("<div class='section-header'>ĐỘ DÀI CÁC GIAI ĐOẠN ÂM QUỸ</div>", unsafe_allow_html=True)
        companies = ["Petrolimex", "PVOil"]
        avg_len = [
            float(np.mean(petro_streaks)) if petro_streaks else 0.0,
            float(np.mean(pvoil_streaks)) if pvoil_streaks else 0.0,
        ]
        max_len = [
            max(petro_streaks) if petro_streaks else 0,
            max(pvoil_streaks) if pvoil_streaks else 0,
        ]
        labels = [f"{company} ({count} đợt)" for company, count in zip(companies, [len(petro_streaks), len(pvoil_streaks)])]
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=labels,
                y=avg_len,
                name="Độ dài TB mỗi đợt",
                marker_color="#7288AE",
                text=[f"{value:.0f}" for value in avg_len],
                textposition="outside",
                cliponaxis=False,
            )
        )
        fig.add_trace(
            go.Bar(
                x=labels,
                y=max_len,
                name="Đợt dài nhất",
                marker_color="#0B1849",
                text=[f"{value:.0f}" for value in max_len],
                textposition="outside",
                cliponaxis=False,
            )
        )
        fig.update_layout(
            height=240,
            barmode="group",
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis=dict(title="Số ngày", rangemode="tozero"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            bargap=0.28,
            bargroupgap=0.08,
            margin=dict(l=45, r=15, t=42, b=45),
        )
        style_figure(fig)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with row2_right:
        st.markdown("<div class='section-header'>CHI QUỸ BOG VÀ ĐỘ DÀI CHU KỲ GIỮ GIÁ</div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='color:var(--muted);font-size:12px;margin-top:-6px;margin-bottom:8px;'>"
            "Chu kỳ được tính là khoảng thời gian giữa 2 lần điều chỉnh giá liên tiếp. "
            "Chi quỹ là trung bình/ngày (tổng 4 loại nhiên liệu) trong chu kỳ.</div>",
            unsafe_allow_html=True,
        )
        if len(valid_cycles) < 2:
            st.info("Chưa đủ chu kỳ điều chỉnh để phân tích mối liên hệ giữa chi quỹ và độ dài giữ giá.")
        else:
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=valid_cycles["avg_spend"],
                    y=valid_cycles["length_days"],
                    mode="markers",
                    marker=dict(color="#7288AE", size=8, line=dict(color="white", width=0.5)),
                    name="Chu kỳ giữ giá",
                    hovertemplate="Chi quỹ TB/ngày: %{x:,.0f} đ<br>Độ dài chu kỳ: %{y} ngày<extra></extra>",
                )
            )
            z = np.polyfit(valid_cycles["avg_spend"], valid_cycles["length_days"], 1)
            x_min = float(valid_cycles["avg_spend"].min())
            x_max = float(valid_cycles["avg_spend"].max())
            x_line = np.linspace(x_min, x_max if x_max > x_min else x_min + 1, 50)
            fig.add_trace(
                go.Scatter(
                    x=x_line,
                    y=np.polyval(z, x_line),
                    mode="lines",
                    line=dict(color="#0B1849", width=2, dash="dash"),
                    name=f"Xu hướng (r={corr:.2f})" if pd.notna(corr) else "Xu hướng",
                )
            )
            fig.update_layout(
                height=240,
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(title="Chi quỹ TB/ngày trong chu kỳ (đ, tổng 4 nhiên liệu)"),
                yaxis=dict(title="Độ dài chu kỳ giữ giá (ngày)", rangemode="tozero"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=48, r=20, t=38, b=42),
            )
            style_figure(fig)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with st.expander("Xem dữ liệu quỹ BOG theo bộ lọc"):
        cols = ["date", "is_adjustment_day", petro_col, pvoil_col] + FUEL_SPENDING_COLS
        st.dataframe(data[cols], width="stretch", hide_index=True)
