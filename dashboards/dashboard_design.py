"""
Design elements for the dashboard
"""

import streamlit as st

# Colors
BG_VOID = "#0B0F14"
PANEL = "#121A21"
PANEL_RAISED = "#161F27"
BORDER = "#232E38"
TEXT_PRIMARY = "#EDEFF2"
TEXT_MUTED = "#7C8894"
ACCENT_AMBER = "#E8A33D"
ACCENT_CYAN = "#4FD1C5"
ACCENT_RED = "#E8615A"


# Injects CSS design for the dashboard
def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
 
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}
 
        .stApp {{
            background:
                radial-gradient(circle at 15% 0%, #101820 0%, {BG_VOID} 45%),
                {BG_VOID};
            color: {TEXT_PRIMARY};
        }}
 
        #MainMenu, footer, header {{visibility: hidden;}}
        .block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1300px; }}
 
        /* ---------- typography helpers ---------- */
        .mono {{ font-family: 'IBM Plex Mono', monospace; }}
        .eyebrow {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: {TEXT_MUTED};
        }}
 
        /* ---------- hero ---------- */
        .hero {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-bottom: 1px solid {BORDER};
            padding-bottom: 1.1rem;
            margin-bottom: 1.6rem;
        }}
        .hero h1 {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 2.1rem;
            letter-spacing: -0.01em;
            margin: 0.15rem 0 0 0;
            color: {TEXT_PRIMARY};
        }}
        .status-pill {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            color: {ACCENT_CYAN};
            border: 1px solid {ACCENT_CYAN}55;
            background: {ACCENT_CYAN}14;
            border-radius: 999px;
            padding: 0.35rem 0.9rem;
            white-space: nowrap;
        }}
        .status-dot {{
            display:inline-block; width:7px; height:7px; border-radius:50%;
            background:{ACCENT_CYAN}; margin-right:6px;
            box-shadow: 0 0 8px {ACCENT_CYAN};
        }}
 
        /* ---------- section labels ---------- */
        .section-label {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            font-size: 1.02rem;
            color: {TEXT_PRIMARY};
            margin: 1.9rem 0 0.7rem 0;
            display: flex;
            align-items: center;
            gap: 0.55rem;
        }}
        .section-label .tag {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.68rem;
            color: {ACCENT_AMBER};
            border: 1px solid {ACCENT_AMBER}55;
            background: {ACCENT_AMBER}14;
            border-radius: 5px;
            padding: 0.12rem 0.45rem;
            letter-spacing: 0.06em;
        }}
 
        /* ---------- module cards (inputs) ---------- */
        .module-card {{
            background: {PANEL};
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 1rem 1.1rem 1.15rem 1.1rem;
            height: 100%;
        }}
        .module-title {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {ACCENT_AMBER};
            margin-bottom: 0.7rem;
            border-bottom: 1px solid {BORDER};
            padding-bottom: 0.55rem;
        }}
 
        /* Streamlit widget re-skin */
        div[data-testid="stNumberInput"] input,
        div[data-testid="stTextInput"] input,
        div[data-baseweb="select"] > div,
        div[data-testid="stDateInput"] input {{
            background-color: {PANEL_RAISED} !important;
            border: 1px solid {BORDER} !important;
            color: {TEXT_PRIMARY} !important;
            font-family: 'IBM Plex Mono', monospace !important;
            border-radius: 6px !important;
        }}
        label, .stRadio label, .stCheckbox label {{
            color: {TEXT_MUTED} !important;
            font-size: 0.85rem !important;
        }}
        div[data-testid="stSlider"] > div > div > div > div {{
            background-color: {ACCENT_AMBER} !important;
        }}
 
        /* ---------- readout row ---------- */
        .readout-panel {{
            background: {PANEL};
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 1.3rem;
            display: flex;
            align-items: center;
            gap: 1.6rem;
            height: 100%;
        }}
        .gauge-wrap {{
            position: relative;
            width: 148px; height: 148px;
            border-radius: 50%;
            flex-shrink: 0;
            display: flex; align-items: center; justify-content: center;
        }}
        .gauge-hole {{
            position: absolute;
            width: 112px; height: 112px;
            border-radius: 50%;
            background: {PANEL};
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
        }}
        .gauge-value {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 1.5rem;
            font-weight: 600;
            color: {TEXT_PRIMARY};
        }}
        .gauge-unit {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.63rem;
            color: {TEXT_MUTED};
            letter-spacing: 0.08em;
            margin-top: 2px;
        }}
 
        .stat-stack {{ display: flex; flex-direction: column; gap: 0.85rem; flex: 1; }}
        .stat-row {{ display: flex; justify-content: space-between; align-items: baseline;
                     border-bottom: 1px dashed {BORDER}; padding-bottom: 0.6rem; }}
        .stat-row:last-child {{ border-bottom: none; }}
        .stat-label {{ font-family: 'IBM Plex Mono', monospace; font-size: 0.74rem;
                       color: {TEXT_MUTED}; letter-spacing: 0.04em; }}
        .stat-value {{ font-family: 'IBM Plex Mono', monospace; font-size: 1.05rem;
                       color: {ACCENT_CYAN}; font-weight: 600; }}
 
        /* ---------- graph / table containers ---------- */
        .panel-frame {{
            background: {PANEL};
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 1rem 1.2rem 0.4rem 1.2rem;
        }}
 
        /* dataframe skin */
        div[data-testid="stDataFrame"] {{
            border: 1px solid {BORDER};
            border-radius: 8px;
            overflow: hidden;
        }}
        /* ---------- tabs ---------- */
                button[data-baseweb="tab"] {{
                    font-family: 'IBM Plex Mono', monospace !important;
                    font-size: 0.8rem !important;
                    letter-spacing: 0.06em;
                    text-transform: uppercase;
                    color: {TEXT_MUTED} !important;
                }}
                button[data-baseweb="tab"][aria-selected="true"] {{
                    color: {ACCENT_AMBER} !important;
                }}
                div[data-baseweb="tab-highlight"] {{
                    background-color: {ACCENT_AMBER} !important;
                }}
                div[data-baseweb="tab-border"] {{
                    background-color: {BORDER} !important;
                }}
        
                /* ---------- recommendation badge ---------- */
                .rec-panel {{
                    background: {PANEL};
                    border: 1px solid {BORDER};
                    border-radius: 10px;
                    padding: 1.3rem 1.6rem;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 1.6rem;
                    height: 100%;
                    flex-wrap: wrap;
                }}
                .rec-metrics {{ display: flex; gap: 2.2rem; flex-wrap: wrap; }}
                .rec-metric-label {{
                    font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem;
                    letter-spacing: 0.06em; color: {TEXT_MUTED}; margin-bottom: 0.25rem;
                }}
                .rec-metric-value {{
                    font-family: 'IBM Plex Mono', monospace; font-size: 1.35rem;
                    font-weight: 600; color: {TEXT_PRIMARY};
                }}
                .rec-badge {{
                    font-family: 'Space Grotesk', sans-serif;
                    font-weight: 700;
                    font-size: 1.15rem;
                    letter-spacing: 0.08em;
                    border-radius: 8px;
                    padding: 0.7rem 1.4rem;
                    white-space: nowrap;
                }}
                .rec-buy {{ color: {ACCENT_CYAN}; border: 1px solid {ACCENT_CYAN}66; background: {ACCENT_CYAN}18; }}
                .rec-sell {{ color: {ACCENT_RED}; border: 1px solid {ACCENT_RED}66; background: {ACCENT_RED}18; }}
                .rec-hold {{ color: {ACCENT_AMBER}; border: 1px solid {ACCENT_AMBER}66; background: {ACCENT_AMBER}18; }}
                </style>
        """,
        unsafe_allow_html=True,
    )
