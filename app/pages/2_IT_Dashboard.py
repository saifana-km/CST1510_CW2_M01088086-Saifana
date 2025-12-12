import streamlit as st
import pandas as pd
import altair as alt
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

# ---------------------------
# Session state setup
# ---------------------------
conn = connect_database('DATA/intelligence_platform.db')

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
# Navigation (Analytics / Ticket Manager / AI Chat Bot)
# ---------------------------
SECTIONS = ["Analytics", "Ticket Manager", "AI Chat Bot"]
st.sidebar.title("Navigation")
selection = st.sidebar.selectbox("Go to", SECTIONS)

# ---------------------------
# Analytics Section
# ---------------------------
if selection == "Analytics":
    st.title("🎫 IT Tickets — Analytics")
    st.markdown("*Visualise ticket trends, priorities and category breakdowns.*")
    st.divider()

    # Load tickets directly from DB for analytics
    tickets_df = pd.read_sql("SELECT * FROM it_tickets", conn)

    # Sidebar filters
    st.sidebar.subheader("Filters")
    if not tickets_df.empty and "created_date" in tickets_df.columns:
        try:
            min_date = pd.to_datetime(tickets_df["created_date"]).min()
            max_date = pd.to_datetime(tickets_df["created_date"]).max()
            date_range = st.sidebar.slider(
                "Select Date Range",
                min_value=min_date.to_pydatetime(),
                max_value=max_date.to_pydatetime(),
                value=(min_date.to_pydatetime(), max_date.to_pydatetime())
            )
            tickets_df = tickets_df[
                (pd.to_datetime(tickets_df["created_date"]) >= date_range[0]) &
                (pd.to_datetime(tickets_df["created_date"]) <= date_range[1])
            ]
        except Exception:
            # ignore date parsing errors
            pass

    # Priority filter
    priority_filter = st.sidebar.multiselect(
        "Priority",
        options=["Low", "Medium", "High", "Critical"],
        default=["Low", "Medium", "High", "Critical"]
    )
    if "priority" in tickets_df.columns:
        tickets_df = tickets_df[tickets_df["priority"].isin(priority_filter)]

    # Status filter
    status_filter = st.sidebar.multiselect(
        "Status",
        options=["Open", "Investigating", "Resolved", "Closed"],
        default=["Open", "Investigating", "Resolved", "Closed"]
    )
    if "status" in tickets_df.columns:
        tickets_df = tickets_df[tickets_df["status"].isin(status_filter)]

    # Display filtered table
    st.subheader("Filtered Tickets")
    st.dataframe(tickets_df, use_container_width=True)

    # Visualisations (pastel)
    st.subheader("Visualizations")

    if "priority" in tickets_df.columns:
        st.write("### Tickets by Priority")
        prior_counts = tickets_df["priority"].value_counts().reset_index()
        prior_counts.columns = ["priority", "count"]
        prior_chart = alt.Chart(prior_counts).mark_bar().encode(
            x="priority",
            y="count",
            color=alt.Color("priority",
                            scale=alt.Scale(
                                domain=["Critical", "High", "Medium", "Low"],
                                range=["#FFD1D1", "#FFE9C9", "#D7E9FF", "#E6F7E9"]
                            ))
        )
        st.altair_chart(prior_chart, use_container_width=True)

    if "status" in tickets_df.columns:
        st.write("### Tickets by Status")
        status_counts = tickets_df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        status_chart = alt.Chart(status_counts).mark_bar().encode(
            x="status",
            y="count",
            color=alt.Color("status",
                            scale=alt.Scale(
                                domain=["Open", "Investigating", "Resolved", "Closed"],
                                range=["#DDEFFC", "#FFF6D6", "#EAF7E9", "#F3EAFB"]
                            ))
        )
        st.altair_chart(status_chart, use_container_width=True)

    if "category" in tickets_df.columns:
        st.write("### Tickets by Category")
        cat_counts = tickets_df["category"].value_counts().reset_index()
        cat_counts.columns = ["category", "count"]
        pastel_palette = ["#FAD9E6", "#DDEBF7", "#E8F8E0", "#FFF1D6", "#F3E8FF", "#FFE4F1"]
        domain = cat_counts["category"].tolist()
        palette = (pastel_palette * ((len(domain) // len(pastel_palette)) + 1))[:len(domain)]
        cat_chart = alt.Chart(cat_counts).mark_bar().encode(
            x="category",
            y="count",
            color=alt.Color("category",
                            scale=alt.Scale(domain=domain, range=palette))
        )
        st.altair_chart(cat_chart, use_container_width=True)

    # Metrics
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tickets", len(tickets_df))
    with col2:
        high_count = tickets_df[tickets_df["priority"].isin(["High", "Critical"])].shape[0] if "priority" in tickets_df.columns else 0
        st.metric("High Priority", high_count)
    with col3:
        open_count = tickets_df[tickets_df["status"].isin(["Open", "Investigating"])].shape[0] if "status" in tickets_df.columns else 0
        st.metric("Open Tickets", open_count)

# ---------------------------
# Ticket Manager Section
# ---------------------------
elif selection == "Ticket Manager":
    st.title("🎫 Ticket Manager")
    st.markdown("*Create, update, search, and delete IT tickets.*")
    st.divider()

    # Load tickets for manager actions (use helper)
    tickets = get_all_tickets()

    cola, colb, colc, cold = st.columns(4)
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

    # Create
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
            ticket_id = insert_it_ticket(priority, status, category, subject, description, created_date, resolved_date or None, assigned_to or None)
            st.success(f"Ticket {ticket_id} created successfully!")
            st.rerun()

    # Update
    elif st.session_state.form == "B":
        with st.form("update_ticket"):
            ticket_id = st.text_input("Ticket ID (numeric id or ticket_id string)")
            new_status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
            submitted = st.form_submit_button("Update Ticket")

        if submitted and ticket_id:
            # try numeric id first, otherwise use provided string
            formatted = ticket_id.strip()
            updated = update_ticket_status(conn, formatted, new_status)
            if updated:
                st.success(f"Ticket {formatted} updated to {new_status} successfully!")
            else:
                st.error(f"Failed to update ticket {formatted}.")
            st.rerun()

    # Search
    elif st.session_state.form == "C":
        with st.form("search_ticket"):
            ticket_num = st.text_input("Ticket Number (numeric id or e.g. 0001)")
            submitted = st.form_submit_button("Search Ticket")

        if submitted and ticket_num:
            q = ticket_num.strip()
            # if looks numeric, try to match primary id; also support formatted ticket_id
            if tickets is None:
                tickets = get_all_tickets()
            if tickets is not None and not tickets.empty:
                # check both id and ticket_id columns
                matches = pd.DataFrame()
                if "id" in tickets.columns:
                    matches = matches.append(tickets[tickets["id"].astype(str) == q], ignore_index=True)
                if "ticket_id" in tickets.columns:
                    # allow passing just number like 7 -> TCK-0007
                    formatted_ticket_id = f"TCK-{q.zfill(4)}" if q.isdigit() else q
                    matches = matches.append(tickets[tickets["ticket_id"] == formatted_ticket_id], ignore_index=True)
                matches = matches.drop_duplicates()
                if not matches.empty:
                    st.write("### Ticket Details")
                    st.dataframe(matches, use_container_width=True)
                else:
                    st.warning(f"No ticket found matching '{q}'")
            else:
                st.warning("No tickets available to search.")

    # Delete
    elif st.session_state.form == "D":
        with st.form("delete_ticket"):
            ticket_id = st.text_input("Ticket ID (numeric id or ticket_id string)")
            confirm = st.checkbox("I understand this will permanently delete the ticket")
            submitted = st.form_submit_button("Delete Ticket")

        if submitted and ticket_id:
            if not confirm:
                st.warning("Please confirm deletion by checking the box.")
            else:
                deleted = delete_ticket(conn, ticket_id.strip())
                if deleted and deleted > 0:
                    st.success(f"Ticket {ticket_id} deleted!")
                else:
                    st.error(f"No ticket found with ID {ticket_id}")
                st.rerun()

# ---------------------------
# AI Chat Bot Section
# ---------------------------
elif selection == "AI Chat Bot":
    st.title("🤖 AI Chat Bot")
    st.info("This page links to the AI Chat Bot — use the dedicated page for chat functionality.")

# ---------------------------
# Logout
# ---------------------------
st.sidebar.divider()
if st.sidebar.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")