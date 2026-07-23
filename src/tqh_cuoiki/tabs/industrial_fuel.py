import plotly.graph_objects as go
import streamlit as st

from tqh_cuoiki.dashboard_utils import adjustment_rows, progress_svg, sparkline_svg, style_figure


MAZUT_UNIT = "đ/kg"
MAZUT_COLOR = "#C2540A"
BRAND_COLOR = "#0B1849"
MUTED_COLOR = "#4B5694"
BLUE_SOFT_COLOR = "#7288AE"
SOFT_COLOR = "#C1B49A"
TRANSPORT_RETAIL_COLS = [
    "ron95_retail_price",
    "e5ron92_retail_price",
    "diesel_retail_price",
]


def _kpi_card(title, value, note, visual=""):
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-title">{title}</div>'
        f'<div class="kpi-value">{value}</div><div style="margin:6px 0">{visual}</div>'
        f'<div class="kpi-trend">{note}</div></div>',
        unsafe_allow_html=True,
    )


def _prepare_data(df):
    data = df.sort_values("date").copy()
    data["transport_avg_retail_price"] = data[TRANSPORT_RETAIL_COLS].mean(axis=1)
    data["mazut_transport_gap"] = data["mazut_retail_price"] - data["transport_avg_retail_price"]
    data["mazut_base_retail_gap"] = data["mazut_retail_price"] - data["mazut_base_price"]
    data["mazut_net_bog"] = data["mazut_bog_contribution"] - data["mazut_bog_spending"]
    data["has_mazut_bog"] = data["mazut_bog_contribution"].gt(0) | data["mazut_bog_spending"].gt(0)
    data["mazut_retail_delta"] = data["mazut_retail_price"].diff()
    return data


def _prepare_events(data):
    events = adjustment_rows(data, ["mazut"]).copy()
    events["mazut_retail_delta"] = data.set_index("date")["mazut_retail_price"].diff().reindex(events["date"]).values
    events["abs_delta"] = events["mazut_retail_delta"].abs()
    events["bog_type"] = "Không can thiệp"
    both = events["mazut_bog_contribution"].gt(0) & events["mazut_bog_spending"].gt(0)
    contribution = events["mazut_bog_contribution"].gt(0) & events["mazut_bog_spending"].eq(0)
    spending = events["mazut_bog_spending"].gt(0) & events["mazut_bog_contribution"].eq(0)
    events.loc[contribution, "bog_type"] = "Trích lập"
    events.loc[spending, "bog_type"] = "Chi sử dụng"
    events.loc[both, "bog_type"] = "Vừa trích vừa chi"
    return events.dropna(subset=["mazut_retail_delta"])


