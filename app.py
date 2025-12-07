import streamlit as st
from pathlib import Path
import sys

# Add app directory to path for imports
app_path = Path(__file__).parent / "app"
sys.path.insert(0, str(app_path))

# Initialize database on startup
from data.db import initialize_database

initialize_database()

from services.user_service import register_user_db, authenticate_user_db

# Configure page - Hide default pages from menu
st.set_page_config(
    page_title="Multi-Domain Intelligence Platform",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide the default Streamlit menu and pages
hide_streamlit_style = """
<style>
    [data-testid="stSidebarNav"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "role" not in st.session_state:
    st.session_state.role = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"


# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.current_page = "home"
    st.rerun()


# =============================
# IF NOT LOGGED IN - SHOW LOGIN/REGISTER
# =============================
if not st.session_state.logged_in:
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<h1 style='text-align: center;'>🔐 Multi-Domain Intelligence Platform</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #666;'>Secure Authentication Portal</h3>",
                    unsafe_allow_html=True)
        st.markdown("---")

        # Create tabs for Login and Register
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

        # =============================
        # LOGIN TAB
        # =============================
        with tab1:
            st.markdown("### Sign In")

            with st.form("login_form"):
                username = st.text_input("👤 Username", placeholder="Enter your username")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")

                submit = st.form_submit_button("🔓 Login", use_container_width=True, type="primary")

                if submit:
                    if not username or not password:
                        st.error("⚠️ Please enter both username and password")
                    else:
                        with st.spinner("🔄 Authenticating..."):
                            success, result = authenticate_user_db(username, password)

                            if success:
                                st.session_state.logged_in = True
                                st.session_state.username = result["username"]
                                st.session_state.user_id = result["id"]
                                st.session_state.role = result["role"]
                                st.session_state.current_page = "home"
                                st.success(f"✅ Welcome back, {username}!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ {result}")

            with st.expander("ℹ️ Need Help?"):
                st.info("If you don't have an account, use the **Register** tab above.")

        # =============================
        # REGISTER TAB
        # =============================
        with tab2:
            st.markdown("### Create New Account")

            with st.form("register_form"):
                new_username = st.text_input("👤 Username", placeholder="Choose a username (min 3 characters)")
                new_password = st.text_input("🔒 Password", type="password",
                                             placeholder="Choose a password (min 6 characters)")
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password")
                role = st.selectbox("👔 Role", ["user", "admin"], index=0)

                submit_register = st.form_submit_button("📝 Create Account", use_container_width=True, type="primary")

                if submit_register:
                    errors = []

                    if not new_username or not new_password:
                        errors.append("Please fill in all fields")
                    if len(new_username) < 3:
                        errors.append("Username must be at least 3 characters")
                    if ',' in new_username or ' ' in new_username:
                        errors.append("Username cannot contain commas or spaces")
                    if len(new_password) < 6:
                        errors.append("Password must be at least 6 characters")
                    if new_password != confirm_password:
                        errors.append("Passwords do not match")

                    if errors:
                        for error in errors:
                            st.error(f"⚠️ {error}")
                    else:
                        success, result = register_user_db(new_username, new_password, role)
                        if success:
                            st.success(f"✅ Account created! User ID: {result}")
                            st.info("Switch to the **Login** tab to sign in.")
                            st.balloons()
                        else:
                            st.error(f"❌ {result}")

        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #666;'><small>🔒 Secure authentication with bcrypt encryption</small></div>",
            unsafe_allow_html=True)

# =============================
# IF LOGGED IN - SHOW DOMAIN SELECTION DASHBOARD
# =============================
else:
    # Sidebar with user info and logout
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        st.markdown(f"**Role:** {st.session_state.role}")
        st.markdown(f"**ID:** {st.session_state.user_id}")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            logout()

    # Main dashboard
    st.title("🎯 Multi-Domain Intelligence Platform")
    st.markdown(f"### Welcome, **{st.session_state.username}**!")
    st.markdown("---")

    st.markdown("## Select Your Domain")
    st.info("Choose a domain to access specialized tools and analytics")

    # Create three columns for domain cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style='padding: 20px; border: 2px solid #4169E1; border-radius: 10px; text-align: center;'>
            <h2>🛡️</h2>
            <h3>Cybersecurity</h3>
            <p>Manage cyber incidents, track threats, and analyze security patterns</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📊 Open Cybersecurity Dashboard", use_container_width=True, type="primary", key="cyber"):
            st.session_state.current_page = "cybersecurity"
            st.switch_page("pages/Cybersecurity.py")

    with col2:
        st.markdown("""
        <div style='padding: 20px; border: 2px solid #FF8C00; border-radius: 10px; text-align: center;'>
            <h2>📊</h2>
            <h3>Data Science</h3>
            <p>Analyze datasets, perform ML tasks, and generate insights</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📊 Open Data Science Dashboard", use_container_width=True, type="primary", key="data"):
            st.session_state.current_page = "data_science"
            st.switch_page("pages/Data_Science.py")

    with col3:
        st.markdown("""
        <div style='padding: 20px; border: 2px solid #32CD32; border-radius: 10px; text-align: center;'>
            <h2>🎫</h2>
            <h3>IT Operations</h3>
            <p>Manage IT tickets, track resolutions, and monitor support metrics</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📊 Open IT Operations Dashboard", use_container_width=True, type="primary", key="it"):
            st.session_state.current_page = "it_operations"
            st.switch_page("pages/IT_Operations.py")

    st.markdown("---")

    # Quick stats section
    st.markdown("## Quick Overview")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("Session Status", "🟢 Active")
    with metric_col2:
        st.metric("Access Level", st.session_state.role.upper())
    with metric_col3:
        st.metric("Available Domains", "3")
    with metric_col4:
        st.metric("Security", "🔒 Encrypted")