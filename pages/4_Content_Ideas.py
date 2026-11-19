"""
pages/4_Content_Ideas.py
--------------------------
AI (NLP rule-based) content generation: title suggestions, description +
hashtags, best upload time recommendation, thumbnail improvement tips,
and a quick audience engagement analysis.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import require_login, hashtag_chips
from recommendation import (
    generate_title_suggestions, generate_description, generate_hashtags,
    best_upload_time, thumbnail_suggestions, analyze_engagement,
)

st.set_page_config(page_title="Content Ideas | YouTube Growth Assistant", page_icon="💡", layout="wide")
require_login()

st.title("💡 AI Content Idea Generator")
st.caption("Get AI-generated titles, descriptions, hashtags, upload time & thumbnail tips.")

CATEGORIES = ["Tech", "Gaming", "Vlog", "Education", "Comedy", "Music", "Fitness", "Cooking", "Finance", "Beauty"]

col1, col2 = st.columns(2)
with col1:
    topic = st.text_input("Video Topic / Keyword", placeholder="e.g. AI Productivity Tools")
with col2:
    category = st.selectbox("Category", CATEGORIES)

generate = st.button("✨ Generate Ideas", use_container_width=True)

if generate:
    if not topic.strip():
        st.error("Please enter a topic or keyword.")
    else:
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📝 Titles", "📄 Description & Hashtags", "⏰ Best Upload Time", "🖼️ Thumbnail Tips"]
        )

        with tab1:
            st.markdown("#### AI-Suggested Titles")
            titles = generate_title_suggestions(topic, category)
            for i, t in enumerate(titles, 1):
                st.markdown(f'<div class="section-card">**{i}.** {t}</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown("#### AI-Generated Description")
            description = generate_description(topic, category)
            st.text_area("Description", description, height=220)

            st.markdown("#### Suggested Hashtags")
            tags = generate_hashtags(topic, category)
            st.markdown(hashtag_chips(tags), unsafe_allow_html=True)

        with tab3:
            st.markdown("#### Recommended Upload Time")
            rec = best_upload_time(category)
            st.markdown(
                f"""
                <div class="section-card">
                    <h3 style="margin-top:0;">🕒 {rec['window']}</h3>
                    <p>{rec['note']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with tab4:
            st.markdown("#### Thumbnail Improvement Suggestions")
            tips = thumbnail_suggestions(6)
            for tip in tips:
                st.markdown(f"- {tip}")

st.markdown("---")
st.markdown("### 📊 Quick Engagement Analysis")
st.caption("Enter a video's stats to get a quick engagement health check.")

with st.form("engagement_form"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        views_e = st.number_input("Views", min_value=0, value=5000, key="eng_views")
        likes_e = st.number_input("Likes", min_value=0, value=300, key="eng_likes")
    with c2:
        comments_e = st.number_input("Comments", min_value=0, value=40, key="eng_comments")
        shares_e = st.number_input("Shares", min_value=0, value=15, key="eng_shares")
    with c3:
        ctr_e = st.slider("CTR (%)", 0.0, 20.0, 5.0, step=0.1, key="eng_ctr")
        duration_e = st.number_input("Duration (sec)", min_value=10, value=600, key="eng_duration")
    with c4:
        watch_e = st.number_input("Avg Watch Time (sec)", min_value=0, value=200, key="eng_watch")
    analyze = st.form_submit_button("Analyze Engagement", use_container_width=True)

if analyze:
    result = analyze_engagement(views_e, likes_e, comments_e, shares_e, ctr_e, watch_e, duration_e)
    c1, c2, c3 = st.columns(3)
    c1.metric("Engagement Rate", f"{result['engagement_rate_percent']}%")
    c2.metric("Watch Ratio", f"{result['watch_ratio_percent']}%")
    c3.metric("CTR", f"{result['ctr_percent']}%")
    st.markdown("#### Recommendations")
    for tip in result["tips"]:
        st.markdown(f"- {tip}")
