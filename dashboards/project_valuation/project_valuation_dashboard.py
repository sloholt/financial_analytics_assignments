"""
Project Valuation Dashboard (stand alone entry point)

Run with: streamlit run project_valuation_dashboard.py

This file wires everything together -> all layout/markup lives in project_valuation_functions.py
and all calculations live in project_valuation_calculations.py
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import dashboard_design
from project_valuation_functions import (
    render_hero,
    render_input_modules,
    compute_project_results,
    render_pro_forma_table,
    render_recommendation_panel,
)

st.set_page_config(
    page_title="Project Valuation Dashboard",
    layout="wide",
)

dashboard_design.inject_css()
render_hero()
inputs = render_input_modules()
results = compute_project_results(inputs)

render_pro_forma_table(results["pro_forma_df"])
render_recommendation_panel(results)
