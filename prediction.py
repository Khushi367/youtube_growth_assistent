"""
prediction.py
--------------
Loads the trained pipeline (models/growth_model.pkl) and exposes a simple
`predict_growth(...)` function used by the Streamlit app.
"""

import os
import joblib
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "growth_model.pkl")

NUMERIC_FEATURES = [
    "duration_sec", "upload_hour", "views", "likes", "comments", "shares",
    "watch_time_sec", "ctr_percent", "subscribers_gained",
    "engagement_rate", "watch_ratio",
]


@st.cache_resource(show_spinner=False)
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


def predict_growth(
    title: str,
    category: str,
    duration_sec: int,
    upload_hour: int,
    views: int,
    likes: int,
    comments: int,
    shares: int,
    watch_time_sec: float,
    ctr_percent: float,
    subscribers_gained: int,
):
    """
    Returns (predicted_label: str, confidence: float, probability_dict: dict)
    """
    model = load_model()
    if model is None:
        raise FileNotFoundError(
            "Model not found. Run `python train_model.py` first to train and save the model."
        )

    engagement_rate = (likes + comments + shares) / max(views, 1)
    watch_ratio = watch_time_sec / max(duration_sec, 1)

    row = pd.DataFrame([{
        "title": title,
        "duration_sec": duration_sec,
        "upload_hour": upload_hour,
        "views": views,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "watch_time_sec": watch_time_sec,
        "ctr_percent": ctr_percent,
        "subscribers_gained": subscribers_gained,
        "engagement_rate": engagement_rate,
        "watch_ratio": watch_ratio,
        "category": category,
    }])

    pred = model.predict(row)[0]
    proba = model.predict_proba(row)[0]
    classes = model.named_steps["classifier"].classes_
    prob_dict = {cls: float(round(p * 100, 2)) for cls, p in zip(classes, proba)}
    confidence = float(round(max(proba) * 100, 2))

    return pred, confidence, prob_dict
