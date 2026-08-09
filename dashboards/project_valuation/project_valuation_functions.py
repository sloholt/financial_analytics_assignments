"""
Rendering functions for Project Valuation Dashboard.
Each function renders one section of the app using Streamlit and dashboard_design.py

Note: no calculation logic is contained here -> all math comes from project_valuation_calculations.py
This module is self-contained so the dashboard can run standalone as well as mounted as a tab later.
"""

import pandas as pd
import streamlit as st
import dashboard_design
from project_valuation_calculations import (
    build_pro_forma_table,
    pro_forma_cf_schedule,
    calculate_npv,
    calculate_irr,
    calculate_payback,
    is_go,
)

DEFAULT_INITIAL_REVENUE = 1_000_000_000.0
DEFAULT_GROWTH_RATE = 7.5
DEFAULT_GROSS_MARGIN = 40.0
DEFAULT_TERM = 6
DEFAULT_BASE_OPEX = 200_000_000.0
DEFAULT_STEP_UP_THRESHOLD = 1_250_000_000.0
DEFAULT_STEP_UP_PCT = 10.0
DEFAULT_CAPEX = 750_000_000.0
DEFAULT_DISPOSAL = 0.0
DEFAULT_NWCREQ = 10.0
DEFAULT_TAXRATE = 21.0
DEFAULT_DISCRATE = 15.5
DEFAULT_PAYBACK_TARGET = 3.0


def render_hero(title="Project Valuation Dashboard", eyebrow="CAPITAL BUDGETING"):
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


