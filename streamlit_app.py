# app.py
import streamlit as st
from database import init_db, login_user, register_user

st.set_page_config(page_title="FitMate", page_icon="💪", layout="wide")

# Global styling
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); }
    h1, h2 { color: #1a535c; }
    .stButton>button {
        background-color: #ff6b35; color: white;
        border-radius: 10px; font-weight: bold;
        transition: 0.2s ease;
    }
    .stButton>button:hover { background-color: #e55a2b; transform: translateY(-1px); }
    div[data-testid="stMetricValue"] { color: #1a535c; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff; border-radius: 8px 8px 0 0;
        padding: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)

init_db()

if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None

st.title("💪 FitMate — AI-Powered Fitness Planner")
st.caption("Personalized workouts powered by machine learning")

if st.session_state.user_id is None:
    tab1, tab2 = st.tabs(["🔑 Login", "✨ Register"])

    with tab1:
        st.subheader("Welcome back")
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            ok, uid = login_user(u, p)
            if ok:
                st.session_state.user_id = uid
                st.session_state.username = u
                st.success("Logged in! Redirecting...")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab2:
        st.subheader("Create your account")
        u = st.text_input("Choose a username", key="reg_user")
        p = st.text_input("Choose a password (min 4 chars)", type="password", key="reg_pass")
        if st.button("Register", use_container_width=True):
            if len(u) < 3:
                st.warning("Username must be at least 3 characters.")
            elif len(p) < 4:
                st.warning("Password must be at least 4 characters.")
            else:
                ok, _ = register_user(u, p)
                if ok:
                    st.success("✅ Account created! Please log in.")
                else:
                    st.error("Username already exists.")

else:
    st.sidebar.success(f"👋 Logged in as **{st.session_state.username}**")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()

    st.sidebar.divider()
    st.sidebar.markdown("### How to use FitMate")
    st.sidebar.markdown("""
    1. **👤 Profile** — Set your goals
    2. **📋 Planner** — Get AI recommendations
    3. **✅ Tracker** — Log today's workout
    4. **📊 Dashboard** — See progress
    """)

    st.info("👈 Use the sidebar to navigate between pages.")
    st.markdown("""
    ### Welcome to FitMate!
    
    FitMate uses **machine learning** (TF-IDF + Cosine Similarity) to match your fitness goals, 
    target muscles, and available equipment to a database of **800+ exercises** with 
    step-by-step instructions and demo images.
    
    **Start here →** Open the **Profile** page to enter your details.
    """)





    # streamlit run app.py
