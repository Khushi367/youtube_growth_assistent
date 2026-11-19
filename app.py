"""
app.py
------
Main entry point for the AI-Powered YouTube Growth Assistant.

Run with:
    streamlit run app.py

Handles:
  - App-wide config + CSS
  - User registration & login (SQLite via database.py)
  - Landing/welcome screen with feature overview once logged in
  - Logout

Navigate to the other features via the sidebar pages (pages/1..5), which are
automatically discovered by Streamlit's multipage app system.
"""

import streamlit as st
from database import init_db, create_user, verify_user
from utils import load_css

st.set_page_config(
    page_title="YouTube Growth Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
load_css()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None


def show_login_register():
    st.markdown('<div class="auth-title">🚀 YouTube Growth Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="auth-subtitle">AI-powered analytics, predictions & content ideas for creators</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log In", use_container_width=True)
                if submitted:
                    if not username or not password:
                        st.error("Please fill in both fields.")
                    else:
                        user = verify_user(username, password)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user_id = user["id"]
                            st.session_state.username = user["username"]
                            st.success(f"Welcome back, {user['username']}! 🎉")
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")

        with tab_register:
            with st.form("register_form"):
                new_username = st.text_input("Choose a Username")
                new_email = st.text_input("Email")
                channel_name = st.text_input("Channel Name (optional)")
                new_password = st.text_input("Choose a Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                if submitted:
                    if not new_username or not new_email or not new_password:
                        st.error("Please fill in all required fields.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        ok, msg = create_user(new_username, new_email, new_password, channel_name)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)


def show_welcome():
    st.sidebar.success(f"Logged in as **{st.session_state.username}**")
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧭 Navigate")
    st.sidebar.markdown(
        "Use the pages above (**Dashboard, Video Analysis, AI Prediction, "
        "Content Ideas, Report**) to explore each feature."
    )

    st.markdown('<div class="auth-title">Welcome back, ' + st.session_state.username + ' 👋</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="auth-subtitle">Here\'s what you can do with your AI Growth Assistant</div>',
        unsafe_allow_html=True,
    )

    features = [
        ("📊 Dashboard", "Monthly growth overview, KPI cards, engagement & growth trend charts."),
        ("🎥 Video Analysis", "Upload a performance CSV and analyze views, likes, CTR, watch time & more."),
        ("🤖 AI Prediction", "Predict whether a video will get Low / Medium / High growth using ML."),
        ("💡 Content Ideas", "AI-generated titles, descriptions, hashtags, best upload time & thumbnail tips."),
        ("📄 Report", "Download your growth history as a CSV or a polished PDF report."),
    ]

    cols = st.columns(3)
    for i, (title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="section-card" style="min-height: 150px;">
                    <h3 style="margin-top:0;">{title}</h3>
                    <p>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.info("👈 Open the sidebar and pick a page to get started, e.g. **3_AI_Prediction** to try a "
            "growth prediction, or **2_Video_Analysis** to upload your performance CSV.")


if st.session_state.logged_in:
    show_welcome()
else:
    show_login_register()
