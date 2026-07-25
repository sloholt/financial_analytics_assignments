"""
Bond Valuation Dashboard

Run with: streamlit run bond_valuation_dashboard.py

Pulls styling from dashboard_design.py, math and logic from bond_valuation_calculations.py
and rendering from functions.py
"""

import streamlit as st
import dashboard_design
import functions
import bond_valuation_calculations as bvc

# Page set up:
st.set_page_config(page_title="Bond Valuation Calculation", layout="wide")
dashboard_design.inject_css()

# Hero:
functions.render_hero()

# Input modules:
inputs = functions.render_input_modules()

# Calculations:
payments_per_year = bvc.compounding_to_n(inputs["compounding"])

try:
    metrics = bvc.compute_bond_metrics(
        coupon_rate=bvc.pct_to_decimal(inputs["coupon_rate"]),
        years=inputs["years"],
        ytm=bvc.pct_to_decimal(inputs["ytm"]),
        par=inputs["par"],
        payments_per_year=payments_per_year,
    )

    duration_df = bvc.build_duration_table(
        par=inputs["par"],
        coupon_rate=bvc.pct_to_decimal(inputs["coupon_rate"]),
        ytm=bvc.pct_to_decimal(inputs["ytm"]),
        years=inputs["years"],
        payments_per_year=payments_per_year,
    )

    yields, prices = bvc.generate_price_yield_curve(
        coupon_rate=bvc.pct_to_decimal(inputs["coupon_rate"]),
        years=inputs["years"],
        par=inputs["par"],
        payments_per_year=payments_per_year,
        ytm_center=bvc.pct_to_decimal(inputs["ytm"]),
    )
except ValueError as e:
    st.error(f"Invalid inputs: {e}")
    st.stop()
except ZeroDivisionError as e:
    st.error(f"Calculation error: {e}")
    st.stop()

# Calculation, graph and duration table displays
functions.render_calculation_display(metrics)
functions.render_graph(
    yields,
    prices,
    current_ytm=bvc.pct_to_decimal(inputs["ytm"]),
    current_price=metrics["price"],
)
functions.render_duration_table(duration_df)
