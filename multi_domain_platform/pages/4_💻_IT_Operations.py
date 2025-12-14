import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from services.database_manager import DatabaseManager
from models.it_ticket import ITTicket
from pathlib import Path

# Resolve DB path relative to package root (pages -> parent = multi_domain_platform)
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = str(ROOT / "database" / "platform.db")

# Page config
st.set_page_config(page_title="IT Operations", layout="wide")

# DB manager instance — require existing DB
db = DatabaseManager(DB_PATH)
try:
    db.connect()
except Exception as e:
    st.error(f"Could not open database at {DB_PATH}: {e}")
    st.stop()

# Ensure session state keys exist
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "form" not in st.session_state:
    st.session_state.form = None
if "ai_chat_history" not in st.session_state:
    st.session_state.ai_chat_history = []

# Require login
if not st.session_state.logged_in:
    st.error("You must be logged in to view IT Operations.")
    if st.button("Go to login page"):
        try:
            st.switch_page("1_Home.py")
        except Exception:
            st.rerun()
    st.stop()

st.title("💻 IT Operations — Tickets")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")
st.divider()

# Top tabs navigation (replace sidebar navigation)
SECTIONS = ["Analytics", "Ticket Manager", "AI Chat Bot"]
tab_analytics, tab_manager, tab_ai = st.tabs(SECTIONS)

