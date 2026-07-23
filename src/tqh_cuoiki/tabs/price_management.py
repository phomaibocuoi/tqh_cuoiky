import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from tqh_cuoiki.dashboard_utils import FUEL_META, adjustment_rows, progress_svg, sparkline_svg, style_figure


COLORS = {"Xăng RON 95": "#0B1849", "Xăng E5 RON 92": "#4B5694", "Dầu Diesel": "#7288AE"}


def _kpi_card(title, value, note, visual):
    st.markdown(
        f'<div class="kpi-card"><div><div class="kpi-title">{title}</div>'
        f'<div class="kpi-value">{value}</div></div><div style="margin:6px 0">{visual}</div>'
        f'<div class="kpi-trend">{note}</div></div>', unsafe_allow_html=True,
    )


def render(df, selected_fuels, selected_year, df_full):
    st.markdown(
        """<div style="display:flex;align-items:center;justify-content:space-between;
        border-bottom:2px solid var(--line);padding-bottom:12px;margin-bottom:20px;width:100%;">
        <div style="font-size:30px;font-weight:800;color:var(--brand);letter-spacing:-0.8px;line-height:1.1;">
        Cơ Chế <span style="color:var(--muted);font-weight:300;">Điều Hành và Điều Tiết Giá Xăng Dầu</span>
        </div><span style="background:var(--brand);color:#fff;font-size:10px;font-weight:800;
        padding:4px 10px;border-radius:999px;letter-spacing:.5px;text-transform:uppercase;">
        Cơ chế điều hành giá</span></div>""", unsafe_allow_html=True,
    )

    data = df.sort_values("date").copy()
    if data.empty or not selected_fuels:
        st.warning("Không có dữ liệu phù hợp với bộ lọc hiện tại.")
        return

    primary_fuel = selected_fuels[0]
    prefix, unit = FUEL_META[primary_fuel]
    base_col = f"{prefix}_base_price"
    retail_col = f"{prefix}_retail_price"
    contrib_col = f"{prefix}_bog_contribution"
    spend_col = f"{prefix}_bog_spending"
    prefixes = [FUEL_META[f][0] for f in selected_fuels]
    events = adjustment_rows(data, [prefix])
    latest = data.iloc[-1]

    k1, k2, k3, k4, k5 = st.columns(5)
    expected_days = (data.date.max() - data.date.min()).days + 1
    coverage = len(data) / expected_days * 100
    with k1:
        _kpi_card("SỐ NGÀY DỮ LIỆU", f"{len(data):,}", f"Độ phủ ngày: {coverage:.1f}%", progress_svg(coverage))
    with k2:
        _kpi_card(f"GIÁ BÁN LẺ ({primary_fuel})", f"{latest[retail_col]:,.0f} {unit}", "Cập nhật kỳ cuối",
                  sparkline_svg(data[retail_col], COLORS[primary_fuel], "pm-retail"))
    with k3:
        _kpi_card(f"GIÁ CƠ SỞ ({primary_fuel})", f"{latest[base_col]:,.0f} {unit}", "Giá trị ghi nhận",
                  sparkline_svg(data[base_col], "#4B5694", "pm-base"))
    with k4:
        _kpi_card(f"TRÍCH LẬP BOG ({primary_fuel})", f"{latest[contrib_col]:,.0f} {unit}", "Mức tại kỳ cuối",
                  sparkline_svg(data[contrib_col], "#7288AE", "pm-contrib"))
    with k5:
        _kpi_card(f"CHI SỬ DỤNG BOG ({primary_fuel})", f"{latest[spend_col]:,.0f} {unit}", "Mức tại kỳ cuối",
                  sparkline_svg(data[spend_col], "#C1B49A", "pm-spend"))

    bog_events = events[events[contrib_col].ne(0) | events[spend_col].ne(0)].copy()

    row1_left, row1_right = st.columns([4, 6])
    with row1_left:
        st.markdown(f"<div class='section-header'>TÁC ĐỘNG CỦA QUỸ BOG ĐẾN GIÁ BÁN LẺ ({primary_fuel})</div>", unsafe_allow_html=True)
        if bog_events.empty:
            st.info("Không có kỳ điều chỉnh nào phát sinh trích lập hoặc chi sử dụng BOG trong phạm vi đã chọn.")
        else:
            chosen_date = st.selectbox(
                "Chọn kỳ có can thiệp BOG:", bog_events.date.sort_values(ascending=False).tolist(),
                format_func=lambda d: d.strftime("%d/%m/%Y"), key="wf_date_select",
            )
            row = data[data.date.eq(chosen_date)].iloc[0]
            base, contribution = row[base_col], row[contrib_col]
            spending, retail = row[spend_col], row[retail_col]
            net_effect = contribution - spending
            
            # Dynamic Y-axis zoom to make small BOG changes clearly visible
            y_min = min(base, retail) - 1000
            y_max = max(base, retail) + 1000
            
            fig = go.Figure(go.Waterfall(
                name=primary_fuel,
                orientation="v",
                measure=["relative", "relative", "relative", "total"],
                x=["Giá cơ sở (A)", "Trích lập BOG (B)", "Chi sử dụng BOG (C)", "Giá bán lẻ"],
                textposition="outside",
                text=[f"{base:,.0f} đ", 
                      f"+{contribution:,.0f} đ" if contribution > 0 else "0 đ", 
                      f"-{spending:,.0f} đ" if spending > 0 else "0 đ", 
                      f"{retail:,.0f} đ"],
                y=[base, contribution, -spending, retail],
                connector=dict(line=dict(color="#7288AE", width=1, dash="dot")),
                decreasing=dict(marker=dict(color="#7288AE")),
                increasing=dict(marker=dict(color="#4B5694")),
                totals=dict(marker=dict(color="#0B1849"))
            ))
            
            effect_text = (f"BOG làm giá tăng: <b>{net_effect:,.0f} {unit}</b>" if net_effect >= 0
                           else f"BOG hỗ trợ giảm giá: <b>{abs(net_effect):,.0f} {unit}</b>")
            fig.add_annotation(
                x=0.5, y=1.16, xref="paper", yref="paper", showarrow=False,
                text=effect_text,
                font=dict(size=13, color="#0B1849"),
            )
            fig.update_layout(
                height=230, plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(title=None), yaxis=dict(title=f"Giá ({unit})", range=[y_min, y_max], showgrid=False),
                showlegend=False, margin=dict(l=48, r=20, t=38, b=35),
            )
            style_figure(fig, show_legend=False)
            st.plotly_chart(fig, use_container_width=True)

    with row1_right:
        st.markdown(f"<div class='section-header'>LỊCH SỬ TRÍCH LẬP VÀ CHI SỬ DỤNG BOG ({primary_fuel})</div>", unsafe_allow_html=True)
        event_primary = adjustment_rows(data, [prefix])
        if event_primary.empty or (event_primary[[contrib_col, spend_col]].fillna(0) == 0).all().all():
            st.info("Không phát sinh trích lập hoặc chi BOG trong phạm vi bộ lọc.")
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=event_primary.date, y=event_primary[contrib_col], name="Mức trích lập",
                                     mode="lines", line_shape="hv", line=dict(color="#4B5694", width=2),
                                     hovertemplate="Ngày %{x|%d/%m/%Y}<br>Trích lập: %{y:,.0f} " + unit + "<extra></extra>"))
            fig.add_trace(go.Scatter(x=event_primary.date, y=event_primary[spend_col], name="Mức chi sử dụng",
                                     mode="lines", line_shape="hv", line=dict(color="#C1B49A", width=2),
                                     hovertemplate="Ngày %{x|%d/%m/%Y}<br>Chi sử dụng: %{y:,.0f} " + unit + "<extra></extra>"))
            date_padding = pd.Timedelta(days=45)
            fig.update_layout(
                height=322, plot_bgcolor="white", paper_bgcolor="white", yaxis_title=unit,
                xaxis=dict(range=[event_primary.date.min() - date_padding, event_primary.date.max() + date_padding]),
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="center", x=0.5),
                margin=dict(l=58, r=28, t=48, b=42),
            )
            style_figure(fig)
            st.plotly_chart(fig, use_container_width=True)

    row2_left, row2_right = st.columns(2)
    with row2_left:
        st.markdown("<div class='section-header'>MỨC GIẢM THAY ĐỔI GIÁ</div>", unsafe_allow_html=True)
        absorption = []
        for fuel in selected_fuels:
            p, _ = FUEL_META[fuel]
            event_fuel = adjustment_rows(data, [p])
            base_std = event_fuel[f"{p}_base_price"].pct_change().std()
            retail_std = event_fuel[f"{p}_retail_price"].pct_change().std()
            value = (base_std - retail_std) / base_std * 100 if pd.notna(base_std) and base_std > 0 else 0
            absorption.append(value)
        min_x = min(-5, min(absorption) * 1.2) if absorption else -5
        max_x = max(10, max(absorption) * 1.25) if absorption else 10
        fig = go.Figure(go.Bar(y=selected_fuels, x=absorption, orientation="h",
                               marker_color=[COLORS[f] for f in selected_fuels],
                               text=[f"{v:.1f}%" for v in absorption], textposition="outside"))
        fig.add_vline(x=0, line_color="#94A3B8")
        fig.update_layout(height=240, plot_bgcolor="white", paper_bgcolor="white",
                          xaxis=dict(title="Mức giảm thay đổi (%)", range=[min_x, max_x]))
        style_figure(fig, show_legend=False, keep_zero_line=True)
        st.plotly_chart(fig, use_container_width=True)

    with row2_right:
        st.markdown("<div class='section-header'>SỐ KỲ TRÍCH LẬP VÀ CHI SỬ DỤNG BOG</div>", unsafe_allow_html=True)
        fig = go.Figure()
        contribution_counts, spending_counts = [], []
        for fuel in selected_fuels:
            p, _ = FUEL_META[fuel]
            event_fuel = adjustment_rows(data, [p])
            contribution_counts.append(int(event_fuel[f"{p}_bog_contribution"].gt(0).sum()))
            spending_counts.append(int(event_fuel[f"{p}_bog_spending"].gt(0).sum()))
        fig.add_trace(go.Bar(x=selected_fuels, y=contribution_counts, name="Có trích lập", marker_color="#4B5694",
                             text=contribution_counts, textposition="outside"))
        fig.add_trace(go.Bar(x=selected_fuels, y=spending_counts, name="Có chi sử dụng", marker_color="#C1B49A",
                             text=spending_counts, textposition="outside"))
        fig.update_layout(height=240, barmode="group", plot_bgcolor="white", paper_bgcolor="white",
                          yaxis=dict(title="Số kỳ", rangemode="tozero"),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                          bargap=0.28, bargroupgap=0.08, margin=dict(l=45, r=15, t=42, b=45))
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    row3_left, row3_right = st.columns(2)
    with row3_left:
        st.markdown("<div class='section-header'>TẦN SUẤT ĐIỀU CHỈNH GIÁ QUA CÁC NĂM</div>", unsafe_allow_html=True)
        full = df_full.sort_values("date").copy()
        full_events = adjustment_rows(full, [prefix]).assign(Năm=lambda x: x.date.dt.year.astype(str))
        annual = full_events.groupby("Năm").size().reset_index(name="Số kỳ")
        colors = ["#0B1849" if selected_year == "Tất cả các năm" or y == selected_year else "#7288AE" for y in annual.Năm]
        fig = go.Figure(go.Bar(x=annual.Năm, y=annual["Số kỳ"], marker_color=colors,
                               text=annual["Số kỳ"], textposition="outside"))
        max_kỳ = annual["Số kỳ"].max() if not annual.empty else 60
        fig.update_layout(
            height=240, plot_bgcolor="white", paper_bgcolor="white", yaxis_title="Số kỳ",
            xaxis=dict(type="category", range=[-0.55, len(annual) - 0.45], automargin=True),
            yaxis=dict(rangemode="tozero", range=[0, max_kỳ * 1.15]), margin=dict(l=48, r=32, t=35, b=42),
        )
        style_figure(fig, show_legend=False)
        st.plotly_chart(fig, use_container_width=True)

    with row3_right:
        st.markdown(f"<div class='section-header'>GIÁ BÁN LẺ VÀ GIÁ CƠ SỞ GHI NHẬN ({primary_fuel})</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.date, y=data[base_col], name="Giá cơ sở",
                                 line=dict(color="#9AA9C4", width=2.0, dash="dash")))
        fig.add_trace(go.Scatter(
            x=data.date, y=data[retail_col], name="Giá bán lẻ",
            line=dict(color="#0B1849", width=2.4),
        ))
        time_padding = pd.Timedelta(days=45)
        fig.update_layout(height=240, plot_bgcolor="white", paper_bgcolor="white", yaxis_title=unit,
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                          hovermode="x unified",
                          xaxis=dict(automargin=True, showgrid=False, zeroline=False,
                                     range=[data.date.min() - time_padding, data.date.max() + time_padding]),
                          yaxis=dict(title=unit, showgrid=False, zeroline=False),
                          margin=dict(l=50, r=25, t=42, b=35))
        style_figure(fig)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Xem dữ liệu điều hành theo bộ lọc"):
        columns = ["date", "is_adjustment_day"]
        for p in prefixes:
            columns += [f"{p}_base_price", f"{p}_retail_price", f"{p}_bog_contribution", f"{p}_bog_spending"]
        st.dataframe(data[columns], width="stretch", hide_index=True)