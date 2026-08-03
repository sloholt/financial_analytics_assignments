"""
Rendering functions for the dashboard.
Each function renders one section of the app using Streamlit and design.py.

Note: no calculation logic is used here
"""

import datetime as dt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import dashboard_design
from bond_valuation_calculations import (
    COMPOUNDING_OPTIONS,
    DEFAULT_COMPOUNDING,
    DEFAULT_PAR,
)

DEFAULT_FORECAST_YEARS = 5
DEFAULT_DIVIDEND = 1.00

# =============================================================================
# Bond Valuation tab
# =============================================================================


def render_hero(title="Valuation Dashboard", eyebrow="SYSTEM OVERVIEW"):
    st.markdown(
        f"""
        <div class="hero">
            <div>
                <div class="eyebrow">{eyebrow}</div>
                <h1>{title}</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_label(tag, title):
    st.markdown(
        f'<div class="section-label"><span class="tag">{tag}</span>{title}</div>',
        unsafe_allow_html=True,
    )


def _clamp_input(key, floor, floor_label, msg_key):
    value = st.session_state[key]
    if value < floor:
        st.session_state[key] = floor
        st.session_state[msg_key] = (
            f"Value can't go below {floor_label} — reset to {floor_label}."
        )
    else:
        st.session_state[msg_key] = None


def render_input_modules():
    """Renders the 5 input modules and returns all collected values as a dictionary"""
    render_section_label("INPUT", "Bond parameters")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(
            '<div class="module-card"><div class="module-title">01 · Coupon Rate</div>',
            unsafe_allow_html=True,
        )
        coupon_rate = st.number_input(
            "Coupon rate (APR, %)",
            min_value=-100.0,
            value=5.0,
            step=0.10,
            key="coupon_rate",
            # on_change=_clamp_input,
            # args=("coupon_rate", 0.0, "0%", "coupon_rate_msg"),
        )
        # if st.session_state.get("coupon_rate_msg"):
        # st.warning(st.session_state["coupon_rate_msg"])
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown(
            '<div class="module-card"><div class="module-title">02 · Term to Maturity</div>',
            unsafe_allow_html=True,
        )
        years = st.number_input(
            "Term to maturity (years)", min_value=0.1, value=10.0, step=0.5, key="years"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown(
            '<div class="module-card"><div class="module-title">03 · YTM</div>',
            unsafe_allow_html=True,
        )
        ytm = st.number_input(
            "Yield to maturity (APR, %)",
            min_value=-100.0,
            value=6.0,
            step=0.10,
            key="ytm",
            # on_change=_clamp_input,
            # args=("ytm", 0.0, "0%", "ytm_msg"),
        )
        # if st.session_state.get("ytm_msg"):
        # st.warning(st.session_state["ytm_msg"])
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        st.markdown(
            '<div class="module-card"><div class="module-title">04 · Par Value</div>',
            unsafe_allow_html=True,
        )
        par = st.number_input(
            "Par value ($)",
            # min_value=0.0,
            value=float(DEFAULT_PAR),
            step=1.0,
            key="par",
            on_change=_clamp_input,
            args=("par", 0.0, "$1", "par_msg"),
        )
        if st.session_state.get("par_msg"):
            st.warning(st.session_state["par_msg"])
        st.markdown("</div>", unsafe_allow_html=True)

    with c5:
        st.markdown(
            '<div class="module-card"><div class="module-title">05 · Compounding</div>',
            unsafe_allow_html=True,
        )
        compounding = st.selectbox(
            "Compounding frequency",
            options=list(COMPOUNDING_OPTIONS.keys()),
            index=list(COMPOUNDING_OPTIONS.keys()).index(DEFAULT_COMPOUNDING),
            key="compounding",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    return {
        "coupon_rate": coupon_rate,
        "years": years,
        "ytm": ytm,
        "par": par,
        "compounding": compounding,
    }


def render_calculation_display(metrics):
    render_section_label("OUTPUT", "Calculation readout")

    max_gauge = max(metrics["price"] * 1.6, 1)
    gauge_pct = min(max(metrics["price"] / max_gauge, 0), 1) * 100

    st.markdown(
        f"""
        <div class="readout-panel">
            <div class="gauge-wrap" style="background: conic-gradient({dashboard_design.ACCENT_AMBER} {gauge_pct}%, {dashboard_design.BORDER} 0);">
                <div class="gauge-hole">
                    <div class="gauge-value">${metrics['price']:,.2f}</div>
                    <div class="gauge-unit">BOND PRICE</div>
                </div>
            </div>
            <div class="stat-stack">
                <div class="stat-row"><span class="stat-label">MACAULAY DURATION</span><span class="stat-value">{metrics['macaulay_duration']:,.3f} yrs</span></div>
                <div class="stat-row"><span class="stat-label">MODIFIED DURATION</span><span class="stat-value">{metrics['modified_duration']:,.3f} yrs</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_graph(x, y, current_ytm, current_price):
    render_section_label("TREND", "Price / yield sensitivity")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x * 100,
            y=y,
            mode="lines",
            line=dict(color=dashboard_design.ACCENT_CYAN, width=2.5),
            fill="tozeroy",
            fillcolor="rgba(79, 209, 197, 0.08)",
            name="Price",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[current_ytm * 100],
            y=[current_price],
            mode="markers",
            marker=dict(
                color=dashboard_design.ACCENT_AMBER,
                size=10,
                line=dict(color=dashboard_design.PANEL, width=2),
            ),
            name="Current YTM",
        )
    )
    fig.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor=dashboard_design.PANEL,
        paper_bgcolor=dashboard_design.PANEL,
        font=dict(family="IBM Plex Mono", color=dashboard_design.TEXT_MUTED, size=12),
        xaxis=dict(
            title="Yield to maturity (%)",
            showgrid=False,
            color=dashboard_design.TEXT_MUTED,
            linecolor=dashboard_design.BORDER,
        ),
        yaxis=dict(
            title="Bond price ($)",
            showgrid=True,
            gridcolor=dashboard_design.BORDER,
            color=dashboard_design.TEXT_MUTED,
            zeroline=False,
        ),
        showlegend=False,
    )

    st.markdown('<div class="panel-frame">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)


def render_duration_table(df):
    render_section_label("SCHEDULE", "Duration table")

    styled = df.style.format(
        {
            "Cash Flow": "{:,.2f}",
            "PV of CF": "{:,.2f}",
            "Weight": "{:.4f}",
            "Time x Weight": "{:.4f}",
        }
    )

    st.markdown(
        '<div class="panel-frame" style="padding-bottom: 1rem;">',
        unsafe_allow_html=True,
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# Stock Valuation (Dividend Discount Model) tab
# =============================================================================
def render_stock_input_modules():
    """Renders the stock/DDM input modules and returns all collected values."""
    render_section_label("INPUT", "Company & rate assumptions")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(
            '<div class="module-card"><div class="module-title">01 · Ticker</div>',
            unsafe_allow_html=True,
        )
        ticker = st.text_input(
            "Stock ticker",
            value="",
            placeholder="e.g. AAPL",
            key="stock_ticker",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown(
            '<div class="module-card"><div class="module-title">02 · Discount Rate</div>',
            unsafe_allow_html=True,
        )
        discount_rate = st.number_input(
            "Required return / discount rate (APR, %)",
            value=9.0,
            step=0.10,
            key="stock_discount_rate",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown(
            '<div class="module-card"><div class="module-title">03 · Terminal Growth</div>',
            unsafe_allow_html=True,
        )
        terminal_growth_rate = st.number_input(
            "Terminal growth rate (%)",
            value=2.5,
            step=0.10,
            key="stock_terminal_growth",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        st.markdown(
            '<div class="module-card"><div class="module-title">04 · Market Price</div>',
            unsafe_allow_html=True,
        )
        market_price = st.number_input(
            "Current market price ($)",
            min_value=0.0,
            value=100.0,
            step=0.50,
            key="stock_market_price",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c5:
        st.markdown(
            '<div class="module-card"><div class="module-title">05 · First Dividend Timing</div>',
            unsafe_allow_html=True,
        )
        months_to_first_dividend = st.number_input(
            "Months to first dividend",
            min_value=1,
            max_value=12,
            value=12,
            step=1,
            key="stock_months_to_first",
            help="Use 12 if the valuation date falls exactly on a fiscal year end. "
            "Use a smaller number if the valuation date is partway through the "
            "current fiscal year — the first cash flow will be prorated.",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    render_section_label("INPUT", "Forecasted annual dividends")
    st.markdown('<div class="module-card">', unsafe_allow_html=True)
    num_years = st.number_input(
        "Number of forecasted years",
        min_value=1,
        max_value=15,
        value=DEFAULT_FORECAST_YEARS,
        step=1,
        key="stock_num_years",
    )
    num_years = int(num_years)

    default_rows = pd.DataFrame(
        {
            "Forecast Year": list(range(1, num_years + 1)),
            "Dividend ($)": [DEFAULT_DIVIDEND] * num_years,
        }
    )

    edited = st.data_editor(
        default_rows,
        key=f"stock_dividend_editor_{num_years}",
        hide_index=True,
        use_container_width=True,
        column_config={
            "Forecast Year": st.column_config.NumberColumn(disabled=True),
            "Dividend ($)": st.column_config.NumberColumn(
                min_value=0.0, step=0.01, format="%.2f"
            ),
        },
    )
    st.caption(
        "Edit each year's forecasted dividend directly in the table above. "
        "Changing the year count resets the table."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    dividends = edited["Dividend ($)"].tolist()

    return {
        "ticker": ticker,
        "dividends": dividends,
        "terminal_growth_rate": terminal_growth_rate,
        "discount_rate": discount_rate,
        "market_price": market_price,
        "months_to_first_dividend": months_to_first_dividend,
    }


def render_stock_calculation_display(result):
    """Renders the intrinsic value readout and buy/sell/hold recommendation."""
    render_section_label("OUTPUT", "Valuation readout")

    rec = result["recommendation"]
    rec_class = {"BUY": "rec-buy", "SELL": "rec-sell", "HOLD": "rec-hold"}[rec]
    diff_pct = result["diff_pct"]
    diff_sign = "+" if diff_pct >= 0 else ""

    st.markdown(
        f"""
        <div class="rec-panel">
            <div class="rec-metrics">
                <div>
                    <div class="rec-metric-label">TICKER</div>
                    <div class="rec-metric-value">{result['ticker']}</div>
                </div>
                <div>
                    <div class="rec-metric-label">INTRINSIC VALUE</div>
                    <div class="rec-metric-value">${result['intrinsic_value']:,.2f}</div>
                </div>
                <div>
                    <div class="rec-metric-label">MARKET PRICE</div>
                    <div class="rec-metric-value">${result['market_price']:,.2f}</div>
                </div>
                <div>
                    <div class="rec-metric-label">MISPRICING</div>
                    <div class="rec-metric-value">{diff_sign}{diff_pct * 100:,.2f}%</div>
                </div>
                <div>
                    <div class="rec-metric-label">TERMINAL VALUE</div>
                    <div class="rec-metric-value">${result['terminal_value']:,.2f}</div>
                </div>
            </div>
            <div class="rec-badge {rec_class}">{rec}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stock_cash_flow_table(df):
    render_section_label("SCHEDULE", "Discounted cash flow table")

    styled = df.style.format(
        {
            "Forecasted Dividend": lambda v: (
                f"{v:,.2f}" if isinstance(v, (int, float)) else v
            ),
            "Cash Flow Used": "{:,.2f}",
            "PV of Cash Flow": "{:,.2f}",
        }
    )

    st.markdown(
        '<div class="panel-frame" style="padding-bottom: 1rem;">',
        unsafe_allow_html=True,
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)