# ---------------------------
# Analytics Tab
# ---------------------------
with tab_analytics:
    st.header("📊 IT Operations Analytics")
    st.markdown("*Visualise ticket trends, priorities and category breakdowns.*")

    try:
        tickets_df = ITTicket.get_all_tickets(db)
        if tickets_df is None:
            tickets_df = pd.DataFrame()
    except Exception as e:
        import traceback, pathlib
        st.error(f"Failed to load tickets: {e}")
        st.text(traceback.format_exc())
        st.write("DB path (resolved):", pathlib.Path(DB_PATH).resolve())
        try:
            tables = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table';")
            st.write("Tables in DB:", tables)
        except Exception as e2:
            st.write("Could not list tables:", e2)
        tickets_df = pd.DataFrame()

    # move filters into a right-side column so they are tab-scoped
    main_col, side_col = st.columns([4, 1])
    with side_col:
        st.subheader("Filters")
        date_range = None
        if not tickets_df.empty and "created_date" in tickets_df.columns:
            try:
                min_date = pd.to_datetime(tickets_df["created_date"]).min()
                max_date = pd.to_datetime(tickets_df["created_date"]).max()
                date_range = st.date_input(
                    "Date range (start / end)",
                    value=(min_date.date(), max_date.date()),
                    key="analytics_date"
                )
            except Exception:
                date_range = None

        priority_filter = st.multiselect(
            "Priority",
            options=["Low", "Medium", "High", "Critical"],
            default=["Low", "Medium", "High", "Critical"],
            key="analytics_priority"
        )
        status_filter = st.multiselect(
            "Status",
            options=["Open", "Investigating", "Resolved", "Closed"],
            default=["Open", "Investigating", "Resolved", "Closed"],
            key="analytics_status"
        )

    with main_col:
        df = tickets_df.copy()
        if date_range and not df.empty and "created_date" in df.columns:
            try:
                start_dt = pd.to_datetime(date_range[0])
                end_dt = pd.to_datetime(date_range[1])
                df = df[(pd.to_datetime(df["created_date"]) >= start_dt) & (pd.to_datetime(df["created_date"]) <= end_dt)]
            except Exception:
                pass

        if "priority" in df.columns:
            df = df[df["priority"].isin(priority_filter)]
        if "status" in df.columns:
            df = df[df["status"].isin(status_filter)]

        with st.expander("Filtered Tickets (click to expand)", expanded=False):
            st.dataframe(df, use_container_width=True)

        with st.expander("Visualizations (click to expand)", expanded=False):
            st.write("Choose a chart from the dropdown to display it.")
            chart_choice = st.selectbox("Select chart", [
                "Tickets by Priority",
                "Tickets by Status",
                "Tickets by Category",
                "Ticket Trend Over Time (by type)"
            ], key="analytics_chart")

            if chart_choice == "Tickets by Priority" and "priority" in df.columns and not df.empty:
                prior_counts = df["priority"].value_counts().reset_index()
                prior_counts.columns = ["priority", "count"]
                prior_chart = alt.Chart(prior_counts).mark_bar().encode(
                    x=alt.X("priority:N", sort=["Critical", "High", "Medium", "Low"]),
                    y=alt.Y("count:Q"),
                    color=alt.Color("priority:N",
                                    scale=alt.Scale(
                                        domain=["Critical", "High", "Medium", "Low"],
                                        range=["#FFD1D1", "#FFE9C9", "#D7E9FF", "#E6F7E9"]
                                    ),
                                    legend=None
                    )
                )
                st.altair_chart(prior_chart, use_container_width=True)

            if chart_choice == "Tickets by Status" and "status" in df.columns and not df.empty:
                status_counts = df["status"].value_counts().reset_index()
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

            if chart_choice == "Tickets by Category" and "category" in df.columns and not df.empty:
                cat_counts = df["category"].value_counts().reset_index()
                cat_counts.columns = ["category", "count"]
                pastel_palette = ["#FAD9E6", "#DDEBF7", "#E8F8E0", "#FFF1D6", "#F3E8FF", "#FFE4F1"]
                domain = cat_counts["category"].tolist()
                palette = (pastel_palette * ((len(domain) // len(pastel_palette)) + 1))[:len(domain)]
                cat_chart = alt.Chart(cat_counts).mark_bar().encode(
                    x="category",
                    y="count",
                    color=alt.Color("category", scale=alt.Scale(domain=domain, range=palette))
                )
                st.altair_chart(cat_chart, use_container_width=True)

            if chart_choice == "Ticket Trend Over Time (by type)" and "created_date" in df.columns and not df.empty:
                try:
                    tmp = df.copy()
                    tmp["date"] = pd.to_datetime(tmp["created_date"]).dt.date
                    if "subject" in tmp.columns:
                        type_col = "subject"
                    elif "category" in tmp.columns:
                        type_col = "category"
                    else:
                        type_col = "ticket_id"
                    grouped = tmp.groupby(["date", type_col]).size().reset_index(name="count")
                    grouped["date"] = pd.to_datetime(grouped["date"])
                    chart = alt.Chart(grouped).mark_line(point=True).encode(
                        x=alt.X("date:T", title="Date"),
                        y=alt.Y("count:Q", title="Count"),
                        color=alt.Color(f"{type_col}:N", title=type_col.capitalize()),
                        tooltip=[alt.Tooltip("date:T", title="Date"), alt.Tooltip(f"{type_col}:N", title=type_col.capitalize()), alt.Tooltip("count:Q", title="Count")]
                    ).interactive()
                    st.altair_chart(chart, use_container_width=True)
                except Exception:
                    st.warning("Unable to render trend over time.")

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
# Ticket Manager Tab
# ---------------------------
with tab_manager:
    st.title("🎫 Ticket Manager")
    st.markdown("*Create, update, search, and delete IT tickets.*")
    st.divider()

    try:
        tickets = ITTicket.get_all_tickets(db)
        if tickets is None:
            tickets = pd.DataFrame()
    except Exception:
        tickets = pd.DataFrame()

    st.subheader("All Tickets")
    st.dataframe(tickets, use_container_width=True)
    st.divider()
    st.info("Please input the correct values and ID when filing reports.")
    # CRUD buttons under the table in columns
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
            ticket_id = ITTicket.insert_ticket(
                db,
                priority,
                status,
                category,
                subject,
                description,
                created_date,
                (resolved_date or None),
                (assigned_to or "")
            )
            st.success(f"Ticket {ticket_id} created successfully!")
            st.rerun()

    # Update
    elif st.session_state.form == "B":
        with st.form("update_ticket"):
            ticket_identifier = st.text_input("Ticket ID (numeric id or ticket_id)")
            new_status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
            new_resolved_date = st.text_input("Resolved Date (YYYY-MM-DD, leave empty if not resolved)", value="")
            submitted = st.form_submit_button("Update Ticket")

        if submitted and ticket_identifier:
            tid_raw = ticket_identifier.strip()
            if tid_raw.isdigit():
                tid = f"TCK-{int(tid_raw):04d}"
            else:
                tid = tid_raw
            
            # Update status
            updated = ITTicket.update_ticket_status(db, tid, new_status)
            
            # Update resolved_date if provided
            resolved_date_value = new_resolved_date.strip() if new_resolved_date else None
            if resolved_date_value:
                try:
                    db.execute_query(
                        "UPDATE it_tickets SET resolved_date = ? WHERE ticket_id = ?",
                        (resolved_date_value, tid)
                    )
                except Exception as e:
                    st.error(f"Failed to update resolved_date: {e}")
            else:
                # Set resolved_date to NULL if empty
                try:
                    db.execute_query(
                        "UPDATE it_tickets SET resolved_date = NULL WHERE ticket_id = ?",
                        (tid,)
                    )
                except Exception as e:
                    st.error(f"Failed to clear resolved_date: {e}")
            
            if updated:
                st.success(f"Ticket {tid} updated to {new_status} successfully!")
            else:
                st.error(f"Failed to update ticket {ticket_identifier}.")
            st.rerun()

    # Search
    elif st.session_state.form == "C":
        with st.form("search_ticket"):
            query = st.text_input("Search by ticket id (e.g. TCK-0001) or numeric id")
            submitted = st.form_submit_button("Search Ticket")

        if submitted and query:
            q = query.strip()
            if q.isdigit():
                try:
                    df = ITTicket.get_all_tickets(db)
                    if "id" in df.columns and "ticket_id" in df.columns:
                        match = df[df["id"].astype(str) == q]
                    else:
                        match = pd.DataFrame()
                except Exception:
                    match = pd.DataFrame()
                if not match.empty:
                    st.dataframe(match, use_container_width=True)
                else:
                    st.warning(f"No ticket found for id {q}")
            else:
                ticket_obj = ITTicket.search_ticket(db, q)
                if ticket_obj:
                    st.write("### Ticket Details")
                    # ticket_obj may be a dataclass/object; show dict if available
                    try:
                        st.json(ticket_obj.to_dict())
                    except Exception:
                        st.write(ticket_obj)
                else:
                    st.warning(f"No ticket found matching '{q}'")

    # Delete
    elif st.session_state.form == "D":
        with st.form("delete_ticket"):
            ticket_identifier = st.text_input("Ticket ID (numeric id or ticket_id)")
            confirm = st.checkbox("I understand this will permanently delete the ticket")
            submitted = st.form_submit_button("Delete Ticket")

        if submitted and ticket_identifier:
            if not confirm:
                st.warning("Please confirm deletion by checking the box.")
            else:
                tid_raw = ticket_identifier.strip()
                if tid_raw.isdigit():
                    tid = f"TCK-{int(tid_raw):04d}"
                else:
                    tid = tid_raw
                deleted = ITTicket.delete_ticket(db, tid)
                if deleted and deleted > 0:
                    st.success(f"Ticket {tid} deleted!")
                else:
                    st.error(f"No ticket found with ID {ticket_identifier}")
                st.rerun()

# ---------------------------
# AI Chat Bot Tab
# ---------------------------
with tab_ai:
    st.header("🤖 ChatGPT - OpenAI API")
    st.caption("IT Operations Specialist - Powered by GPT-4o-mini")

    # session history with unique key for IT Operations
    if "it_ai_chat_history" not in st.session_state:
        st.session_state.it_ai_chat_history = []

    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        st.warning("No API key found in .streamlit/secrets.toml — add OPENAI_API_KEY to enable chat.")

    model = "gpt-4o-mini"

    # Render chat history in a scrollable chat interface
    if st.session_state.it_ai_chat_history:
        for msg in st.session_state.it_ai_chat_history:
            role = msg.get("role", "assistant")
            content = msg.get("content", "")
            st.chat_message(role).write(content)
    else:
        st.info("Start the conversation by typing a message below.")

    # Chat input at the bottom using st.chat_input (native chat UI)
    user_input = st.chat_input("Ask the IT Operations Specialist...")

    if user_input:
        if not api_key:
            st.error("No API key configured; cannot call OpenAI.")
        else:
            # retrieve temperature from session (set via controls below)
            temperature = st.session_state.get("it_ai_temperature", 1.0)

            system_prompt = (
                "You are an IT operations specialist. Provide clear, actionable guidance "
                "for ticket triage, escalation, deployments and runbook steps. Avoid unsafe or illegal instructions."
            )

            history_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.it_ai_chat_history]
            messages = [{"role": "system", "content": system_prompt}] + history_msgs + [{"role": "user", "content": user_input}]

            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )
                assistant_text = resp.choices[0].message.content
            except Exception as e:
                st.error(f"API request failed: {e}")
                assistant_text = None

            # Append user and assistant messages once
            st.session_state.it_ai_chat_history.append({"role": "user", "content": user_input})
            if assistant_text:
                st.session_state.it_ai_chat_history.append({"role": "assistant", "content": assistant_text})

            st.rerun()

    # Controls at the bottom (expander)
    st.divider()
    with st.expander("⚙️ Chat Settings", expanded=False):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.metric("Messages", len(st.session_state.it_ai_chat_history))
        with col2:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state.get("it_ai_temperature", 1.0),
                step=0.1,
                help="Higher values make output more random",
                key="it_ai_temperature"
            )
        with col3:
            if st.button("🗑 Clear Chat", use_container_width=True, key="it_clear_chat"):
                st.session_state.it_ai_chat_history = []
                st.rerun()

# ---------------------------
# Logout (sidebar)
# ---------------------------
st.sidebar.divider()
if st.sidebar.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    try:
        st.switch_page("1_Home.py")
    except Exception:
        st.rerun()