# To get started: Install necessary libraries in your terminal run: pip install streamlit pandas plotly
# To run the file: streamlit run valuation_calculator.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page Layout:
st.set_page_config(page_title="Valuation Calculator", layout="wide")

st.title("Valuation Calculator")
st.write("Financial Analysis, Assignment 1: Problem 6")
st.write("Sloane Holtby, Jessica North, Dru Valugubelly")
st.write("July 19th, 2026")

# Collecting user input for calculations:
calc_type = st.radio("Select a Calculation:", ["Present Value", "Future Value"])
forecast_periods = st.number_input(
    "Number of discrete forecast periods", min_value=0, step=1
)
growth_phases = st.number_input(
    "Number of growth phases (including 'none')", min_value=1, value=1, step=1
)
discount_rate = st.number_input("Discount rate (%)", value=1.0) / 100

# Adjusting cf based on forecast periods
if forecast_periods == 0:
    initial_cf = st.number_input("Cash Flow in period 1", value=0.0)
else:
    initial_cf = st.number_input("Initial cash flow (CF0)", value=0.0)


# Forecast cash flows. One input box per period 
cfs = []
cf = initial_cf
for i in range(1, int(forecast_periods) + 1):
    cf = st.number_input(f"Cash flow in period {i}", value=cf, key=f"initial_cf_{i}")
    cfs.append(cf)


# Per phase inputs:
phases = [] #list of dictionaries storing the total phases and their values 
for i in range(int(growth_phases)):
    st.subheader(f"Phase {i+1}")
    growth = (
        st.number_input(
            f"Enter the growth rate for phase {i+1} as a percentage",
            value=0.0,
            key=f"growth_{i}",
        )
        / 100
    )
    is_last = i == growth_phases - 1
    terminal_type = "Annuity"  # default for non-last phases
    if is_last:
        terminal_type = st.radio(
            "Annuity or Perpetuity?", ["Annuity", "Perpetuity"], key=f"terminal_{i}"
        )
    if terminal_type == "Perpetuity":
        length = None
        st.caption("Perpetuities have no defined length")
    else:
        #asks for length if it is not a perpetuity 
        length = st.number_input(
            f"Enter the length of phase {i+1} (periods)",
            min_value=1,
            value=1,
            key=f"length_{i}",
        )

    phases.append(
        {
            "phase": i + 1,
            "growth_rate": growth,
            "length": length,
            "terminal_type": terminal_type,
        }
    )

# Display phase inputs
df_phases = pd.DataFrame(phases)
st.write("### Phase Inputs")
st.dataframe(df_phases)


# PVA - Growing Annuity at the start of the phase
def pva_growing(cf1, r, g, n):
    if abs(r - g) < 1e-9:
        return n * cf1 / (1 + r)
    return (cf1 / (r - g)) * (1 - ((1 + g) / (1 + r)) ** n)


# PV of phase discounted to today (infinite stream)
def pv_perpetuity(cf1, r, g):
    if g >= r:
        st.error("Growth rate must be less than discount rate.")
        st.stop()
    return cf1 / (r - g)


# Convert each phase to today's present value
def phase_pv(cf1, r, g, n, previous_periods, terminal_type):
    if terminal_type == "Perpetuity":
        value_start = pv_perpetuity(cf1, r, g)
    else:
        value_start = pva_growing(cf1, r, g, n)
    return value_start / (1 + r) ** previous_periods

# Main calculations
def main():
    r = discount_rate

    # Discrete forecast PV
    pv_discrete = sum(cf / (1 + r) ** t for t, cf in enumerate(cfs, start=1))

    # Growth phase PVs
    breakdown = [{"Component": "PV Discrete Forecast", "Value": pv_discrete}]
    passed_periods = int(forecast_periods)
    prior_cf = cfs[-1] if cfs else initial_cf
    is_first_application = not cfs

    # Per phase cash flow and discounted PV 
    for idx, p in enumerate(phases):
        g = p["growth_rate"]
        n = p["length"]
        if idx == 0 and is_first_application:
            cf1 = prior_cf
        else:
            cf1 = prior_cf * (1 + g)

        pv = phase_pv(cf1, r, g, n, passed_periods, p["terminal_type"])
        label = f"Present Value Phase {p['phase']} {p["terminal_type"]}"
        breakdown.append({"Component": label, "Value": pv})

        if p["terminal_type"] != "Perpetuity":
            prior_cf = cf1 * (1 + g) ** (n - 1)
            passed_periods += n

    total_pv = sum(row["Value"] for row in breakdown)

    total_periods = int(forecast_periods) + sum(
        r["length"] for r in phases if r["terminal_type"] != "Perpetuity"
    )
    if calc_type == "Future Value":
        final_value = total_pv * (1 + r) ** total_periods
    else:
        final_value = total_pv

    # Display results as a table 
    st.write("#### Valuation Breakdown")
    df_breakdown = pd.DataFrame(breakdown)
    st.dataframe(df_breakdown)

    st.write("### Result")
    st.metric(label=f"Total {calc_type}", value=f"${final_value:,.2f}")

    return final_value


if __name__ == "__main__":
    main()