# =============================================================================
# INPUTS
# =============================================================================
def render_input_modules():
    """Renders the project valuation input modules and returns all collected
    values as a dictionary of decimals/ints ready for the calculation functions."""

    render_section_label("INPUT", "Revenue & margin assumptions")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(
            '<div class="module-card"><div class="module-title">01 · Initial Revenue</div>',
            unsafe_allow_html=True,
        )
        initial_revenue = st.number_input(
            "Year 1 revenue ($)",
            min_value=0.0,
            value=DEFAULT_INITIAL_REVENUE,
            step=1000.0,
            key="pv_initial_revenue",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown(
            '<div class="module-card"><div class="module-title">02 · Revenue Growth</div>',
            unsafe_allow_html=True,
        )
        growth_rate = st.number_input(
            "Annual revenue growth (%)",
            value=DEFAULT_GROWTH_RATE,
            step=0.25,
            key="pv_growth_rate",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown(
            '<div class="module-card"><div class="module-title">03 · Gross Margin</div>',
            unsafe_allow_html=True,
        )
        gross_margin = st.number_input(
            "Gross margin, excl. depreciation (%)",
            min_value=0.0,
            max_value=100.0,
            value=DEFAULT_GROSS_MARGIN,
            step=0.1,
            key="pv_gross_margin",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        st.markdown(
            '<div class="module-card"><div class="module-title">04 · Project Term</div>',
            unsafe_allow_html=True,
        )
        term = st.number_input(
            "Project term (years)",
            min_value=0,
            value=DEFAULT_TERM,
            step=1,
            key="pv_term",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c5:
        st.markdown(
            '<div class="module-card"><div class="module-title">05 · Tax Rate</div>',
            unsafe_allow_html=True,
        )
        taxrate = st.number_input(
            "Corporate tax rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=DEFAULT_TAXRATE,
            step=0.01,
            key="pv_taxrate",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    render_section_label("INPUT", "Operating costs")
    c6, c7, c8 = st.columns(3)

    with c6:
        st.markdown(
            '<div class="module-card"><div class="module-title">06 · Base Opex</div>',
            unsafe_allow_html=True,
        )
        base_opex = st.number_input(
            "Base annual opex ($)",
            min_value=0.0,
            value=DEFAULT_BASE_OPEX,
            step=1000.0,
            key="pv_base_opex",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c7:
        st.markdown(
            '<div class="module-card"><div class="module-title">07 · Opex Step-Up Threshold</div>',
            unsafe_allow_html=True,
        )
        opex_step_up_threshold = st.number_input(
            "Revenue level that triggers step-up ($)",
            min_value=0.0,
            value=DEFAULT_STEP_UP_THRESHOLD,
            step=1000.0,
            key="pv_step_up_threshold",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c8:
        st.markdown(
            '<div class="module-card"><div class="module-title">08 · Opex Step-Up</div>',
            unsafe_allow_html=True,
        )
        opex_step_up_pct = st.number_input(
            "Opex step-up, once threshold is crossed (%)",
            min_value=0.0,
            value=DEFAULT_STEP_UP_PCT,
            step=0.01,
            key="pv_step_up_pct",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    render_section_label("INPUT", "Capital & working capital")
    c9, c10, c11 = st.columns(3)

    with c9:
        st.markdown(
            '<div class="module-card"><div class="module-title">09 · CapEx</div>',
            unsafe_allow_html=True,
        )
        capex = st.number_input(
            "Initial capital expenditure ($)",
            min_value=0.0,
            value=DEFAULT_CAPEX,
            step=1000.0,
            key="pv_capex",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c10:
        st.markdown(
            '<div class="module-card"><div class="module-title">10 · Disposal / Salvage</div>',
            unsafe_allow_html=True,
        )
        disposal = st.number_input(
            "Terminal disposal / salvage value ($)",
            value=DEFAULT_DISPOSAL,
            step=1000.0,
            key="pv_disposal",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c11:
        st.markdown(
            '<div class="module-card"><div class="module-title">11 · NWC Requirement</div>',
            unsafe_allow_html=True,
        )
        nwcreq = st.number_input(
            "NWC as % of next year's revenue",
            min_value=0.0,
            max_value=100.0,
            value=DEFAULT_NWCREQ,
            step=0.01,
            key="pv_nwcreq",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    render_section_label("INPUT", "Decision rules")
    c12, c13 = st.columns(2)

    with c12:
        st.markdown(
            '<div class="module-card"><div class="module-title">12 · Discount Rate</div>',
            unsafe_allow_html=True,
        )
        discrate = st.number_input(
            "Discount rate / hurdle rate (%)",
            value=DEFAULT_DISCRATE,
            step=0.01,
            key="pv_discrate",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c13:
        st.markdown(
            '<div class="module-card"><div class="module-title">13 · Payback Target</div>',
            unsafe_allow_html=True,
        )
        management_target = st.number_input(
            "Management's maximum acceptable payback (years)",
            min_value=0.0,
            value=DEFAULT_PAYBACK_TARGET,
            step=0.01,
            key="pv_payback_target",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    return {
        "initial_revenue": initial_revenue,
        "growth_rate": growth_rate / 100,
        "gross_margin": gross_margin / 100,
        "term": int(term),
        "base_opex": base_opex,
        "opex_step_up_threshold": opex_step_up_threshold,
        "opex_step_up_pct": opex_step_up_pct / 100,
        "capex": capex,
        "disposal": disposal,
        "nwcreq": nwcreq / 100,
        "taxrate": taxrate / 100,
        "discrate": discrate / 100,
        "management_target": management_target,
    }


# =============================================================================
# OUTPUTS
# =============================================================================
def compute_project_results(inputs):
    """Runs the calculation pipeline with collected inputs and returns
    everything the render functions need: the pro forma table, the FCF
    schedule, and the NPV / IRR / payback metrics with Go / No Go decisions."""
    calc_kwargs = {
        k: v for k, v in inputs.items() if k not in ("discrate", "management_target")
    }

    pro_forma_df = build_pro_forma_table(**calc_kwargs)
    fcf_schedule = pro_forma_cf_schedule(**calc_kwargs)

    npv = calculate_npv(fcf_schedule, inputs["discrate"])
    irr = calculate_irr(fcf_schedule)
    payback = calculate_payback(fcf_schedule)
    decisions = is_go(
        irr,
        payback,
        management_target=inputs["management_target"],
        npv=npv,
        discrate=inputs["discrate"],
    )

    return {
        "pro_forma_df": pro_forma_df,
        "fcf_schedule": fcf_schedule,
        "npv": npv,
        "irr": irr,
        "payback": payback,
        "decisions": decisions,
    }


def render_pro_forma_table(df):
    """Pro Forma Cash Flows Table"""
    render_section_label("SCHEDULE", "Pro forma cash flows")

    currency_cols = [
        "Revenue",
        "Gross Profit",
        "Opex",
        "Depreciation",
        "EBIT",
        "Taxes",
        "NOPAT",
        "Operating CF",
        "Delta NWC",
        "CapEx",
        "Disposal",
        "FCF",
    ]
    styled = df.style.format({col: "{:,.0f}" for col in currency_cols})

    st.markdown(
        '<div class="panel-frame" style="padding-bottom: 1rem;">',
        unsafe_allow_html=True,
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_recommendation_panel(results):
    """NPV, IRR, and Payback Period, each with its own Go / No Go
    recommendation per management's decision rules."""
    render_section_label("OUTPUT", "Decision metrics")

    npv = results["npv"]
    irr = results["irr"]
    payback = results["payback"]
    decisions = results["decisions"]

    payback_display = "Never" if payback == float("inf") else f"{payback:,.2f} yrs"

    def badge_class(decision):
        return "rec-buy" if decision == "Go" else "rec-sell"

    st.markdown(
        f"""
        <div class="rec-panel">
            <div class="rec-metrics">
                <div>
                    <div class="rec-metric-label">NPV</div>
                    <div class="rec-metric-value">${npv:,.2f}</div>
                    <div class="rec-badge {badge_class(decisions['NPV'])}" style="margin-top:0.5rem; font-size:0.85rem; padding:0.35rem 0.8rem; display:inline-block;">{decisions['NPV']}</div>
                </div>
                <div>
                    <div class="rec-metric-label">IRR</div>
                    <div class="rec-metric-value">{irr * 100:,.2f}%</div>
                    <div class="rec-badge {badge_class(decisions['IRR'])}" style="margin-top:0.5rem; font-size:0.85rem; padding:0.35rem 0.8rem; display:inline-block;">{decisions['IRR']}</div>
                </div>
                <div>
                    <div class="rec-metric-label">PAYBACK PERIOD</div>
                    <div class="rec-metric-value">{payback_display}</div>
                    <div class="rec-badge {badge_class(decisions['Payback Period'])}" style="margin-top:0.5rem; font-size:0.85rem; padding:0.35rem 0.8rem; display:inline-block;">{decisions['Payback Period']}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
