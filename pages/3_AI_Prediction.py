"""
pages/3_AI_Prediction.py
--------------------------
Form to input a video's stats + title/category and get an ML-predicted
growth category (Low / Medium / High), with probability breakdown.
Saves the prediction to the user's history in SQLite.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import require_login, growth_badge
from prediction import predict_growth
from database import save_prediction

st.set_page_config(page_title="AI Prediction | YouTube Growth Assistant", page_icon="🤖", layout="wide")
require_login()

st.title("🤖 AI Video Growth Prediction")
st.caption("Enter your video's details to predict its growth category using our trained ML model.")

CATEGORIES = ["Tech", "Gaming", "Vlog", "Education", "Comedy", "Music", "Fitness", "Cooking", "Finance", "Beauty"]

with st.form("prediction_form"):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Video Title", placeholder="e.g. Top 10 AI Tools You Need in 2026")
        category = st.selectbox("Category", CATEGORIES)
        duration_sec = st.number_input("Duration (seconds)", min_value=10, max_value=7200, value=600)
        upload_hour = st.slider("Upload Hour (24h format)", 0, 23, 18)
        views = st.number_input("Views", min_value=0, value=5000)
        subscribers_gained = st.number_input("Subscribers Gained", min_value=0, value=50)
    with col2:
        likes = st.number_input("Likes", min_value=0, value=400)
        comments = st.number_input("Comments", min_value=0, value=60)
        shares = st.number_input("Shares", min_value=0, value=30)
        watch_time_sec = st.number_input("Avg Watch Time (seconds)", min_value=0, value=300)
        ctr_percent = st.slider("CTR (%)", 0.0, 20.0, 6.0, step=0.1)
    st.markdown('</div>', unsafe_allow_html=True)

    submitted = st.form_submit_button("🔮 Predict Growth", use_container_width=True)

if submitted:
    if not title.strip():
        st.error("Please enter a video title.")
    else:
        try:
            pred, confidence, proba = predict_growth(
                title=title, category=category, duration_sec=duration_sec,
                upload_hour=upload_hour, views=views, likes=likes, comments=comments,
                shares=shares, watch_time_sec=watch_time_sec, ctr_percent=ctr_percent,
                subscribers_gained=subscribers_gained,
            )
        except FileNotFoundError as e:
            st.error(str(e))
            st.stop()

        st.markdown("### Result")
        st.markdown(growth_badge(pred), unsafe_allow_html=True)
        st.markdown(f"**Confidence:** {confidence}%")

        st.markdown("#### Probability Breakdown")
        proba_display = {k: v for k, v in sorted(proba.items(), key=lambda x: -x[1])}
        st.bar_chart(proba_display)

        save_prediction(st.session_state.user_id, {
            "title": title, "category": category, "duration_sec": duration_sec,
            "upload_hour": upload_hour, "views": views, "likes": likes, "comments": comments,
            "shares": shares, "watch_time_sec": watch_time_sec, "ctr_percent": ctr_percent,
            "subscribers_gained": subscribers_gained, "predicted_growth": pred, "confidence": confidence,
        })
        st.success("Saved to your history. Check the **Dashboard** or **Report** page to view it.")

        if pred == "Low":
            st.warning("💡 This video is predicted for Low growth. Visit **4_Content_Ideas** for AI title, "
                       "description, hashtag, and thumbnail suggestions to improve it.")
        elif pred == "Medium":
            st.info("📈 Solid but there's room to grow — check **4_Content_Ideas** for optimization tips.")
        else:
            st.success("🚀 Great predicted performance! Consider making this a series.")
