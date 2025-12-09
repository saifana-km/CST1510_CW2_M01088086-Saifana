import streamlit as st
import pandas as pd
from datetime import datetime
from data.db import connect_database
from data.incidents import (
    get_all_incidents,
    insert_incident,
    update_incident_status,
    delete_incident,
    search_incident
)

conn = connect_database()

# Ensure session state keys exist
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "form" not in st.session_state:
    st.session_state.form = None

# Guard: require login
if not st.session_state.logged_in:
    st.error("You must be logged in to view the incidents dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

st.title("⚠️ Incidents Dashboard")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

# Use same DB path as other pages (adjust if needed)
conn = connect_database('DATA/intelligence_platform.db')
incidents = get_all_incidents()
st.dataframe(incidents, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Incidents", len(incidents))
with col2:
    high_sev = incidents[incidents.get("severity", "").isin(["High", "Critical"])].shape[0]
    st.metric("High Severity", high_sev)
with col3:
    open_inc = incidents[incidents.get("status", "").isin(["Open", "Investigating"])].shape[0]
    st.metric("Open Incidents", open_inc)

# Simple breakdown chart if category column exists
if "category" in incidents.columns:
    cat_counts = incidents["category"].value_counts().to_dict()
    st.bar_chart(cat_counts)

st.subheader("Incident Manager")
cola, colb, colc, cold = st.columns(4)
with cola:
    if st.button("Insert Incident"):
        st.session_state.form = "A"
with colb:
    if st.button("Update Incident"):
        st.session_state.form = "B"
with colc:
    if st.button("Search Incident"):
        st.session_state.form = "C"
with cold:
    if st.button("Delete Incident"):
        st.session_state.form = "D"

# Create
if st.session_state.form == "A":
    with st.form("new_incident"):
        title = st.text_input("Title")
        category = st.text_input("Category")
        description = st.text_area("Description")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
        created_date = datetime.now().strftime("%Y-%m-%d")
        resolved_date = st.text_input("Resolved Date (YYYY-MM-DD)")
        assigned_to = st.text_input("Assigned To")
        submitted = st.form_submit_button("Create Incident")

    if submitted:
        incident_id = insert_incident(
            severity, status, category, title, description, created_date, resolved_date or None, assigned_to or None
        )
        st.success(f"Incident {incident_id} created successfully!")
        st.rerun()

# Search
elif st.session_state.form == "C":
    with st.form("search_incident"):
        incident_num = st.text_input("Incident ID")
        submitted = st.form_submit_button("Search Incident")

    if submitted and incident_num:
        # Use plain numeric IDs (no INC- prefix). Trim whitespace.
        formatted_id = incident_num.strip()
        # Optional validation: ensure numeric input
        try:
            int(formatted_id)
        except ValueError:
            st.warning("Please enter a numeric incident ID.")
        else:
            # Prefer in-memory dataframe
            if "incidents" in locals() or "incidents" in globals():
                if "incident_id" in incidents.columns:
                    # Compare as strings to be robust to int/text DB column types
                    match = incidents[incidents["incident_id"].astype(str) == formatted_id]
                else:
                    match = pd.DataFrame()
                if not match.empty:
                    st.write("### Incident Details")
                    st.dataframe(match, use_container_width=True)
                else:
                    st.warning(f"No incident found with ID {formatted_id}")
            else:
                result = search_incident(conn, formatted_id)
                if result is not None:
                    st.write("### Incident Details")
                    st.table(result)
                else:
                    st.warning(f"No incident found with ID {formatted_id}")

# Delete
elif st.session_state.form == "D":
    with st.form("delete_incident"):
        incident_id = st.text_input("Incident ID")
        confirm = st.checkbox("I understand this will permanently delete the incident")
        submitted = st.form_submit_button("Delete Incident")

    if submitted and incident_id:
        formatted_id = incident_id.strip()
        try:
            int(formatted_id)
        except ValueError:
            st.warning("Please enter a numeric incident ID.")
        else:
            if not confirm:
                st.warning("Please confirm deletion by checking the box.")
            else:
                deleted = delete_incident(conn, formatted_id)
                if deleted and deleted > 0:
                    st.success(f"Incident {formatted_id} deleted!")
                else:
                    st.error(f"No incident found with ID {formatted_id}")
                st.rerun()

# Update
elif st.session_state.form == "B":
    with st.form("update_incident"):
        incident_id = st.text_input("Incident ID")
        new_status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
        submitted = st.form_submit_button("Update Incident")

    if submitted and incident_id:
        formatted_id = incident_id.strip()
        try:
            int(formatted_id)
        except ValueError:
            st.warning("Please enter a numeric incident ID.")
        else:
            updated = update_incident_status(conn, formatted_id, new_status)
            if updated:
                st.success(f"Incident {formatted_id} updated to {new_status} successfully!")
            else:
                st.error(f"Failed to update incident {formatted_id}.")
            st.rerun()

# Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")