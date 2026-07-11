import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from tqh_cuoiki.dashboard_utils import FUEL_META, adjustment_rows, period_change, progress_svg, sparkline_svg, style_figure


COLORS = {"Xăng RON 95": "#0B1849", "Xăng E5 RON 92": "#4B5694", "Dầu Diesel": "#7288AE"}


def _card(title, value, note, visual=""):
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-title">{title}</div>'
        f'<div class="kpi-value">{value}</div><div style="margin:6px 0">{visual}</div>'
        f'<div class="kpi-trend">{note}</div></div>',
        unsafe_allow_html=True,
    )


def render(df, selected_fuels):
    data = df.sort_values("date").copy()
    start, end = data["date"].iloc[0], data["date"].iloc[-1]
    prefixes = [FUEL_META[f][0] for f in selected_fuels]

    st.markdown('<div class="hero-title">Tổng Quan Thị Trường</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hero-subtitle">Giai đoạn được chọn: {start:%d/%m/%Y} - {end:%d/%m/%Y}</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(2 + len(selected_fuels))
    with cols[0]:
        completeness = len(data) / ((end - start).days + 1) * 100
        _card("SỐ NGÀY TRONG KỲ", f"{len(data):,}", f"Đủ {completeness:.1f}% ngày lịch", progress_svg(completeness))
    with cols[1]:
        ch = period_change(data["brent_usd_per_barrel"])
        _card("BRENT TRUNG BÌNH", f"${data['brent_usd_per_barrel'].mean():.2f}/thùng", f"Thay đổi trong kỳ: {ch:+.1f}%",
              sparkline_svg(data["brent_usd_per_barrel"], "#0B1849", "overview-brent"))
    for col, fuel in zip(cols[2:], selected_fuels):
        prefix, unit = FUEL_META[fuel]
        ch = period_change(data[f"{prefix}_retail_price"])
        with col:
            _card(f"{fuel.upper()} TRUNG BÌNH", f"{data[f'{prefix}_retail_price'].mean():,.0f} {unit}", f"Thay đổi trong kỳ: {ch:+.1f}%",
                  sparkline_svg(data[f"{prefix}_retail_price"], COLORS[fuel], f"overview-{prefix}"))

    st.markdown("<div class='section-header'>DIỄN BIẾN GIÁ BÁN LẺ GHI NHẬN</div>", unsafe_allow_html=True)
    fig = go.Figure()
    for fuel in selected_fuels:
        prefix, unit = FUEL_META[fuel]
        fig.add_trace(go.Scatter(x=data["date"], y=data[f"{prefix}_retail_price"], name=fuel,
                                 line=dict(color=COLORS[fuel], width=2)))
    fig.update_layout(height=270, hovermode="x unified", plot_bgcolor="white", paper_bgcolor="white",
                      yaxis_title="đ/lít", xaxis_title=None, legend=dict(orientation="h"))
    style_figure(fig)
    st.plotly_chart(fig, width="stretch")

    left, right = st.columns([1, 2.15])
    with left:
        st.markdown("<div class='section-header'>PHÂN PHỐI GIÁ THEO NGÀY</div>", unsafe_allow_html=True)
        long = pd.concat([
            pd.DataFrame({"Nhiên liệu": fuel, "Giá": data[f"{FUEL_META[fuel][0]}_retail_price"]})
            for fuel in selected_fuels
        ], ignore_index=True)
        box = px.box(long, x="Nhiên liệu", y="Giá", color="Nhiên liệu", points=False,
                     color_discrete_map=COLORS)
        box.update_layout(height=235, showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                          xaxis_title=None, yaxis_title="đ/lít")
        style_figure(box, show_legend=False)
        st.plotly_chart(box, width="stretch")

    with right:
        group_by_year = data["date"].dt.year.nunique() > 1
        period_label = "Năm" if group_by_year else "Tháng"
        st.markdown(
            f"<div class='section-header'>MỨC THAY ĐỔI TRUNG BÌNH THEO {period_label.upper()}</div>",
            unsafe_allow_html=True,
        )
        adj = adjustment_rows(data, prefixes)
        delta_long = []
        full = data.set_index("date")
        for fuel in selected_fuels:
            prefix, _ = FUEL_META[fuel]
            delta = full[f"{prefix}_retail_price"].diff().reindex(adj["date"]).values
            delta_long.append(pd.DataFrame({"Ngày": adj["date"], "Nhiên liệu": fuel, "Thay đổi": delta}))
        delta_long = pd.concat(delta_long, ignore_index=True).dropna()
        if group_by_year:
            delta_long["Giai đoạn"] = delta_long["Ngày"].dt.year.astype(str)
        else:
            delta_long["Giai đoạn"] = delta_long["Ngày"].dt.strftime("%m/%Y")
        summary = (
            delta_long.assign(**{"Mức thay đổi tuyệt đối": delta_long["Thay đổi"].abs()})
            .groupby(["Giai đoạn", "Nhiên liệu"], as_index=False)
            .agg(**{"Mức thay đổi trung bình": ("Mức thay đổi tuyệt đối", "mean"), "Số kỳ": ("Thay đổi", "size")})
        )
        bars = px.line(
            summary,
            x="Giai đoạn",
            y="Mức thay đổi trung bình",
            color="Nhiên liệu",
            markers=True,
            color_discrete_map=COLORS,
            custom_data=["Số kỳ"],
        )
        bars.update_traces(
            line=dict(width=2.2),
            marker=dict(size=7),
            hovertemplate="%{fullData.name}<br>Giai đoạn: %{x}<br>Thay đổi TB: %{y:,.0f} đ/lít"
                          "<br>Số kỳ: %{customdata[0]}<extra></extra>",
        )
        bars.update_layout(
            height=255, plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title=None, type="category", showgrid=False),
            yaxis=dict(title="Mức thay đổi trung bình (đ/lít)", rangemode="tozero", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=55, r=20, t=42, b=35),
        )
        style_figure(bars)
        st.plotly_chart(bars, width="stretch", config={"displayModeBar": False})

    macro_col, relation_col = st.columns([3, 2])
    with macro_col:
        st.markdown("<div class='section-header'>GIÁ BRENT QUY ĐỔI VÀ TỶ GIÁ USD/VND</div>", unsafe_allow_html=True)
        data["brent_vnd_liter"] = data["brent_usd_per_barrel"] * data["usd_vnd"] / 158.987
        macro = go.Figure()
        macro.add_trace(go.Scatter(x=data["date"], y=data["brent_vnd_liter"], name="Brent quy đổi (đ/lít)"))
        macro.add_trace(go.Scatter(x=data["date"], y=data["usd_vnd"], name="USD/VND", yaxis="y2"))
        macro.update_layout(height=245, plot_bgcolor="white", paper_bgcolor="white", hovermode="x unified",
                            yaxis=dict(title="Brent quy đổi (đ/lít)"),
                            yaxis2=dict(title="VND/USD", overlaying="y", side="right"),
                            legend=dict(orientation="h", y=1.12), margin=dict(t=35, b=30))
        style_figure(macro)
        st.plotly_chart(macro, width="stretch", config={"displayModeBar": False})

    with relation_col:
        st.markdown("<div class='section-header'>MỐI LIÊN HỆ GIỮA BRENT VÀ GIÁ BÁN LẺ</div>", unsafe_allow_html=True)
        relation = go.Figure()
        relation_styles = {
            "Xăng RON 95": ("#0B1849", "circle"),
            "Xăng E5 RON 92": ("#4B5694", "diamond"),
            "Dầu Diesel": ("#9AA9C4", "square"),
        }
        for fuel in selected_fuels:
            p, _ = FUEL_META[fuel]
            fuel_events = adjustment_rows(data, [p]).sort_values("date")
            x = fuel_events["brent_usd_per_barrel"].pct_change() * 100
            y = fuel_events[f"{p}_retail_price"].pct_change() * 100
            valid = x.notna() & y.notna()
            marker_color, marker_symbol = relation_styles[fuel]
            relation.add_trace(go.Scatter(
                x=x[valid], y=y[valid], mode="markers", name=fuel,
                marker=dict(color=marker_color, symbol=marker_symbol, size=7, opacity=0.62,
                            line=dict(color="#FFFFFF", width=0.5)),
                hovertemplate=f"{fuel}<br>Brent: %{{x:+.2f}}%<br>Giá bán lẻ: %{{y:+.2f}}%<extra></extra>",
            ))
        relation.update_layout(
            height=245, plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title="Brent giữa hai kỳ (%)", showgrid=False, zeroline=False),
            yaxis=dict(title="Giá bán lẻ giữa hai kỳ (%)", showgrid=False, zeroline=False),
            legend=dict(orientation="h", y=1.2), margin=dict(t=48, b=40, l=48, r=15),
        )
        style_figure(relation)
        st.plotly_chart(relation, width="stretch", config={"displayModeBar": False})

    with st.expander("Xem dữ liệu theo bộ lọc"):
        columns = ["date", "usd_vnd", "brent_usd_per_barrel"] + [f"{p}_retail_price" for p in prefixes]
        st.dataframe(data[columns], width="stretch", hide_index=True)