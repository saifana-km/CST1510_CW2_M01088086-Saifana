import streamlit as st
import pandas as pd
from datetime import datetime
from data.db import connect_database
from data.incidents import (
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
st.title("⚠️ Cyber Incident Records")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

# Data display
conn = connect_database('DATA/intelligence_platform.db')
incidents = get_all_incidents()
st.dataframe(incidents, use_container_width=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Incidents", len(incidents))
with col2:
    vulnerabilities = incidents[incidents["severity"].isin(["High", "Critical"])].shape[0]
    st.metric("Severe Vulnerabilities", vulnerabilities)
with col3:
    open_incidents = (incidents["status"] == "Open").sum()
    st.metric("Open Incidents", open_incidents)

threat_counts = incidents["incident_type"].value_counts().to_dict()
st.bar_chart(threat_counts)

# Incident Report
with st.form("new_incident"):
    date = datetime.now().strftime("%Y-%m-%d")
    title = st.text_input("Incident Title")
    severity = st.selectbox("Severity",["Low","Medium","High","Critical"])
    status = st.selectbox("Status",["Open","Investigating","Resolved","Closed"])
    description = st.text_area("Incident Description")
    submitted = st.form_submit_button("Add Incident")

if submitted and title:
    insert_incident(date, title, severity, status, description, reported_by=st.session_state.username)
    st.success("Incident added successfully.")
    st.rerun()

#   Adding Records
if "records" not in st.session_state:
    st.session_state.records = []
with st.form("add_record"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    role = st.selectbox("Role", ["User", "Admin"])
    submitted = st.form_submit_button("Add Record")
if submitted:
    record = {"name": name, "email": email, "role": role}
    st.session_state.records.append(record)
    st.success("Record added!")

#   Displaying Records
if st.session_state.records:
    st.subheader("All Records")
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df,use_container_width=True)
else:
    st.info("No records found")

#   Updating record
if st.session_state.records:
    names = [r["name"] for r in st.session_state.records]
    selected = st.selectbox("Select record", names)
    idx = names.index(selected)
    record = st.session_state.records[idx]
    with st.form("update_form"):
        new_email = st.text_input("Email", record["email"])
        new_role = st.selectbox(
            "Role",
            ["User", "Admin"],
            index=0 if record["role"] == "User" else 1)
        submitted = st.form_submit_button("Update Record")
    if submitted:
        record["email"] = new_email
        record["role"] = new_role
        st.success("Record updated!")

# Deleting record
if st.session_state.records:
    names = [r["name"] for r in st.session_state.records]
    to_delete = st.selectbox("Select record to delete", names)
    col1, col2 = st.columns([3, 1])

    with col1:
        st.warning(f"Delete {to_delete}?")
    with col2:
        if st.button("Delete"):
            idx = names.index(to_delete)
            st.session_state.records.pop(idx)
            st.success("Record deleted!")
            st.rerun()

# Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")
