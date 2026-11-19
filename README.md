# 🚀 AI-Powered YouTube Growth Assistant

A complete Streamlit web app that helps YouTubers analyze video performance and get AI/ML-based
growth suggestions — title & hashtag generation, growth prediction, best upload time, thumbnail
tips, and downloadable reports.

---

## ✨ Features

1. **User login & registration** (SQLite, salted password hashing)
2. **Upload YouTube video performance CSV** and analyze it instantly
3. Analyze **views, likes, comments, shares, watch time, CTR, subscribers gained**
4. **Predict video growth**: Low / Medium / High, using a trained ML model
5. **AI title suggestions** based on topic/category (NLP rule-based generation)
6. **AI description + hashtag generator**
7. **Best upload time recommendation** (learned from historical data per category)
8. **Thumbnail improvement suggestions**
9. **Audience engagement analysis** (engagement rate, watch ratio, CTR health check)
10. **Monthly channel growth dashboard** with KPI cards & charts
11. **User history stored in SQLite** (`youtube_growth.db`, auto-created)
12. **Download growth report** as CSV or PDF
13. Clean, **animated gradient Streamlit UI**

---

## 🧠 ML / NLP Details

- **Input features:** video title (text), category, duration, upload hour, views, likes,
  comments, shares, CTR, watch time, subscribers gained (+ engineered engagement rate & watch ratio)
- **Text features:** TF-IDF vectorization of the video title (unigrams + bigrams, 300 features)
- **Model:** `RandomForestClassifier` inside a scikit-learn `Pipeline`
  (`ColumnTransformer` combines TF-IDF + `StandardScaler` numeric features + one-hot category)
- **Output:** predicted growth category — `Low`, `Medium`, or `High` — with per-class probabilities
- **NLP suggestions:** deterministic, rule/template-based generators for titles, descriptions,
  and hashtags (fully offline, no external API calls required)
- **Persistence:** trained pipeline saved with `joblib` to `models/growth_model.pkl`; a standalone
  TF-IDF vectorizer is also saved to `models/tfidf_vectorizer.pkl` for reuse

> The bundled `data/youtube_data.csv` is a synthetic sample dataset (900 rows) used to train the
> demo model out of the box. Replace it with your own real channel data (same column schema) and
> re-run `train_model.py` to retrain on your data.

---

## 📁 Folder Structure

```
youtube_growth_assistant/
│── app.py                     # Main entry point (login/register + welcome)
│── database.py                # SQLite: users, history, monthly snapshots
│── train_model.py             # Trains & saves the ML growth model
│── prediction.py              # Loads model, exposes predict_growth()
│── recommendation.py          # NLP rule-based content suggestions
│── utils.py                   # Shared UI helpers (CSS, KPI cards, auth guard)
│── requirements.txt
│── README.md
│
├── data/
│   └── youtube_data.csv       # Sample training data
│
├── models/
│   ├── growth_model.pkl       # Trained sklearn Pipeline (created by train_model.py)
│   └── tfidf_vectorizer.pkl   # Standalone TF-IDF vectorizer
│
├── pages/                     # Streamlit multipage app pages
│   ├── 1_Dashboard.py
│   ├── 2_Video_Analysis.py
│   ├── 3_AI_Prediction.py
│   ├── 4_Content_Ideas.py
│   └── 5_Report.py
│
├── assets/
│   └── style.css              # Animated gradient UI styling
│
└── reports/                   # (created on demand when exporting PDF/CSV)
```

---

## ⚙️ Setup & Run

### 1. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate       # on Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Train the ML model

This reads `data/youtube_data.csv`, trains the RandomForest growth-prediction pipeline, and
saves it to `models/growth_model.pkl` (+ `models/tfidf_vectorizer.pkl`).

```bash
python train_model.py
```

You should see a test accuracy and classification report printed in the terminal.

### 4. Run the Streamlit app

```bash
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`) in your browser.

### 5. First-time use

1. Go to the **Register** tab and create an account.
2. Log in.
3. Use the sidebar to navigate:
   - **1_Dashboard** — overview once you have history
   - **2_Video_Analysis** — upload a performance CSV
   - **3_AI_Prediction** — predict growth for a video (saves to your history)
   - **4_Content_Ideas** — AI titles, descriptions, hashtags, upload time, thumbnail tips
   - **5_Report** — download your history as CSV or PDF

---

## 🔁 Retraining on Your Own Data

Replace `data/youtube_data.csv` with your own export, keeping these columns:

```
title, category, duration_sec, upload_hour, views, likes, comments, shares,
watch_time_sec, ctr_percent, subscribers_gained, growth_label
```

`growth_label` must be one of `Low`, `Medium`, `High` for supervised training. If you don't have
labels yet, you can bootstrap them from a composite engagement score (see the labeling logic at
the bottom of the dataset-generation section in `train_model.py`'s docstring, or roll your own
business rule) — then run:

```bash
python train_model.py
```

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit (multipage app, custom CSS for animated gradient UI)
- **ML:** scikit-learn (`RandomForestClassifier`, `TfidfVectorizer`, `ColumnTransformer`, `Pipeline`)
- **Persistence:** SQLite (`sqlite3`), `joblib` for model serialization
- **Reporting:** `reportlab` for PDF generation, native `pandas` CSV export

---

## 📌 Notes

- Passwords are stored as salted SHA-256 hashes (never plaintext).
- The SQLite database file (`youtube_growth.db`) is created automatically on first run in the
  project root.
- All NLP suggestions are generated locally with rule/template-based logic — no external API key
  is required to run this project.
