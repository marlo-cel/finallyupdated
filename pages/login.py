import streamlit as st
from pathlib import Path
import sys

# Add app directory to path for imports
app_path = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_path))

from services.user_service import register_user_db, authenticate_user_db

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "role" not in st.session_state:
    st.session_state.role = None


# Logout handler
def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.role = None
    st.success("✅ Logged out successfully!")
    st.rerun()


# Header
st.title("🔐 Authentication Portal")
st.markdown("### Multi-Domain Intelligence Platform")
st.markdown("---")

# Check if already logged in
if st.session_state.logged_in:
    st.success(f"✅ You are logged in as **{st.session_state.username}** ({st.session_state.role})")

    st.info("🎯 Navigate to the **Dashboard** using the sidebar to start managing incidents.")

    st.markdown("### Account Information")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Username", st.session_state.username)
        st.metric("User ID", st.session_state.user_id)
    with col2:
        st.metric("Role", st.session_state.role.upper())
        st.metric("Status", "🟢 Active")

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            logout()

    st.stop()

# Create tabs for Login and Register
tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

# =============================
# LOGIN TAB
# =============================
with tab1:
    st.markdown("### 🔓 Sign In to Your Account")
    st.markdown("Enter your credentials to access the platform")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "👤 Username",
            placeholder="Enter your username",
            key="login_username"
        )
        password = st.text_input(
            "🔒 Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )

        st.markdown("")  # Spacing
        submit = st.form_submit_button(
            "🔓 Login",
            use_container_width=True,
            type="primary"
        )

        if submit:
            if not username or not password:
                st.error("⚠️ Please enter both username and password")
            else:
                with st.spinner("🔄 Authenticating..."):
                    success, result = authenticate_user_db(username, password)

                    if success:
                        # Store user info in session state
                        st.session_state.logged_in = True
                        st.session_state.username = result["username"]
                        st.session_state.user_id = result["id"]
                        st.session_state.role = result["role"]

                        st.success(f"✅ Welcome back, **{username}**!")
                        st.balloons()
                        st.info("🔄 Redirecting to dashboard...")
                        st.rerun()
                    else:
                        st.error(f"❌ Login failed: {result}")
                        st.warning(
                            "💡 Hint: Check your username and password, or register a new account in the Register tab.")

    # Help section
    with st.expander("ℹ️ Need Help?"):
        st.markdown("""
        **Having trouble logging in?**
        - Make sure your username and password are correct
        - Usernames are case-sensitive
        - If you don't have an account, use the Register tab

        **Test Account (if available):**
        - Username: `Alex`
        - Password: Check with your instructor
        """)

# =============================
# REGISTER TAB
# =============================
with tab2:
    st.markdown("### 📝 Create a New Account")
    st.markdown("Join the Multi-Domain Intelligence Platform")

    with st.form("register_form", clear_on_submit=True):
        new_username = st.text_input(
            "👤 Username",
            placeholder="Choose a username (3-20 characters)",
            key="register_username",
            help="Username must be at least 3 characters and cannot contain commas or spaces"
        )

        col1, col2 = st.columns(2)
        with col1:
            new_password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Min 6 characters",
                key="register_password",
                help="Choose a strong password with at least 6 characters"
            )
        with col2:
            confirm_password = st.text_input(
                "🔒 Confirm Password",
                type="password",
                placeholder="Re-enter password",
                key="confirm_password"
            )

        role = st.selectbox(
            "👔 Role",
            ["user", "admin"],
            index=0,
            help="Select your role: 'user' for standard access, 'admin' for full privileges"
        )

        # Password strength indicator
        if new_password:
            strength = "Weak" if len(new_password) < 8 else "Medium" if len(new_password) < 12 else "Strong"
            color = "🔴" if strength == "Weak" else "🟡" if strength == "Medium" else "🟢"
            st.info(f"{color} Password Strength: **{strength}**")

        st.markdown("")  # Spacing
        submit_register = st.form_submit_button(
            "📝 Create Account",
            use_container_width=True,
            type="primary"
        )

        if submit_register:
            # Validation
            errors = []

            if not new_username or not new_password:
                errors.append("⚠️ Please fill in all required fields")

            if new_username and len(new_username) < 3:
                errors.append("⚠️ Username must be at least 3 characters long")

            if new_username and (',' in new_username or ' ' in new_username):
                errors.append("⚠️ Username cannot contain commas or spaces")

            if new_password and len(new_password) < 6:
                errors.append("⚠️ Password must be at least 6 characters long")

            if new_password != confirm_password:
                errors.append("⚠️ Passwords do not match")

            # Display errors
            if errors:
                for error in errors:
                    st.error(error)
            else:
                with st.spinner("🔄 Creating your account..."):
                    success, result = register_user_db(new_username, new_password, role)

                    if success:
                        st.success(f"✅ Account created successfully!")
                        st.success(f"🆔 Your User ID: **{result}**")
                        st.success(f"👤 Username: **{new_username}**")
                        st.success(f"👔 Role: **{role}**")
                        st.balloons()
                        st.info("🔑 You can now login with your credentials in the **Login** tab above!")
                    else:
                        st.error(f"❌ Registration failed: {result}")

    # Registration requirements
    with st.expander("📋 Registration Requirements"):
        st.markdown("""
        **Username Requirements:**
        - ✅ At least 3 characters long
        - ✅ No commas or spaces
        - ✅ Must be unique

        **Password Requirements:**
        - ✅ At least 6 characters (8+ recommended)
        - ✅ Will be securely encrypted

        **Roles:**
        - 👤 **User**: Standard access to view and manage incidents
        - 👑 **Admin**: Full access with additional privileges
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>🔒 Security Features</strong></p>
    <p>🔐 Bcrypt password encryption | 🛡️ Secure session management | 🔑 Role-based access control</p>
    <br>
    <small>Multi-Domain Intelligence Platform | CST1510 CW2</small>
</div>
""", unsafe_allow_html=True)