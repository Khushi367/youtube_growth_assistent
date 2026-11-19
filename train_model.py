"""
train_model.py
---------------
Trains the video-growth prediction model.

Features used:
  - Text:    video title -> TF-IDF vector
  - Numeric: duration_sec, upload_hour, views, likes, comments, shares,
             watch_time_sec, ctr_percent, subscribers_gained,
             engagement_rate (engineered), watch_ratio (engineered)
  - Categorical: category (one-hot)

Target:
  - growth_label -> {Low, Medium, High}

Model:
  - RandomForestClassifier inside a scikit-learn Pipeline
    (ColumnTransformer handles TF-IDF + numeric scaling + one-hot together)

Run:
    python train_model.py

Outputs:
    models/growth_model.pkl        -> full sklearn Pipeline (preprocessing + classifier)
    models/tfidf_vectorizer.pkl    -> a *standalone* copy of the fitted TF-IDF vectorizer,
                                       kept separately so other modules (e.g. recommendation.py)
                                       can reuse it without loading the whole pipeline.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "youtube_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "growth_model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")

NUMERIC_FEATURES = [
    "duration_sec", "upload_hour", "views", "likes", "comments", "shares",
    "watch_time_sec", "ctr_percent", "subscribers_gained",
    "engagement_rate", "watch_ratio",
]
CATEGORICAL_FEATURES = ["category"]
TEXT_FEATURE = "title"


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["engagement_rate"] = (df["likes"] + df["comments"] + df["shares"]) / df["views"].replace(0, 1)
    df["watch_ratio"] = df["watch_time_sec"] / df["duration_sec"].replace(0, 1)
    return df


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("title_tfidf", TfidfVectorizer(max_features=300, stop_words="english", ngram_range=(1, 2)), TEXT_FEATURE),
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("category", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )

    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=2,
        random_state=42,
        class_weight="balanced",
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", clf),
    ])
    return pipeline


def main():
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    df = engineer_features(df)

    X = df[[TEXT_FEATURE] + NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df["growth_label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Building pipeline...")
    pipeline = build_pipeline()

    print("Training RandomForestClassifier...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {acc:.4f}\n")
    print(classification_report(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Saved full pipeline -> {MODEL_PATH}")

    # Also save a standalone fitted TF-IDF vectorizer (refit on all titles) so that
    # recommendation.py / other modules can reuse title-similarity features without
    # loading the entire classifier pipeline.
    tfidf_standalone = TfidfVectorizer(max_features=300, stop_words="english", ngram_range=(1, 2))
    tfidf_standalone.fit(df[TEXT_FEATURE])
    joblib.dump(tfidf_standalone, VECTORIZER_PATH)
    print(f"Saved standalone TF-IDF vectorizer -> {VECTORIZER_PATH}")

    print("\nTraining complete.")


if __name__ == "__main__":
    main()
