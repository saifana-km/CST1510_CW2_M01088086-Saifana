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
    search_ticket
)
conn = connect_database()
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
    st.metric("Total Tickets", len(tickets))
with col2:
    priority = tickets[tickets["priority"].isin(["High", "Critical"])].shape[0]
    st.metric("High Priority", priority)
with col3:
    unresolved = tickets[tickets["status"].isin(["Open", "Investigating"])].shape[0]
    st.metric("Open Tickets", unresolved)

subject_counts = tickets["category"].value_counts().to_dict()
st.bar_chart(subject_counts)

st.subheader("Ticket Manager")
cola, colb, colc, cold = st.columns(4)
if "form" not in st.session_state:
    st.session_state.form = None

with cola:
    if st.button("Insert Ticket"):
        st.session_state.form = "A"
with colb:
    if st.button("Update Ticket"):
        st.session_state.form = "B"
with colc:
    if st.button("Search Ticket"):
        st.session_state.form = "C"
with cold:
    if st.button("Delete Ticket"):
        st.session_state.form = "D"

# Conditional rendering of forms
if st.session_state.form == "A":
    with st.form("new_ticket"):
        subject = st.text_input("Subject")
        category = st.text_input("Category")
        description = st.text_area("Description")
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
        created_date = datetime.now().strftime("%Y-%m-%d")
        resolved_date = st.text_input("Resolved Date (YYYY-MM-DD)")
        assigned_to = st.text_input("Assigned To")
        submitted = st.form_submit_button("Create Ticket")

    if submitted:
        ticket_id = insert_it_ticket(priority,status,category,subject,description,created_date,resolved_date, assigned_to or None)
        st.success(f"Ticket {ticket_id} created successfully!")
        st.rerun()

elif st.session_state.form == "B":
    with st.form("update_ticket"):
        ticket_id = st.text_input("Ticket ID")
        new_status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
        submitted = st.form_submit_button("Update Ticket")

    if submitted:
        ticket_id = update_ticket_status(conn,ticket_id,new_status)
        st.success(f"Ticket {ticket_id} updated to {new_status} successfully!")
        st.rerun()

elif st.session_state.form == "C":
    with st.form("search_ticket"):
        ticket_num = st.text_input("Ticket Number (e.g. 0001)")  
        submitted = st.form_submit_button("Search Ticket")

    if submitted and ticket_num:
        # Ensure 4-digit padding: "7" → "0007"
        formatted_id = f"TCK-{ticket_num.zfill(4)}"

        # Use the already-loaded DataFrame instead of raw cursor/indexing
        if "tickets" in locals() or "tickets" in globals():
            match = tickets[tickets["ticket_id"] == formatted_id]
            if not match.empty:
                st.write("### Ticket Details")
                st.dataframe(match, use_container_width=True)
            else:
                st.warning(f"No ticket found with ticket ID {formatted_id}")
        else:
            # fallback to DB query if DataFrame isn't available
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM it_tickets WHERE ticket_id = ?", (formatted_id,))
            result = cursor.fetchone()
            if result:
                st.write("### Ticket Details")
                st.table({
                    "ID": [result[0]],
                    "Ticket ID": [result[1]],
                    "Priority": [result[2]],
                    "Status": [result[3]],
                    "Category": [result[4]],
                    "Subject": [result[5]],
                    "Description": [result[6]],
                    "Created Date": [result[7]],
                    "Resolved Date": [result[8]],
                    "Assigned To": [result[9]],
                    "Created At": [result[10]],
                })
            else:
                st.warning(f"No ticket found with ticket ID {formatted_id}")

elif st.session_state.form == "D":
    with st.form("delete_ticket"):
        ticket_id = st.text_input("Ticket ID (e.g. TCK-0001)")  
        confirm = st.checkbox("I understand this will permanently delete the ticket")
        submitted = st.form_submit_button("Delete Ticket")

    if submitted and ticket_id:
        if not confirm:
            st.warning("Please confirm deletion by checking the box.")
        else:
            deleted = delete_ticket(conn, ticket_id)
            if deleted and deleted > 0:
                st.success(f"Ticket {ticket_id} deleted!")
            else:
                st.error(f"No ticket found with ID {ticket_id}")
            st.rerun()