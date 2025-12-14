from services.database_manager import DatabaseManager
from services.auth_manager import AuthManager
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[0] 
DB_PATH = str(ROOT / "database" / "platform.db")

# ---------------------------
# Initialize database and auth manager
# ---------------------------
db = DatabaseManager(DB_PATH)
try:
    db.connect()
except Exception as e:
    st.error(f"Could not open database at {DB_PATH}: {e}")
    st.stop()

auth = AuthManager(db)

# ---------------------------
# Session state setup
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

st.title("🔐 Welcome")


if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**.")
    if st.sidebar.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.info("You have been logged out.")
        try:
            st.switch_page("1_Home.py")
        except Exception:
            st.rerun()
    if st.button("Go to dashboard"):
        st.switch_page("pages/2_🛡️_Cybersecurity.py")  # adjust path to your dashboard page
    st.stop()  # Don’t show login/register again

# ---------------------------
# Tabs: Login / Register
# ---------------------------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ---------------------------
# Login Tab
# ---------------------------
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
        user = auth.login_user(login_username, login_password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user.get_username()
            st.session_state.role = user.get_role()
            st.success(f"Welcome back, {user.get_username()}!")
            st.switch_page("pages/2_🛡️_Cybersecurity.py")
        else:
            st.error("Invalid username or password.")


# ---------------------------
# Register Tab
# ---------------------------
with tab_register:
    st.subheader("Register")

    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")

    if st.button("Create account"):
        if not new_username or not new_password:
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            success, message = auth.register_user(new_username, new_password, role="user")
            if success:
                st.success(message)
                st.info("Tip: Go to the Login tab and sign in with your new account.")
            else:
                st.error(message)