def render(df, selected_year, df_full):
    st.markdown(
        """<div style="display:flex;align-items:center;justify-content:space-between;
        border-bottom:2px solid var(--line);padding-bottom:12px;margin-bottom:20px;width:100%;">
        <div style="font-size:30px;font-weight:800;color:var(--brand);letter-spacing:-0.8px;line-height:1.1;">
        Nhiên Liệu Công Nghiệp Mazut
        </div><span style="background:var(--accent);color:#fff;font-size:10px;font-weight:800;
        padding:4px 10px;border-radius:999px;letter-spacing:.5px;text-transform:uppercase;">
        Mazut</span></div>""",
        unsafe_allow_html=True,
    )

    if df.empty:
        st.warning("Không có dữ liệu phù hợp với bộ lọc năm hiện tại.")
        return

    data = _prepare_data(df)
    events = _prepare_events(data)
    latest = data.iloc[-1]
    bog_events = events[events["has_mazut_bog"]]
    bog_rate = len(bog_events) / len(events) * 100 if len(events) else 0
    avg_abs_delta = events["abs_delta"].mean() if not events.empty else 0
    avg_net_bog = events["mazut_net_bog"].mean() if not events.empty else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        _kpi_card(
            "GIÁ MAZUT KỲ CUỐI",
            f"{latest['mazut_retail_price']:,.0f} {MAZUT_UNIT}",
            f"Cập nhật ngày {latest['date']:%d/%m/%Y}",
            sparkline_svg(data["mazut_retail_price"], MAZUT_COLOR, "mazut-retail"),
        )
    with k2:
        _kpi_card(
            "GIÁ CƠ SỞ KỲ CUỐI",
            f"{latest['mazut_base_price']:,.0f} {MAZUT_UNIT}",
            f"Chênh bán lẻ - cơ sở: {latest['mazut_base_retail_gap']:,.0f} {MAZUT_UNIT}",
            sparkline_svg(data["mazut_base_price"], "#4B5694", "mazut-base"),
        )
    with k3:
        _kpi_card(
            "KỲ CÓ CAN THIỆP BOG",
            f"{bog_rate:.1f}%",
            f"{len(bog_events):,}/{len(events):,} kỳ điều chỉnh có BOG",
            progress_svg(bog_rate, MAZUT_COLOR),
        )
    with k4:
        _kpi_card(
            "BIẾN ĐỘNG TB/KỲ",
            f"{avg_abs_delta:,.0f} {MAZUT_UNIT}",
            f"BOG ròng bình quân: {avg_net_bog:,.0f} {MAZUT_UNIT}",
            sparkline_svg(events["abs_delta"] if not events.empty else [], "#7288AE", "mazut-delta"),
        )

    row1_left, row1_right = st.columns([3, 2])
    with row1_left:
        st.markdown("<div class='section-header'>GIÁ CƠ SỞ, GIÁ BÁN LẺ VÀ BOG MAZUT</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.date, y=data["mazut_base_price"], name="Giá cơ sở",
                                 line=dict(color="#9AA9C4", width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=data.date, y=data["mazut_retail_price"], name="Giá bán lẻ",
                                 line=dict(color=MAZUT_COLOR, width=2.4)))
        fig.add_trace(go.Bar(x=events.date, y=events["mazut_bog_contribution"], name="Trích lập BOG",
                             marker_color="#4B5694", opacity=0.55, yaxis="y2"))
        fig.add_trace(go.Bar(x=events.date, y=events["mazut_bog_spending"], name="Chi sử dụng BOG",
                             marker_color="#C1B49A", opacity=0.65, yaxis="y2"))
        fig.update_layout(
            height=320,
            plot_bgcolor="white",
            paper_bgcolor="white",
            hovermode="x unified",
            barmode="group",
            yaxis=dict(title=MAZUT_UNIT),
            yaxis2=dict(title=f"BOG ({MAZUT_UNIT})", overlaying="y", side="right", rangemode="tozero"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=52, r=55, t=48, b=35),
        )
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with row1_right:
        st.markdown("<div class='section-header'>CƠ CẤU CAN THIỆP BOG THEO NĂM</div>", unsafe_allow_html=True)
        bog_mix = (
            events.assign(Năm=events["date"].dt.year.astype(str))
            .groupby(["Năm", "bog_type"])
            .size()
            .unstack(fill_value=0)
        )
        if bog_mix.empty:
            st.info("Không có dữ liệu BOG theo kỳ điều chỉnh.")
        else:
            colors = {
                "Không can thiệp": "#CBD5E1",
                "Trích lập": "#4B5694",
                "Chi sử dụng": "#C1B49A",
                "Vừa trích vừa chi": "#0B1849",
            }
            fig = go.Figure()
            for label, color in colors.items():
                values = bog_mix[label] if label in bog_mix else [0] * len(bog_mix)
                fig.add_trace(go.Bar(x=bog_mix.index, y=values, name=label, marker_color=color))
            fig.update_layout(
                height=320,
                barmode="stack",
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis=dict(title="Số kỳ", rangemode="tozero"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                margin=dict(l=45, r=20, t=48, b=45),
            )
            style_figure(fig)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    row2_left, row2_right = st.columns([2, 3])
    with row2_left:
        st.markdown("<div class='section-header'>NHỊP ĐIỀU CHỈNH MAZUT THEO NĂM</div>", unsafe_allow_html=True)
        annual = (
            events.assign(Năm=events["date"].dt.year.astype(str))
            .groupby("Năm", as_index=False)
            .agg(**{"Số kỳ": ("date", "size"), "Biến động TB": ("abs_delta", "mean")})
        )
        if annual.empty:
            st.info("Không đủ dữ liệu kỳ điều chỉnh để tổng hợp theo năm.")
        else:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=annual["Năm"], y=annual["Số kỳ"], name="Số kỳ",
                                 marker_color=MUTED_COLOR, text=annual["Số kỳ"], textposition="outside"))
            fig.add_trace(go.Scatter(x=annual["Năm"], y=annual["Biến động TB"], name="Biến động TB",
                                     mode="lines+markers", yaxis="y2",
                                     line=dict(color=MAZUT_COLOR, width=2.2),
                                     marker=dict(color=MAZUT_COLOR, size=7)))
            fig.update_layout(
                height=315,
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis=dict(title="Số kỳ", rangemode="tozero"),
                yaxis2=dict(title=MAZUT_UNIT, overlaying="y", side="right", rangemode="tozero"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                margin=dict(l=45, r=55, t=48, b=45),
            )
            style_figure(fig)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with row2_right:
        st.markdown("<div class='section-header'>10 KỲ ĐIỀU CHỈNH MAZUT MẠNH NHẤT</div>", unsafe_allow_html=True)
        strongest = events.nlargest(10, "abs_delta").sort_values("abs_delta")
        if strongest.empty:
            st.info("Không đủ dữ liệu để xác định kỳ điều chỉnh mạnh nhất.")
        else:
            labels = strongest["date"].dt.strftime("%d/%m/%Y")
            colors = [BRAND_COLOR if value > 0 else BLUE_SOFT_COLOR for value in strongest["mazut_retail_delta"]]
            fig = go.Figure(
                go.Bar(
                    x=strongest["mazut_retail_delta"],
                    y=labels,
                    orientation="h",
                    marker_color=colors,
                    text=[f"{v:+,.0f}" for v in strongest["mazut_retail_delta"]],
                    textposition="outside",
                    customdata=strongest[["bog_type", "mazut_bog_contribution", "mazut_bog_spending"]],
                    hovertemplate=(
                        "Ngày %{y}<br>Thay đổi: %{x:+,.0f} " + MAZUT_UNIT
                        + "<br>BOG: %{customdata[0]}"
                        + "<br>Trích lập: %{customdata[1]:,.0f}"
                        + "<br>Chi sử dụng: %{customdata[2]:,.0f}<extra></extra>"
                    ),
                )
            )
            fig.add_vline(x=0, line_color=BRAND_COLOR, line_width=1)
            fig.update_layout(
                height=315,
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis_title=f"Thay đổi giá bán lẻ ({MAZUT_UNIT})",
                margin=dict(l=75, r=35, t=35, b=45),
            )
            style_figure(fig, show_legend=False, keep_zero_line=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div class='section-header'>MAZUT SO VỚI TRUNG BÌNH NHÓM NHIÊN LIỆU GIAO THÔNG</div>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data.date,
            y=data["transport_avg_retail_price"],
            name="TB RON95/E5/Diesel",
            line=dict(color="#4B5694", width=2.1, dash="dot"),
            hovertemplate="Ngày %{x|%d/%m/%Y}<br>TB giao thông: %{y:,.0f} đ/lít<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data.date,
            y=data["mazut_retail_price"],
            name="Mazut",
            line=dict(color=MAZUT_COLOR, width=2.6),
            hovertemplate="Ngày %{x|%d/%m/%Y}<br>Mazut: %{y:,.0f} " + MAZUT_UNIT + "<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data.date,
            y=data["mazut_transport_gap"],
            name="Chênh Mazut - TB giao thông",
            fill="tozeroy",
            yaxis="y2",
            line=dict(color="#7288AE", width=1.6),
            opacity=0.35,
            hovertemplate="Ngày %{x|%d/%m/%Y}<br>Chênh lệch: %{y:,.0f}<extra></extra>",
        )
    )
    fig.add_shape(
        type="line",
        x0=0,
        x1=1,
        xref="paper",
        y0=0,
        y1=0,
        yref="y2",
        line=dict(color="#94A3B8", dash="dash"),
    )
    fig.update_layout(
        height=300,
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
        yaxis=dict(title="Giá ghi nhận"),
        yaxis2=dict(title="Chênh lệch", overlaying="y", side="right", zeroline=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=52, r=58, t=48, b=35),
    )
    style_figure(fig, keep_zero_line=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with st.expander("Xem dữ liệu mazut theo bộ lọc"):
        table = data[
            [
                "date",
                "mazut_base_price",
                "mazut_retail_price",
                "mazut_retail_delta",
                "mazut_bog_contribution",
                "mazut_bog_spending",
                "mazut_net_bog",
                "mazut_base_retail_gap",
            ]
        ].rename(
            columns={
                "date": "Ngày",
                "mazut_base_price": "Giá cơ sở mazut",
                "mazut_retail_price": "Giá bán lẻ mazut",
                "mazut_retail_delta": "Thay đổi giá bán lẻ",
                "mazut_bog_contribution": "Trích lập BOG mazut",
                "mazut_bog_spending": "Chi BOG mazut",
                "mazut_net_bog": "BOG ròng",
                "mazut_base_retail_gap": "Chênh bán lẻ - cơ sở",
            }
        )
        st.dataframe(table, use_container_width=True, hide_index=True)
