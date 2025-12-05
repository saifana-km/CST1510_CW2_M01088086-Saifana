import streamlit as st
from datetime import datetime
from app.data.db import connect_database
from app.data.incidents import (
    get_all_incidents,
    insert_incident,
    update_incident_status,
    delete_incident
)

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")   # back to the first page
    st.stop()

# If logged in, show dashboard content
st.title("📊 Cyber Incidents Dashboard")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

conn = connect_database('DATA/intelligence_platform.db')
incidents = get_all_incidents()
st.dataframe(incidents, use_container_width=True)

with st.form("new_incident"):
    date = datetime.now().strftime("%Y-%m-%d")
    title = st.text_input("Incident Title")
    severity = st.selectbox("Severity",["Low","Medium","High","Critical"])
    status = st.selectbox("Status",["Open","In Progress", "Resolved"])
    description = st.text_input("Incident Description")
    submitted = st.form_submit_button("Add Incident")

if submitted and title:
    insert_incident(date, title, severity, status, description, reported_by="user")
    st.success("Incident added successfully.")
    st.rerun()

# Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")
