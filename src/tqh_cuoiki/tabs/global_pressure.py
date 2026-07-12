import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from tqh_cuoiki.dashboard_utils import (
    FUEL_META,
    adjustment_rows,
    period_change,
    progress_svg,
    sparkline_svg,
    style_figure,
)


COLORS = {
    "Xăng RON 95": "#0B1849",
    "Xăng E5 RON 92": "#4B5694",
    "Dầu Diesel": "#7288AE",
}

GLOBAL_COLORS = {
    "Brent": "#C1B49A",
    "USD/VND": "#9AA9C4",
}


def _kpi_card(title, value, note, visual=""):
    st.markdown(
        f'<div class="kpi-card"><div><div class="kpi-title">{title}</div>'
        f'<div class="kpi-value">{value}</div></div><div style="margin:6px 0">{visual}</div>'
        f'<div class="kpi-trend">{note}</div></div>',
        unsafe_allow_html=True,
    )


def _indexed(series):
    valid = series.dropna()

    if valid.empty or valid.iloc[0] == 0:
        return pd.Series(index=series.index, dtype=float)

    return series / valid.iloc[0] * 100


def _structure_table(data, selected_fuels):
    annual = (
        data.assign(Năm=data["date"].dt.year)
        .groupby("Năm", as_index=False)[
            [
                f"{FUEL_META[f][0]}_retail_price"
                for f in selected_fuels
            ]
        ]
        .mean()
    )

    rows = []

    for _, row in annual.iterrows():
        prices = {
            fuel: row[
                f"{FUEL_META[fuel][0]}_retail_price"
            ]
            for fuel in selected_fuels
        }

        market_mean = pd.Series(prices).mean()

        for fuel, price in prices.items():
            rows.append(
                {
                    "Năm": str(int(row["Năm"])),
                    "Nhiên liệu": fuel,
                    "Giá trung bình": price,
                    "Chỉ số giá tương đối": (
                        price / market_mean * 100
                    ),
                }
            )

    return pd.DataFrame(rows)


