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
SECTIONS = ["Analytics", "Incidents Manager", "AI Chat Bot"]

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
    st.title("📊 Cybersecurity Analytics")
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
    # Display Filtered Data (inside an expander)
    # ---------------------------
    with st.expander("Filtered Incidents (click to expand)", expanded=False):
        st.dataframe(incidents, use_container_width=True)

    # ---------------------------
    # Visualizations (inside an expander + dropdown)
    # ---------------------------
    with st.expander("Visualizations (click to expand)", expanded=False):
        st.write("Choose a chart from the dropdown to display it.")
        chart_choice = st.selectbox("Select chart", [
            "Incidents by Severity",
            "Incidents by Status",
            "Incident Trend Over Time",
            "Incident Types"
        ])

        # 1. Incidents by Severity
        if chart_choice == "Incidents by Severity" and not incidents.empty:
            severity_counts = incidents["severity"].value_counts().reset_index()
            severity_counts.columns = ["severity", "count"]
            severity_chart = alt.Chart(severity_counts).mark_bar().encode(
                x="severity",
                y="count",
                color=alt.Color("severity",
                                scale=alt.Scale(
                                    domain=["Critical", "High", "Medium", "Low"],
                                    range=["#FFB3B3", "#FFD7A6", "#AFCBFF", "#BFFCC6"]
                                ))
            )
            st.altair_chart(severity_chart, use_container_width=True)

        # 2. Incidents by Status
        if chart_choice == "Incidents by Status" and not incidents.empty:
            status_counts = incidents["status"].value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            status_chart = alt.Chart(status_counts).mark_bar().encode(
                x="status",
                y="count",
                color=alt.Color("status",
                                scale=alt.Scale(
                                    domain=["Open", "Investigating", "Resolved", "Closed"],
                                    range=["#B3D9FF", "#FFEBB3", "#C8F7C5", "#E6D5FF"]
                                ))
            )
            st.altair_chart(status_chart, use_container_width=True)

        # 3. Incident trend over time
        if chart_choice == "Incident Trend Over Time" and not incidents.empty and "date" in incidents.columns:
            time_series = incidents.groupby("date").size().reset_index(name="count")
            time_chart = alt.Chart(time_series).mark_line(color="#9BB7D4", point=True).encode(
                x=alt.X("date:T"),
                y=alt.Y("count:Q")
            )
            st.altair_chart(time_chart, use_container_width=True)

        # 4. Incident type distribution
        if chart_choice == "Incident Types" and not incidents.empty:
            type_counts = incidents["incident_type"].value_counts().reset_index()
            type_counts.columns = ["incident_type", "count"]
            pastel_palette = ["#FAD9E6", "#DDEBF7", "#E8F8E0", "#FFF1D6", "#F3E8FF", "#FFE4F1", "#EAF6FF", "#FBEEDC"]
            domain = type_counts["incident_type"].tolist()
            palette = (pastel_palette * ((len(domain) // len(pastel_palette)) + 1))[:len(domain)]
            type_chart = alt.Chart(type_counts).mark_bar().encode(
                x="incident_type",
                y="count",
                color=alt.Color("incident_type",
                                scale=alt.Scale(domain=domain, range=palette))
            )
            st.altair_chart(type_chart, use_container_width=True)

    # ---------------------------
    # Metrics (unchanged)
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
elif selection == "Incidents Manager":
    st.title("⚠️ Incidents Manager")
    with st.container():
        st.markdown("*Manage or file a report below. Please insert all required information as instructed.*")
    st.divider()

    # Load incidents for manager actions (use provided function signature)
    incidents = get_all_incidents()
    if incidents is None:
        incidents = pd.DataFrame()

    # Display the full cyber_incidents table for the manager
    st.subheader("All Incidents")
    st.dataframe(incidents, use_container_width=True)
    st.divider()
    
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

    # Create (match insert_incident(date, incident_type, severity, status, description, reported_by=None))
    if st.session_state.form == "A":
        with st.form("new_incident"):
            incident_type = st.text_input("Incident Type", help="e.g. Phishing, Malware, Unauthorized Access")
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
            description = st.text_area("Description")
            reported_by = st.text_input("Reported By (optional)")
            created_date = datetime.now().strftime("%Y-%m-%d")
            submitted = st.form_submit_button("Create Incident")

        if submitted:
            # call insert_incident following incidents.py signature
            incident_id = insert_incident(
                created_date,
                incident_type,
                severity,
                status,
                description,
                reported_by or None
            )
            st.success(f"Incident {incident_id} created successfully!")
            st.rerun()

    # Search (uses numeric id search on dataframe OR search_incident(conn, incident_id) for non-numeric)
    elif st.session_state.form == "C":
        with st.form("search_incident"):
            query = st.text_input("Search by numeric id or incident identifier (e.g. INC-0001)")
            submitted = st.form_submit_button("Search Incident")

        if submitted and query:
            q = query.strip()
            # numeric id search against dataframe
            try:
                int_q = int(q)
            except ValueError:
                # non-numeric -> try search_incident(conn, incident_id)
                result = search_incident(conn, q)
                if result:
                    # convert dict of lists to DataFrame for display
                    df_result = pd.DataFrame.from_dict(result)
                    st.write("### Search result")
                    st.dataframe(df_result, use_container_width=True)
                else:
                    st.warning(f"No incident found matching '{q}'")
            else:
                # integer id search in incidents dataframe
                incidents = get_all_incidents() or pd.DataFrame()
                if "id" in incidents.columns:
                    match = incidents[incidents["id"].astype(str) == str(int_q)]
                else:
                    match = pd.DataFrame()
                if not match.empty:
                    st.write("### Incident Details")
                    st.dataframe(match, use_container_width=True)
                else:
                    st.warning(f"No incident found with ID {int_q}")

    # Delete (delete_incident(conn, incident_id) expects conn + numeric id)
    elif st.session_state.form == "D":
        with st.form("delete_incident"):
            incident_id = st.text_input("Incident ID # (numeric)")
            confirm = st.checkbox("I understand this will permanently delete the incident")
            submitted = st.form_submit_button("Delete Incident")

        if submitted and incident_id:
            formatted_id = incident_id.strip()
            try:
                int(formatted_id)
            except ValueError:
                st.warning("Please enter the numeric incident ID (e.g. 500).")
            else:
                if not confirm:
                    st.warning("Please confirm deletion by checking the box.")
                else:
                    deleted = delete_incident(conn, int(formatted_id))
                    if deleted and deleted > 0:
                        st.success(f"Incident {formatted_id} deleted!")
                    else:
                        st.error(f"No incident found with ID {formatted_id}")
                    st.rerun()

    # Update (update_incident_status(conn, incident_id, new_status) already matches signature)
    elif st.session_state.form == "B":
        with st.form("update_incident"):
            incident_id = st.text_input("Incident ID # (numeric)")
            new_status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
            submitted = st.form_submit_button("Update Incident")

        if submitted and incident_id:
            formatted_id = incident_id.strip()
            try:
                int_id = int(formatted_id)
            except ValueError:
                st.warning("Please enter the numeric incident ID (e.g. 500).")
            else:
                updated = update_incident_status(conn, int_id, new_status)
                if updated:
                    st.success(f"Incident {formatted_id} updated to {new_status} successfully!")
                else:
                    st.error(f"Failed to update incident {formatted_id}.")
                st.rerun()
# ---------------------------
# AI Chat Bot Section
# ---------------------------
elif selection == "AI Chat Bot":
    # Cyber Security Specialist persona only
    st.title("🤖 Chat GPT - OpenAI API")
    st.caption("Cyber Security Specialist - Powered by GPT-4o-mini")

    # session keys
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    # API key from secrets
    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        st.warning("No API key found in .streamlit/secrets.toml — add OPENAI_API_KEY to enable chat.")

    # 👉 Fixed model (always gpt-4o-mini)
    model = "gpt-4o-mini"

    # Sidebar controls
    with st.sidebar:
        st.subheader("Chat Controls")

        # Messages counter (excluding system prompt)
        message_count = len(st.session_state.ai_chat_history)
        st.metric("Messages", message_count)

        # Temperature slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="Higher values make output more random"
        )

        # Clear chat button
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.ai_chat_history = []
            st.rerun()

    # Render chat history ABOVE the input form
    if st.session_state.ai_chat_history:
        for msg in st.session_state.ai_chat_history:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])
    else:
        st.info("Start the conversation by typing a message below.")

    # Chat form
    with st.form("incidents_chat_form", clear_on_submit=False):
        user_input = st.text_area(
            "Your message",
            placeholder="Ask the Cyber Security Specialist...",
            height=120
        )
        col1, col2 = st.columns([1, 1])
        send = col1.form_submit_button("Send")
        clear = col2.form_submit_button("Clear Conversation")

    # Clear conversation (form button)
    if clear:
        st.session_state.ai_chat_history = []
        st.rerun()

    # Send message
    if send and user_input:
        if not api_key:
            st.error("No API key configured in secrets; cannot call OpenAI.")
        else:
            system_prompt = """You are a cybersecurity expert assistant.
            Analyze incidents, threats, and provide technical guidance."""
            # build messages: system + history + user
            history_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.ai_chat_history]
            messages = [{"role": "system", "content": system_prompt}] + history_msgs + [{"role": "user", "content": user_input}]

            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature   # 👈 use slider value here
                )
                assistant_text = resp.choices[0].message.content
            except Exception as e:
                st.error(f"API request failed: {e}")
                assistant_text = None

            # append to history and rerun to show conversation
            st.session_state.ai_chat_history.append({"role": "user", "content": user_input})
            if assistant_text:
                st.session_state.ai_chat_history.append({"role": "assistant", "content": assistant_text})
            st.rerun()
# ---------------------------
# Logout
# ---------------------------
st.sidebar.divider()
if st.sidebar.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")
