"""
pages/2_Video_Analysis.py
---------------------------
Upload a YouTube video performance CSV and analyze views, likes, comments,
shares, watch time, CTR and subscribers gained with interactive charts.

Expected CSV columns (case-insensitive, flexible naming handled below):
    title, category, duration_sec, upload_hour, views, likes, comments,
    shares, watch_time_sec, ctr_percent, subscribers_gained
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import require_login, kpi_card

st.set_page_config(page_title="Video Analysis | YouTube Growth Assistant", page_icon="🎥", layout="wide")
require_login()

st.title("🎥 Video Performance Analysis")
st.caption("Upload your YouTube video performance CSV to get an instant breakdown.")

COLUMN_ALIASES = {
    "title": ["title", "video_title", "video title"],
    "category": ["category", "genre", "niche"],
    "duration_sec": ["duration_sec", "duration", "duration_seconds"],
    "upload_hour": ["upload_hour", "hour", "publish_hour"],
    "views": ["views", "view_count"],
    "likes": ["likes", "like_count"],
    "comments": ["comments", "comment_count"],
    "shares": ["shares", "share_count"],
    "watch_time_sec": ["watch_time_sec", "watch_time", "avg_watch_time"],
    "ctr_percent": ["ctr_percent", "ctr", "click_through_rate"],
    "subscribers_gained": ["subscribers_gained", "subs_gained", "new_subscribers"],
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    rename_map = {}
    for standard, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            alias_norm = alias.strip().lower().replace(" ", "_")
            if alias_norm in df.columns and standard not in df.columns:
                rename_map[alias_norm] = standard
    return df.rename(columns=rename_map)


sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "youtube_data.csv")

with st.expander("📄 Need a sample CSV format?"):
    st.write(
        "Your file should include columns similar to: `title, category, duration_sec, upload_hour, "
        "views, likes, comments, shares, watch_time_sec, ctr_percent, subscribers_gained`"
    )
    if os.path.exists(sample_path):
        with open(sample_path, "rb") as f:
            st.download_button("⬇️ Download Sample CSV", f, file_name="sample_youtube_data.csv")

uploaded_file = st.file_uploader("Upload video performance CSV", type=["csv"])

if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
        df = normalize_columns(raw_df)
    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        st.stop()

    numeric_cols = ["views", "likes", "comments", "shares", "watch_time_sec", "ctr_percent", "subscribers_gained"]
    missing = [c for c in numeric_cols if c not in df.columns]
    if missing:
        st.error(f"Your CSV is missing required columns: {', '.join(missing)}")
        st.stop()

    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    st.success(f"Loaded {len(df)} videos successfully.")

    # KPI summary
    st.markdown("### Key Metrics (Aggregate)")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(kpi_card("Total Views", f"{int(df['views'].sum()):,}"), unsafe_allow_html=True)
    c2.markdown(kpi_card("Total Likes", f"{int(df['likes'].sum()):,}"), unsafe_allow_html=True)
    c3.markdown(kpi_card("Total Comments", f"{int(df['comments'].sum()):,}"), unsafe_allow_html=True)
    c4.markdown(kpi_card("Avg CTR", f"{round(df['ctr_percent'].mean(),2)}%"), unsafe_allow_html=True)
    c5.markdown(kpi_card("Subs Gained", f"{int(df['subscribers_gained'].sum()):,}"), unsafe_allow_html=True)

    st.markdown("---")

    # Engagement rate & watch ratio (engineered)
    df["engagement_rate_%"] = ((df["likes"] + df["comments"] + df["shares"]) / df["views"].replace(0, 1) * 100).round(2)
    if "duration_sec" in df.columns:
        df["watch_ratio_%"] = (df["watch_time_sec"] / df["duration_sec"].replace(0, 1) * 100).round(2)

    st.markdown("### 📈 Views vs Engagement")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top 10 Videos by Views**")
        top_views = df.nlargest(10, "views")[["title", "views"]].set_index("title") if "title" in df.columns else df.nlargest(10, "views")[["views"]]
        st.bar_chart(top_views)
    with col2:
        st.markdown("**CTR Distribution**")
        st.bar_chart(df["ctr_percent"])

    st.markdown("### 💬 Engagement Rate by Video")
    if "title" in df.columns:
        st.bar_chart(df.set_index("title")["engagement_rate_%"])
    else:
        st.bar_chart(df["engagement_rate_%"])

    if "category" in df.columns:
        st.markdown("### 🗂️ Performance by Category")
        cat_summary = df.groupby("category").agg(
            avg_views=("views", "mean"),
            avg_ctr=("ctr_percent", "mean"),
            avg_engagement=("engagement_rate_%", "mean"),
        ).round(2)
        st.dataframe(cat_summary, use_container_width=True)
        st.bar_chart(cat_summary["avg_views"])

    st.markdown("### 🔍 Full Data")
    st.dataframe(df, use_container_width=True)

    st.session_state["last_uploaded_df"] = df
    st.info("💡 Tip: Head to **3_AI_Prediction** to predict growth for individual videos from this list, "
            "or **5_Report** to export insights.")
else:
    st.info("Upload a CSV file to begin analysis.")
