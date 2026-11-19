"""
pages/1_Dashboard.py
---------------------
Monthly channel growth dashboard: KPI cards, engagement charts, and a
monthly growth trend chart built from the logged-in user's saved history.
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import require_login, kpi_card
from database import get_history

st.set_page_config(page_title="Dashboard | YouTube Growth Assistant", page_icon="📊", layout="wide")
require_login()

st.title("📊 Channel Growth Dashboard")
st.caption(f"Overview for **{st.session_state.username}**")

history = get_history(st.session_state.user_id)

if history.empty:
    st.warning(
        "No prediction history yet. Head to **3_AI_Prediction** to analyze a video, "
        "or **2_Video_Analysis** to upload a performance CSV — your results will show up here."
    )
    st.stop()

history["created_at"] = pd.to_datetime(history["created_at"])
history["month"] = history["created_at"].dt.to_period("M").astype(str)

# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------
total_views = int(history["views"].sum())
total_likes = int(history["likes"].sum())
total_comments = int(history["comments"].sum())
avg_ctr = round(history["ctr_percent"].mean(), 2)
total_subs = int(history["subscribers_gained"].sum())

st.markdown("### Key Metrics")
c1, c2, c3, c4, c5 = st.columns(5)
c1.markdown(kpi_card("Total Views", f"{total_views:,}"), unsafe_allow_html=True)
c2.markdown(kpi_card("Total Likes", f"{total_likes:,}"), unsafe_allow_html=True)
c3.markdown(kpi_card("Total Comments", f"{total_comments:,}"), unsafe_allow_html=True)
c4.markdown(kpi_card("Avg CTR", f"{avg_ctr}%"), unsafe_allow_html=True)
c5.markdown(kpi_card("Subscribers Gained", f"{total_subs:,}"), unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Monthly growth trend
# ---------------------------------------------------------------------------
st.markdown("### 📈 Monthly Growth Trend")
monthly = history.groupby("month").agg(
    views=("views", "sum"),
    likes=("likes", "sum"),
    comments=("comments", "sum"),
    subscribers_gained=("subscribers_gained", "sum"),
).reset_index().sort_values("month")

col1, col2 = st.columns(2)
with col1:
    st.line_chart(monthly.set_index("month")[["views"]])
with col2:
    st.bar_chart(monthly.set_index("month")[["subscribers_gained"]])

st.markdown("### 💬 Engagement Breakdown")
col3, col4 = st.columns(2)
with col3:
    st.bar_chart(monthly.set_index("month")[["likes", "comments"]])
with col4:
    growth_counts = history["predicted_growth"].value_counts()
    st.markdown("**Predicted Growth Distribution**")
    st.bar_chart(growth_counts)

st.markdown("---")
st.markdown("### 🗂️ Recent Activity")
st.dataframe(
    history[["created_at", "title", "category", "predicted_growth", "confidence", "views", "ctr_percent"]].head(10),
    use_container_width=True,
)
