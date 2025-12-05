import streamlit as st
import bcrypt
from data.users import get_user_by_username, insert_user
from services.user_service import register_user

st.set_page_config(page_title="Login / Register", page_icon="🔑", layout="centered")

if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🔐 Welcome")

# If already logged in, go straight to dashboard (optional)
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**.")
    if st.button("Go to dashboard"):
        # Use the official navigation API to switch pages
        st.switch_page("pages/1_Incidents_Dashboard.py")  # path is relative to Home.py :contentReference[oaicite:1]{index=1}
    st.stop()  # Don’t show login/register again


# ---------- Tabs: Login / Register ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
        user = get_user_by_username(login_username)
        if user:
            stored_hash = user["password_hash"].encode("utf-8")
            password_bytes = login_password.encode("utf-8")

            if bcrypt.checkpw(password_bytes, stored_hash):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success(f"Welcome back, {login_username}!")
                st.switch_page("pages/1_Incidents_Dashboard.py")
            else:
                st.error("Invalid username or password.")
        else:
            st.error("Invalid username or password.")


# ----- REGISTER TAB -----

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
            success, message = register_user(new_username, new_password, role="user")
            if success:
                st.success(message)
                st.info("Tip: Go to the Login tab and sign in with your new account.")
            else:
                st.error(message)
