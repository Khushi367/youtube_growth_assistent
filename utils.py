"""
utils.py
--------
Small shared helpers used by app.py and every page in pages/:
  - load_css(): injects assets/style.css into the Streamlit app
  - require_login(): guards a page so it can only be viewed while logged in
  - kpi_card() / growth_badge() / hashtag_chips(): reusable HTML snippet builders
"""

import os
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(BASE_DIR, "assets", "style.css")


def load_css():
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def require_login():
    """Call at the top of every page in pages/. Stops execution with a friendly
    message if the user isn't logged in."""
    load_css()
    if not st.session_state.get("logged_in"):
        st.warning("🔒 Please log in from the main page to access this section.")
        st.stop()


def kpi_card(label: str, value: str) -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """


def growth_badge(label: str) -> str:
    css_class = {"High": "growth-high", "Medium": "growth-medium", "Low": "growth-low"}.get(label, "growth-medium")
    emoji = {"High": "🚀", "Medium": "📈", "Low": "🐢"}.get(label, "📊")
    return f'<span class="growth-badge {css_class}">{emoji} {label} Growth</span>'


def hashtag_chips(tags: list) -> str:
    chips = "".join(f'<span class="hashtag-chip">{t}</span>' for t in tags)
    return f'<div>{chips}</div>'
