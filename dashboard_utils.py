import numpy as np
import pandas as pd


FUEL_META = {
    "Xăng RON 95": ("ron95", "đ/lít"),
    "Xăng E5 RON 92": ("e5ron92", "đ/lít"),
    "Dầu Diesel": ("diesel", "đ/lít"),
}


def validate_data(df: pd.DataFrame) -> dict:
    """Return reproducible structural checks; this does not certify external provenance."""
    dates = pd.to_datetime(df["date"])
    expected = pd.date_range(dates.min(), dates.max(), freq="D")
    missing_dates = expected.difference(pd.DatetimeIndex(dates))
    required = ["date", "is_adjustment_day", "usd_vnd", "brent_usd_per_barrel"]
    for prefix, _ in FUEL_META.values():
        required += [
            f"{prefix}_base_price", f"{prefix}_retail_price",
            f"{prefix}_bog_contribution", f"{prefix}_bog_spending",
        ]
    formula_errors = 0
    for prefix, _ in FUEL_META.values():
        expected_retail = (
            df[f"{prefix}_base_price"]
            + df[f"{prefix}_bog_contribution"]
            - df[f"{prefix}_bog_spending"]
        )
        formula_errors += int((~np.isclose(df[f"{prefix}_retail_price"], expected_retail)).sum())
    return {
        "rows": len(df),
        "start": dates.min(),
        "end": dates.max(),
        "missing_columns": [c for c in required if c not in df.columns],
        "nulls": int(df[required].isna().sum().sum()),
        "duplicate_dates": int(dates.duplicated().sum()),
        "missing_dates": len(missing_dates),
        "formula_errors": formula_errors,
    }


def adjustment_rows(df: pd.DataFrame, prefixes: list[str]) -> pd.DataFrame:
    """Use the explicit flag plus observed price changes so bad flags cannot hide changes."""
    ordered = df.sort_values("date").copy()
    changed = pd.Series(False, index=ordered.index)
    for prefix in prefixes:
        changed |= ordered[f"{prefix}_retail_price"].diff().ne(0)
    if len(changed):
        changed.iloc[0] = False
    return ordered[ordered["is_adjustment_day"].eq(1) | changed]


def period_change(series: pd.Series) -> float:
    s = series.dropna()
    if len(s) < 2 or s.iloc[0] == 0:
        return np.nan
    return (s.iloc[-1] / s.iloc[0] - 1) * 100


def sparkline_svg(values, color="#0B1849", grad_id="sparkline") -> str:
    """Small dependency-free SVG chart for KPI cards."""
    series = pd.Series(values, dtype="float64").dropna()
    if len(series) < 2:
        return '<div style="height:30px"></div>'
    # Downsample long daily series while preserving the full selected period.
    if len(series) > 60:
        positions = np.linspace(0, len(series) - 1, 60).astype(int)
        series = series.iloc[positions]
    low, high = float(series.min()), float(series.max())
    span = high - low if high != low else 1.0
    width, height, padding = 120, 26, 2
    points = []
    for i, value in enumerate(series):
        x = i / (len(series) - 1) * width
        y = height - padding - (float(value) - low) / span * (height - 2 * padding)
        points.append(f"{x:.1f},{y:.1f}")
    path = "M " + " L ".join(points)
    fill = f"{path} L {width},{height} L 0,{height} Z"
    return (
        f'<svg width="100%" height="30" viewBox="0 0 {width} {height}" '
        'preserveAspectRatio="none" aria-hidden="true">'
        f'<defs><linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{color}" stop-opacity="0.25"/>'
        f'<stop offset="100%" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
        f'<path d="{fill}" fill="url(#{grad_id})"/><path d="{path}" fill="none" '
        f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )


def progress_svg(value, color="#0B1849") -> str:
    pct = max(0.0, min(100.0, float(value)))
    return (
        '<svg width="100%" height="8" viewBox="0 0 100 8" preserveAspectRatio="none" '
        'style="border-radius:4px;overflow:hidden" aria-hidden="true">'
        '<rect width="100" height="8" fill="#E2E8F0"/>'
        f'<rect width="{pct:.1f}" height="8" fill="{color}"/></svg>'
    )


def style_figure(fig, show_legend=True, keep_zero_line=False):
    """Áp dụng quy tắc trình bày thống nhất cho mọi biểu đồ dashboard."""
    fig.update_xaxes(showgrid=False, zeroline=keep_zero_line)
    fig.update_yaxes(showgrid=False, zeroline=keep_zero_line)
    fig.update_layout(
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            title=None,
        ),
    )
    return fig
