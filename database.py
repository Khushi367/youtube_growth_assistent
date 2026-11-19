"""
database.py
-----------
Handles all SQLite database operations for the YouTube Growth Assistant:
- User registration & login (passwords stored as salted SHA-256 hashes)
- Saving / fetching prediction history per user
- Saving / fetching monthly channel snapshots for the dashboard
"""

import sqlite3
import hashlib
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube_growth.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't already exist. Safe to call every app run."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            channel_name TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            category TEXT,
            duration_sec INTEGER,
            upload_hour INTEGER,
            views INTEGER,
            likes INTEGER,
            comments INTEGER,
            shares INTEGER,
            watch_time_sec REAL,
            ctr_percent REAL,
            subscribers_gained INTEGER,
            predicted_growth TEXT,
            confidence REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS monthly_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            total_views INTEGER,
            total_likes INTEGER,
            total_comments INTEGER,
            total_subscribers_gained INTEGER,
            avg_ctr REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Password hashing helpers
# ---------------------------------------------------------------------------

def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def create_user(username: str, email: str, password: str, channel_name: str = "") -> tuple[bool, str]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        salt = uuid.uuid4().hex
        pwd_hash = _hash_password(password, salt)
        cur.execute(
            "INSERT INTO users (username, email, password_hash, salt, channel_name, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (username.strip(), email.strip().lower(), pwd_hash, salt, channel_name.strip(),
             datetime.now().isoformat()),
        )
        conn.commit()
        return True, "Account created successfully. Please log in."
    except sqlite3.IntegrityError:
        return False, "Username or email already exists."
    finally:
        conn.close()


def verify_user(username: str, password: str):
    """Returns the user row (sqlite3.Row) if credentials are valid, else None."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username.strip(),))
    user = cur.fetchone()
    conn.close()
    if user is None:
        return None
    if _hash_password(password, user["salt"]) == user["password_hash"]:
        return user
    return None


def get_user_by_id(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------

def save_prediction(user_id: int, record: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO history (
            user_id, title, category, duration_sec, upload_hour, views, likes, comments,
            shares, watch_time_sec, ctr_percent, subscribers_gained, predicted_growth,
            confidence, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, record.get("title"), record.get("category"), record.get("duration_sec"),
        record.get("upload_hour"), record.get("views"), record.get("likes"),
        record.get("comments"), record.get("shares"), record.get("watch_time_sec"),
        record.get("ctr_percent"), record.get("subscribers_gained"),
        record.get("predicted_growth"), record.get("confidence"),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


def get_history(user_id: int):
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM history WHERE user_id = ? ORDER BY created_at DESC", conn, params=(user_id,)
    )
    conn.close()
    return df


def save_monthly_snapshot(user_id: int, snapshot: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO monthly_snapshots (
            user_id, month, total_views, total_likes, total_comments,
            total_subscribers_gained, avg_ctr, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, snapshot.get("month"), snapshot.get("total_views"),
        snapshot.get("total_likes"), snapshot.get("total_comments"),
        snapshot.get("total_subscribers_gained"), snapshot.get("avg_ctr"),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


def get_monthly_snapshots(user_id: int):
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM monthly_snapshots WHERE user_id = ? ORDER BY month ASC", conn, params=(user_id,)
    )
    conn.close()
    return df
