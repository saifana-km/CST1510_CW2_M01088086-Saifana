import streamlit as st
import pandas as pd
from datetime import datetime
from data.db import connect_database
from data.tickets import (
    get_all_tickets,
    get_tickets_by_category_count,
    get_tickets_category_with_many_cases,
    delete_ticket,
    update_ticket_status,
    insert_it_ticket,
    get_high_priority_by_status,
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
st.title("🎫 IT Ticket Records")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

conn = connect_database('DATA/intelligence_platform.db')
tickets = get_all_tickets()
st.dataframe(tickets, use_container_width=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("CPU Usage", "67%", delta="+5%")

with col2:
    st.metric("Memory","8.2 GB", delta="+0.3 GB")

with col3:
    st.metric("Uptime","99.8%",delta="+0.1%")

usage = pd.DataFrame({
    "time":["00:00","06:00","12:00",
            "18:00","23:59"],
            "CPU":[45,52,78,82,67],
            "Memory":[6.2,6.8,8.5,9.1,8.2]
})

with st.form("new_ticket"):
    subject = st.text_input("Subject")
    category = st.text_input("Category")
    description = st.text_area("Description")

    priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
    status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])

    created_date = datetime.now().strftime("%Y-%m-%d")
    assigned_to = st.text_input("Assigned To")

    submitted = st.form_submit_button("Create Ticket")
    
resolved_date_str = None
if status in ["Resolved", "Closed"]:
    resolved_date = st.date_input("Resolved Date")
    resolved_date_str = resolved_date.strftime("%Y-%m-%d")

if submitted and subject:
    ticket_id = insert_it_ticket(priority,status,category,subject,description,created_date,resolved_date_str, assigned_to or None)
    st.success(f"Ticket {ticket_id} created successfully!")
    st.rerun()