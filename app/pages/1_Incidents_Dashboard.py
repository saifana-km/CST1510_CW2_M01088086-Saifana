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

# ---------------------------
# Session state setup
# ---------------------------
conn = connect_database()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "form" not in st.session_state:
    st.session_state.form = None

# ---------------------------
# Guard: require login
# ---------------------------
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

# ---------------------------
# Dropdown Navigation
# ---------------------------
SECTIONS = ["Analytics", "Incident Manager", "AI Chat Bot"]

st.sidebar.title("Navigation")
selection = st.sidebar.selectbox("Go to", SECTIONS)

# ---------------------------
# Analytics Section
# ---------------------------
# ---------------------------
# Analytics Section (inline)
# ---------------------------
import altair as alt

if selection == "Analytics":
    st.title("📊 Analytics Dashboard")
    with st.container(border=True):
        st.markdown("*Analysis and visualization of recent, and past Cybersecurity incidents.*")
    st.divider()

    # Load incidents directly from DB
    incidents = pd.read_sql("SELECT * FROM cyber_incidents", conn)

    # ---------------------------
    # Sidebar Filters
    # ---------------------------
    st.sidebar.subheader("Filters")

    # Date range slider
    if not incidents.empty:
        min_date = pd.to_datetime(incidents["date"]).min()
        max_date = pd.to_datetime(incidents["date"]).max()
        date_range = st.sidebar.slider(
            "Select Date Range",
            min_value=min_date.to_pydatetime(),
            max_value=max_date.to_pydatetime(),
            value=(min_date.to_pydatetime(), max_date.to_pydatetime())
        )
        incidents = incidents[
            (pd.to_datetime(incidents["date"]) >= date_range[0]) &
            (pd.to_datetime(incidents["date"]) <= date_range[1])
        ]

    # Severity filter
    severity_filter = st.sidebar.multiselect(
        "Filter by Severity",
        options=["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"]
    )
    incidents = incidents[incidents["severity"].isin(severity_filter)]

    # Status filter
    status_filter = st.sidebar.multiselect(
        "Filter by Status",
        options=["Open", "Investigating", "Resolved", "Closed"],
        default=["Open", "Investigating", "Resolved", "Closed"]
    )
    incidents = incidents[incidents["status"].isin(status_filter)]

    # ---------------------------
    # Display Filtered Data
    # ---------------------------
    st.subheader("Filtered Incidents")
    st.dataframe(incidents, use_container_width=True)

    # ---------------------------
    # Visualizations with Colors
    # ---------------------------
    st.subheader("Visualizations")

    # 1. Incident count by severity (pastel)
    st.write("### Incidents by Severity")
    severity_counts = incidents["severity"].value_counts().reset_index()
    severity_counts.columns = ["severity", "count"]

    severity_chart = alt.Chart(severity_counts).mark_bar().encode(
        x="severity",
        y="count",
        color=alt.Color("severity",
                        scale=alt.Scale(
                            domain=["Critical", "High", "Medium", "Low"],
                            range=["#FFB3B3", "#FFD7A6", "#AFCBFF", "#BFFCC6"]  # pastel red, orange, blue, green
                        ))
    )
    st.altair_chart(severity_chart, use_container_width=True)

    # 2. Incident count by status (pastel)
    st.write("### Incidents by Status")
    status_counts = incidents["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]

    status_chart = alt.Chart(status_counts).mark_bar().encode(
        x="status",
        y="count",
        color=alt.Color("status",
                        scale=alt.Scale(
                            domain=["Open", "Investigating", "Resolved", "Closed"],
                            range=["#B3D9FF", "#FFEBB3", "#C8F7C5", "#E6D5FF"]  # pastel blue, yellow, green, purple
                        ))
    )
    st.altair_chart(status_chart, use_container_width=True)

    # 3. Incident trend over time (soft line)
    st.write("### Incident Trend Over Time")
    if "date" in incidents.columns:
        time_series = incidents.groupby("date").size().reset_index(name="count")
        time_chart = alt.Chart(time_series).mark_line(color="#9BB7D4", point=True).encode(
            x=alt.X("date:T"),
            y=alt.Y("count:Q")
        )
        st.altair_chart(time_chart, use_container_width=True)

    # 4. Incident type distribution (dynamic pastel palette)
    st.write("### Incident Types")
    type_counts = incidents["incident_type"].value_counts().reset_index()
    type_counts.columns = ["incident_type", "count"]

    # create a small pastel palette and repeat if needed
    pastel_palette = ["#FAD9E6", "#DDEBF7", "#E8F8E0", "#FFF1D6", "#F3E8FF", "#FFE4F1", "#EAF6FF", "#FBEEDC"]
    domain = type_counts["incident_type"].tolist()
    # ensure palette is long enough
    palette = (pastel_palette * ((len(domain) // len(pastel_palette)) + 1))[:len(domain)]

    type_chart = alt.Chart(type_counts).mark_bar().encode(
        x="incident_type",
        y="count",
        color=alt.Color("incident_type",
                        scale=alt.Scale(
                            domain=domain,
                            range=palette
                        ))
    )
    st.altair_chart(type_chart, use_container_width=True)

    # ---------------------------
    # Metrics
    # ---------------------------
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Incidents", len(incidents))
    with col2:
        st.metric("Critical/High", incidents[incidents["severity"].isin(["Critical", "High"])].shape[0])
    with col3:
        st.metric("Open/Investigating", incidents[incidents["status"].isin(["Open", "Investigating"])].shape[0])
# ---------------------------
# Incident Manager Section
# ---------------------------
elif selection == "Incident Manager":
    st.title("⚠️ Incident Manager")
    with st.container(border=True):
        st.markdown("*Manage or file a report below. Please insert all required information as instructed.*")
    st.divider()

    # Load incidents for manager actions
    incidents = get_all_incidents()

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
                severity, status, category, title, description,
                created_date, resolved_date or None, assigned_to or None
            )
            st.success(f"Incident {incident_id} created successfully!")
            st.rerun()

    # Search
    elif st.session_state.form == "C":
        with st.form("search_incident"):
            incident_num = st.text_input("Incident ID #")
            submitted = st.form_submit_button("Search Incident")

        if submitted and incident_num:
            formatted_id = incident_num.strip()
            try:
                int(formatted_id)
            except ValueError:
                st.warning("Please enter the number of the incident ID, '500' for example.")
            else:
                # Use the DataFrame loaded above; schema uses 'id' as primary key
                if incidents is None:
                    incidents = get_all_incidents()
                if "id" in incidents.columns:
                    match = incidents[incidents["id"].astype(str) == formatted_id]
                else:
                    match = pd.DataFrame()
                if not match.empty:
                    st.write("### Incident Details")
                    st.dataframe(match, use_container_width=True)
                else:
                    st.warning(f"No incident found with ID {formatted_id}")

    # Delete
    elif st.session_state.form == "D":
        with st.form("delete_incident"):
            incident_id = st.text_input("Incident ID #")
            confirm = st.checkbox("I understand this will permanently delete the incident")
            submitted = st.form_submit_button("Delete Incident")

        if submitted and incident_id:
            formatted_id = incident_id.strip()
            try:
                int(formatted_id)
            except ValueError:
                st.warning("Please enter the number of the incident ID, '500' for example.")
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
            incident_id = st.text_input("Incident ID #")
            new_status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
            submitted = st.form_submit_button("Update Incident")

        if submitted and incident_id:
            formatted_id = incident_id.strip()
            try:
                int(formatted_id)
            except ValueError:
                st.warning("Please enter the number of the incident ID, '500' for example.")
            else:
                updated = update_incident_status(conn, formatted_id, new_status)
                if updated:
                    st.success(f"Incident {formatted_id} updated to {new_status} successfully!")
                else:
                    st.error(f"Failed to update incident {formatted_id}.")
                st.rerun()

# ---------------------------
# AI Chat Bot Section
# ---------------------------
elif selection == "AI Chat Bot":
    st.title("🤖 AI Chat Bot")
    st.info("This section is a placeholder for future AI chat functionality.")

# ---------------------------
# Logout
# ---------------------------
st.sidebar.divider()
if st.sidebar.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")