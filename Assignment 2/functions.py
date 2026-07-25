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


def render_hero():
    st.markdown(
        f"""
        <div class="hero">
            <div>
                <div class="eyebrow">SYSTEM OVERVIEW</div>
                <h1>Bond Valuation Calculator</h1>
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