def render(df, selected_fuels, selected_year, df_full):
    st.markdown(
    """<div style="display:flex;align-items:center;justify-content:space-between;
    border-bottom:2px solid var(--line);padding-bottom:12px;margin-bottom:20px;width:100%;">
    <div style="font-size:30px;font-weight:800;color:var(--brand);letter-spacing:-0.8px;line-height:1.1;">
    Sức Ép Toàn Cầu 
    <span style="font-weight:800;">
    ảnh hưởng đến Cấu Trúc Giá Bán Lẻ Nhiên Liệu
    </span>
    </div>
    <span style="background:var(--brand);color:#fff;font-size:10px;font-weight:800;
    padding:4px 10px;border-radius:999px;letter-spacing:.5px;text-transform:uppercase;">
    Thị trường toàn cầu
    </span>
    </div>""",
    unsafe_allow_html=True,
    )

    data = df.sort_values("date").copy()
    full = df_full.sort_values("date").copy()

    if data.empty or not selected_fuels:
        st.warning(
            "Không có dữ liệu phù hợp với bộ lọc hiện tại."
        )
        return

    prefixes = [
        FUEL_META[fuel][0]
        for fuel in selected_fuels
    ]

    start = data["date"].iloc[0]
    end = data["date"].iloc[-1]

    expected_days = (end - start).days + 1

    coverage = (
        len(data) / expected_days * 100
        if expected_days > 0
        else 0
    )

    events = adjustment_rows(
        data,
        prefixes,
    ).sort_values("date")

    corr_rows = []

    if len(events) > 1:
        brent_change = (
            events["brent_usd_per_barrel"]
            .pct_change()
        )

        usd_change = (
            events["usd_vnd"]
            .pct_change()
        )

        for fuel in selected_fuels:
            prefix, _ = FUEL_META[fuel]

            retail_change = (
                events[
                    f"{prefix}_retail_price"
                ]
                .pct_change()
            )

            corr_rows.append(
                {
                    "Nhiên liệu": fuel,
                    "Brent": retail_change.corr(
                        brent_change
                    ),
                    "USD/VND": retail_change.corr(
                        usd_change
                    ),
                }
            )

    corr_df = pd.DataFrame(corr_rows)

    strongest_fuel = "-"
    strongest_corr = 0.0

    if (
        not corr_df.empty
        and corr_df["Brent"].notna().any()
    ):
        strongest_idx = (
            corr_df["Brent"]
            .abs()
            .idxmax()
        )

        strongest_fuel = corr_df.loc[
            strongest_idx,
            "Nhiên liệu",
        ]

        strongest_corr = corr_df.loc[
            strongest_idx,
            "Brent",
        ]

    structure_full = _structure_table(
        full,
        selected_fuels,
    )

    shift_fuel = "-"
    shift_range = 0.0

    if (
        len(selected_fuels) > 1
        and not structure_full.empty
    ):
        structure_range = (
            structure_full
            .groupby("Nhiên liệu")[
                "Chỉ số giá tương đối"
            ]
            .agg(
                lambda series: (
                    series.max() - series.min()
                )
            )
        )

        if not structure_range.empty:
            shift_fuel = structure_range.idxmax()
            shift_range = structure_range.max()

    # =========================================================
    # KPI
    # =========================================================

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        _kpi_card(
            "SỐ NGÀY DỮ LIỆU",
            f"{len(data):,}",
            f"Độ phủ ngày: {coverage:.1f}%",
            progress_svg(coverage),
        )

    with k2:
        brent_change_value = period_change(
            data["brent_usd_per_barrel"]
        )

        _kpi_card(
            "BRENT TRUNG BÌNH",
            (
                f"${data['brent_usd_per_barrel'].mean():.2f}"
                "/thùng"
            ),
            (
                "Thay đổi trong kỳ: "
                f"{brent_change_value:+.1f}%"
            ),
            sparkline_svg(
                data["brent_usd_per_barrel"],
                GLOBAL_COLORS["Brent"],
                "gp-brent",
            ),
        )

    with k3:
        usd_change_value = period_change(
            data["usd_vnd"]
        )

        _kpi_card(
            "USD/VND TRUNG BÌNH",
            f"{data['usd_vnd'].mean():,.0f}",
            (
                "Thay đổi trong kỳ: "
                f"{usd_change_value:+.1f}%"
            ),
            sparkline_svg(
                data["usd_vnd"],
                GLOBAL_COLORS["USD/VND"],
                "gp-usd",
            ),
        )

    with k4:
        _kpi_card(
            "GẮN KẾT BRENT RÕ NHẤT",
            strongest_fuel,
            (
                "Tương quan thay đổi: "
                f"{strongest_corr:+.2f}"
            ),
            progress_svg(
                min(
                    abs(strongest_corr) * 100,
                    100,
                )
            ),
        )

    with k5:
        visual = ""

        if shift_fuel != "-":
            shift_series = (
                structure_full[
                    structure_full[
                        "Nhiên liệu"
                    ].eq(shift_fuel)
                ]
                .sort_values("Năm")[
                    "Chỉ số giá tương đối"
                ]
            )

            visual = sparkline_svg(
                shift_series,
                COLORS[shift_fuel],
                "gp-structure-shift",
            )

        _kpi_card(
            "DỊCH CHUYỂN CẤU TRÚC LỚN NHẤT",
            shift_fuel,
            (
                "Biên độ vị thế giá: "
                f"{shift_range:.1f} điểm"
            ),
            visual,
        )

    # =========================================================
    # BIỂU ĐỒ 1
    # =========================================================

    st.markdown(
        "<div class='section-header'>"
        "CHỈ SỐ BIẾN ĐỘNG TOÀN CẦU VÀ GIÁ BÁN LẺ "
        "(MỐC ĐẦU KỲ = 100)"
        "</div>",
        unsafe_allow_html=True,
    )

    monthly = (
        data
        .set_index("date")[
            [
                "brent_usd_per_barrel",
                "usd_vnd",
            ]
            + [
                f"{prefix}_retail_price"
                for prefix in prefixes
            ]
        ]
        .resample("MS")
        .mean()
        .dropna(how="all")
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly["date"],
            y=_indexed(
                monthly[
                    "brent_usd_per_barrel"
                ]
            ),
            name="Brent",
            line=dict(
                color=GLOBAL_COLORS["Brent"],
                width=2.2,
                dash="dash",
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=monthly["date"],
            y=_indexed(
                monthly["usd_vnd"]
            ),
            name="USD/VND",
            line=dict(
                color=GLOBAL_COLORS["USD/VND"],
                width=2.2,
                dash="dot",
            ),
        )
    )

    for fuel in selected_fuels:
        prefix, _ = FUEL_META[fuel]

        fig.add_trace(
            go.Scatter(
                x=monthly["date"],
                y=_indexed(
                    monthly[
                        f"{prefix}_retail_price"
                    ]
                ),
                name=fuel,
                line=dict(
                    color=COLORS[fuel],
                    width=2.4,
                ),
            )
        )

    fig.add_hline(
        y=100,
        line_color="#D7DFEB",
        line_dash="dot",
    )

    fig.update_layout(
        height=320,
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(
            title="Chỉ số (đầu kỳ = 100)",
            showgrid=False,
        ),
        xaxis=dict(
            title=None,
            showgrid=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        margin=dict(
            l=58,
            r=25,
            t=48,
            b=38,
        ),
    )

    style_figure(fig)

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displayModeBar": False
        },
    )

    # =========================================================
    # BIỂU ĐỒ 2 + 3
    # =========================================================

    row1_left, row1_right = st.columns(
        [4, 6]
    )

    # =========================================================
    # BIỂU ĐỒ 2
    # =========================================================

    with row1_left:
        st.markdown(
            "<div class='section-header'>"
            "TƯƠNG QUAN THAY ĐỔI GIỮA "
            "SỨC ÉP TOÀN CẦU VÀ GIÁ BÁN LẺ"
            "</div>",
            unsafe_allow_html=True,
        )

        if corr_df.empty:
            st.info(
                "Chưa đủ dữ liệu để tính tương quan "
                "trong phạm vi bộ lọc."
            )

        else:
            z = (
                corr_df[
                    ["Brent", "USD/VND"]
                ]
                .fillna(0)
                .values
            )

            fig = go.Figure(
                go.Heatmap(
                    z=z,
                    x=[
                        "Brent",
                        "USD/VND",
                    ],
                    y=corr_df["Nhiên liệu"],
                    zmin=-1,
                    zmax=1,
                    zmid=0,
                    colorscale=[
                        [0.00, "#C1B49A"],
                        [0.50, "#FFFFFF"],
                        [0.72, "#D7DFEB"],
                        [1.00, "#0B1849"],
                    ],
                    text=[
                        [
                            f"{value:+.2f}"
                            for value in row
                        ]
                        for row in z
                    ],
                    texttemplate="%{text}",
                    hovertemplate=(
                        "%{y}<br>"
                        "%{x}: %{z:+.3f}"
                        "<extra></extra>"
                    ),
                    colorbar=dict(
                        title="r",
                        thickness=10,
                    ),
                )
            )

            fig.update_layout(
                height=270,
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(
                    title=None,
                    side="top",
                ),
                yaxis=dict(
                    title=None,
                ),
                margin=dict(
                    l=95,
                    r=20,
                    t=55,
                    b=25,
                ),
            )

            style_figure(
                fig,
                show_legend=False,
            )

            st.plotly_chart(
                fig,
                width="stretch",
                config={
                    "displayModeBar": False
                },
            )

    # =========================================================
    # BIỂU ĐỒ 3
    # =========================================================

    with row1_right:
        st.markdown(
            "<div class='section-header'>"
            "CẤU TRÚC GIÁ TƯƠNG ĐỐI THEO NĂM"
            "</div>",
            unsafe_allow_html=True,
        )

        if len(selected_fuels) <= 1:
            st.info(
                "Chọn từ 2 nhóm nhiên liệu trở lên "
                "để xem cấu trúc giá tương đối."
            )

        else:
            heat = (
                structure_full
                .pivot(
                    index="Nhiên liệu",
                    columns="Năm",
                    values=(
                        "Chỉ số giá tương đối"
                    ),
                )
                .reindex(selected_fuels)
            )

            z = heat.values

            fig = go.Figure(
                go.Heatmap(
                    z=z,
                    x=heat.columns.tolist(),
                    y=heat.index.tolist(),
                    zmid=100,
                    colorscale=[
                        [0.00, "#D7DFEB"],
                        [0.48, "#F7F8FB"],
                        [0.50, "#FFFFFF"],
                        [0.72, "#7288AE"],
                        [1.00, "#0B1849"],
                    ],
                    text=[
                        [
                            f"{value:.1f}"
                            for value in row
                        ]
                        for row in z
                    ],
                    texttemplate="%{text}",
                    hovertemplate=(
                        "%{y}<br>"
                        "Năm %{x}<br>"
                        "Chỉ số giá tương đối: "
                        "%{z:.1f}"
                        "<extra></extra>"
                    ),
                    colorbar=dict(
                        title="Chỉ số",
                        thickness=10,
                    ),
                )
            )

            fig.update_layout(
                height=270,
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(
                    title=None,
                    type="category",
                    side="top",
                ),
                yaxis=dict(
                    title=None,
                ),
                margin=dict(
                    l=105,
                    r=25,
                    t=58,
                    b=25,
                ),
            )

            style_figure(
                fig,
                show_legend=False,
            )

            st.plotly_chart(
                fig,
                width="stretch",
                config={
                    "displayModeBar": False
                },
            )

    # =========================================================
    # BIỂU ĐỒ 4 + 5
    # =========================================================

    row2_left, row2_right = st.columns(2)

    # =========================================================
    # BIỂU ĐỒ 4
    # =========================================================

    with row2_left:
        st.markdown(
            "<div class='section-header'>"
            "THỨ HẠNG GIÁ BÁN LẺ TRUNG BÌNH THEO NĂM "
            "GIỮA CÁC NHÓM NHIÊN LIỆU"
            "</div>",
            unsafe_allow_html=True,
        )

        if len(selected_fuels) <= 1:
            st.info(
                "Chọn từ 2 nhóm nhiên liệu trở lên "
                "để xem thứ hạng giá."
            )
        else:
            rank_data = structure_full.copy()

            rank_data["Thứ hạng"] = (
                rank_data
                .groupby("Năm")["Giá trung bình"]
                .rank(
                    method="min",
                    ascending=False,
                )
            )

            years = sorted(
                rank_data["Năm"].unique()
            )

            year_positions = {
                year: index
                for index, year in enumerate(years)
            }

            # Dịch riêng năm cuối sang phải
            year_positions[years[-1]] += 1.5

            fig = go.Figure()

            for fuel in selected_fuels:
                fuel_rank = (
                    rank_data[
                        rank_data["Nhiên liệu"].eq(fuel)
                    ]
                    .sort_values("Năm")
                )

                x_positions = [
                    year_positions[year]
                    for year in fuel_rank["Năm"]
                ]

                custom_data = [
                    [
                        year,
                        price,
                    ]
                    for year, price in zip(
                        fuel_rank["Năm"],
                        fuel_rank["Giá trung bình"],
                    )
                ]

                fig.add_trace(
                    go.Scatter(
                        x=x_positions,
                        y=fuel_rank["Thứ hạng"],
                        mode="lines+markers+text",
                        name=fuel,
                        line=dict(
                            color=COLORS[fuel],
                            width=2.4,
                        ),
                        marker=dict(
                            size=8,
                        ),
                        text=[
                            f"{price:,.0f}"
                            for price in fuel_rank[
                                "Giá trung bình"
                            ]
                        ],
                        textposition="top center",
                        textfont=dict(
                            size=9,
                            color=COLORS[fuel],
                        ),
                        cliponaxis=False,
                        customdata=custom_data,
                        hovertemplate=(
                            f"{fuel}<br>"
                            "Năm %{customdata[0]}<br>"
                            "Thứ hạng: %{y:.0f}<br>"
                            "Giá trung bình: "
                            "%{customdata[1]:,.0f} đ/lít"
                            "<extra></extra>"
                        ),
                    )
                )

            fig.update_layout(
                height=290,
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(
                    title=None,
                    tickmode="array",
                    tickvals=[
                        year_positions[year]
                        for year in years
                    ],
                    ticktext=[
                        str(year)
                        for year in years
                    ],
                    range=[
                        -0.45,
                        year_positions[years[-1]] + 0.45,
                    ],
                    showgrid=False,
                ),
                yaxis=dict(
                    title="Thứ hạng giá",
                    autorange="reversed",
                    tickmode="linear",
                    dtick=1,
                    range=[
                        len(selected_fuels) + 0.35,
                        0.65,
                    ],
                    showgrid=False,
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=0,
                ),
                margin=dict(
                    l=55,
                    r=35,
                    t=48,
                    b=35,
                ),
            )

            style_figure(fig)

            st.plotly_chart(
                fig,
                width="stretch",
                config={
                    "displayModeBar": False
                },
            ) 
    # =========================================================
    # BIỂU ĐỒ 5
    # =========================================================

    with row2_right:
        st.markdown(
            "<div class='section-header'>"
            "CẤU TRÚC GIÁ KHI BRENT THẤP VÀ CAO"
            "</div>",
            unsafe_allow_html=True,
        )

        if len(selected_fuels) <= 1:
            st.info(
                "Chọn từ 2 nhóm nhiên liệu trở lên "
                "để so sánh cấu trúc giá theo trạng thái Brent."
            )
        else:
            price_cols = [
                f"{FUEL_META[fuel][0]}_retail_price"
                for fuel in selected_fuels
            ]

            monthly_pressure = (
                data
                .set_index("date")[
                    ["brent_usd_per_barrel"] + price_cols
                ]
                .resample("MS")
                .mean()
                .dropna()
                .reset_index()
            )

            q25 = monthly_pressure[
                "brent_usd_per_barrel"
            ].quantile(0.25)

            q75 = monthly_pressure[
                "brent_usd_per_barrel"
            ].quantile(0.75)

            monthly_pressure["Giá trung bình nhóm"] = (
                monthly_pressure[price_cols]
                .mean(axis=1)
            )

            for fuel in selected_fuels:
                prefix, _ = FUEL_META[fuel]

                monthly_pressure[
                    f"{prefix}_relative_price"
                ] = (
                    monthly_pressure[
                        f"{prefix}_retail_price"
                    ]
                    / monthly_pressure[
                        "Giá trung bình nhóm"
                    ]
                    * 100
                )

            low_brent = monthly_pressure[
                monthly_pressure[
                    "brent_usd_per_barrel"
                ] <= q25
            ]

            high_brent = monthly_pressure[
                monthly_pressure[
                    "brent_usd_per_barrel"
                ] >= q75
            ]

            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    color:#4B5694;
                    font-size:11px;
                    margin-top:-2px;
                    margin-bottom:4px;
                ">
                    Brent thấp ≤ ${q25:.2f}/thùng
                    &nbsp;&nbsp; | &nbsp;&nbsp;
                    Brent cao ≥ ${q75:.2f}/thùng
                </div>
                """,
                unsafe_allow_html=True,
            )

            fig = go.Figure()

            for fuel in selected_fuels:
                prefix, _ = FUEL_META[fuel]

                low_value = low_brent[
                    f"{prefix}_relative_price"
                ].mean()

                high_value = high_brent[
                    f"{prefix}_relative_price"
                ].mean()

                fig.add_trace(
                    go.Scatter(
                        x=[
                            "Brent thấp",
                            "Brent cao",
                        ],
                        y=[
                            low_value,
                            high_value,
                        ],
                        mode="lines+markers+text",
                        name=fuel,
                        line=dict(
                            color=COLORS[fuel],
                            width=2.4,
                        ),
                        marker=dict(
                            size=9,
                        ),
                        text=[
                            f"{low_value:.1f}",
                            f"{high_value:.1f}",
                        ],
                        textposition=[
                            "top center",
                            "top center",
                        ],
                        textfont=dict(
                            size=10,
                            color=COLORS[fuel],
                        ),
                        cliponaxis=False,
                        hovertemplate=(
                            f"{fuel}<br>"
                            "%{x}<br>"
                            "Chỉ số giá tương đối: %{y:.1f}"
                            "<extra></extra>"
                        ),
                    )
                )

            fig.add_hline(
                y=100,
                line_color="#D7DFEB",
                line_dash="dot",
            )

            fig.update_layout(
                height=290,
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(
                    title=None,
                    type="category",
                    showgrid=False,
                ),
                yaxis=dict(
                    title="Chỉ số giá tương đối",
                    showgrid=False,
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=0,
                ),
                margin=dict(
                    l=55,
                    r=60,
                    t=48,
                    b=35,
                ),
            )

            style_figure(
                fig,
                keep_zero_line=True,
            )

            st.plotly_chart(
                fig,
                width="stretch",
                config={
                    "displayModeBar": False
                },
            )
    # =========================================================
    # DATA TABLE
    # =========================================================

    with st.expander(
        "Xem dữ liệu sức ép toàn cầu theo bộ lọc"
    ):
        columns = [
            "date",
            "usd_vnd",
            "brent_usd_per_barrel",
        ] + [
            f"{prefix}_retail_price"
            for prefix in prefixes
        ]

        st.dataframe(
            data[columns],
            width="stretch",
            hide_index=True,
        )