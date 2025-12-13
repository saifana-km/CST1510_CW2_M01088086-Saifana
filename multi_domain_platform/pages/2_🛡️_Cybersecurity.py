import streamlit as st
import pandas as pd
import altair as alt
from services.database_manager import DatabaseManager
from models.security_incident import SecurityIncident
from datetime import datetime

DB_PATH = "database/platform.db"

# DB helper
db = DatabaseManager(DB_PATH)
db.connect()  # fixed extra paren

# --- Helpers to convert SecurityIncident objects to DataFrame ---
def incidents_to_df(incidents):
    if not incidents:
        return pd.DataFrame()
    rows = []
    for inc in incidents:
        rows.append({
            "id": inc.get_id(),
            "date": inc.get_date(),
            "incident_type": inc.get_incident_type(),
            "severity": inc.get_severity(),
            "status": inc.get_status(),
            "description": inc.get_description(),
            "reported_by": inc.get_reported_by(),
            "created_at": inc.get_created_at()
        })
    return pd.DataFrame(rows)

def load_incidents_df():
    incidents = SecurityIncident.load_all(db)
    return incidents_to_df(incidents)

# Streamlit UI modeled on Incidents Dashboard
st.set_page_config(page_title="Cybersecurity", layout="wide")
SECTIONS = ["Analytics", "Incidents Manager", "AI Chat Bot"]
st.sidebar.title("Navigation")
selection = st.sidebar.selectbox("Go to", SECTIONS)

# simple auth guard (keeps pattern similar to app pages)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # adjust as needed in this project
if "form" not in st.session_state:
    st.session_state.form = None

if selection == "Analytics":
    st.title("📊 Cybersecurity Analytics")
    st.markdown("*Overview of incidents*")
    incidents = load_incidents_df()

    # Filters
    st.sidebar.subheader("Filters")
    if not incidents.empty and "date" in incidents.columns:
        try:
            min_date = pd.to_datetime(incidents["date"]).min()
            max_date = pd.to_datetime(incidents["date"]).max()
            date_range = st.sidebar.slider(
                "Date range",
                min_value=min_date.to_pydatetime(),
                max_value=max_date.to_pydatetime(),
                value=(min_date.to_pydatetime(), max_date.to_pydatetime())
            )
            incidents = incidents[
                (pd.to_datetime(incidents["date"]) >= date_range[0]) &
                (pd.to_datetime(incidents["date"]) <= date_range[1])
            ]
        except Exception:
            pass

    sev_filter = st.sidebar.multiselect("Severity", ["Critical", "High", "Medium", "Low"], default=["Critical", "High", "Medium", "Low"])
    if "severity" in incidents.columns:
        incidents = incidents[incidents["severity"].isin(sev_filter)]

    status_filter = st.sidebar.multiselect("Status", ["Open", "Investigating", "Resolved", "Closed"], default=["Open", "Investigating", "Resolved", "Closed"])
    if "status" in incidents.columns:
        incidents = incidents[incidents["status"].isin(status_filter)]

    with st.expander("Filtered Incidents (click to expand)", expanded=False):
        st.dataframe(incidents, use_container_width=True)

    with st.expander("Visualizations (click to expand)", expanded=False):
        st.write("Choose a chart")
        choice = st.selectbox("Chart", ["Incidents by Severity", "Incidents by Status", "Trend Over Time"])
        if choice == "Incidents by Severity" and not incidents.empty:
            counts = incidents["severity"].value_counts().reset_index()
            counts.columns = ["severity", "count"]
            chart = alt.Chart(counts).mark_bar().encode(x="severity", y="count", color="severity")
            st.altair_chart(chart, use_container_width=True)
        if choice == "Incidents by Status" and not incidents.empty:
            counts = incidents["status"].value_counts().reset_index()
            counts.columns = ["status", "count"]
            chart = alt.Chart(counts).mark_bar().encode(x="status", y="count", color="status")
            st.altair_chart(chart, use_container_width=True)
        if choice == "Trend Over Time" and not incidents.empty:
            if "date" in incidents.columns:
                ts = pd.to_datetime(incidents["date"]).dt.date.value_counts().sort_index().reset_index()
                ts.columns = ["date", "count"]
                chart = alt.Chart(ts).mark_line(point=True).encode(x=alt.X("date:T"), y="count:Q")
                st.altair_chart(chart, use_container_width=True)

    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Incidents", len(incidents))
    col2.metric("Critical/High", incidents[incidents["severity"].isin(["Critical", "High"])].shape[0] if not incidents.empty else 0)
    col3.metric("Open/Investigating", incidents[incidents["status"].isin(["Open", "Investigating"])].shape[0] if not incidents.empty else 0)

elif selection == "Incidents Manager":
    st.title("⚠️ Incidents Manager")
    st.markdown("*CRUD operations for incidents*")
    incidents_df = load_incidents_df()
    st.subheader("All Incidents")
    st.dataframe(incidents_df, use_container_width=True)
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

    if st.session_state.form == "A":
        with st.form("new_incident"):
            date = st.date_input("Date", value=datetime.utcnow().date())
            incident_type = st.text_input("Incident Type")
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            status = st.selectbox("Status", ["Open", "Investigating", "Resolved", "Closed"])
            description = st.text_area("Description")
            reported_by = st.text_input("Reported By (optional)")
            submitted = st.form_submit_button("Create Incident")
        if submitted:
            new_id = SecurityIncident.insert(db, date.isoformat(), incident_type, severity, status, description, reported_by or None)
            st.success(f"Incident created (id={new_id})")
            st.experimental_rerun()

    elif st.session_state.form == "B":
        with st.form("update_incident"):
            incident_id = st.text_input("Incident ID (numeric)")
            new_status = st.selectbox("New Status", ["Open", "Investigating", "Resolved", "Closed"])
            submitted = st.form_submit_button("Update")
        if submitted and incident_id:
            try:
                iid = int(incident_id.strip())
            except ValueError:
                st.warning("Enter numeric ID")
            else:
                ok = SecurityIncident.update_status_in_db(db, iid, new_status)
                if ok:
                    st.success(f"Incident {iid} updated")
                else:
                    st.error("Incident not found")
                st.experimental_rerun()

    elif st.session_state.form == "C":
        with st.form("search_incident"):
            q = st.text_input("Search by ID or text")
            submitted = st.form_submit_button("Search")
        if submitted and q:
            results = SecurityIncident.search(db, q)
            df = incidents_to_df(results)
            if df.empty:
                st.warning("No matches")
            else:
                st.dataframe(df, use_container_width=True)

    elif st.session_state.form == "D":
        with st.form("delete_incident"):
            incident_id = st.text_input("Incident ID (numeric)")
            confirm = st.checkbox("I confirm deletion")
            submitted = st.form_submit_button("Delete")
        if submitted and incident_id:
            try:
                iid = int(incident_id.strip())
            except ValueError:
                st.warning("Enter numeric ID")
            else:
                if not confirm:
                    st.warning("Please confirm deletion")
                else:
                    deleted = SecurityIncident.delete(db, iid)
                    if deleted:
                        st.success(f"Incident {iid} deleted")
                    else:
                        st.error("Incident not found")
                    st.experimental_rerun()

elif selection == "AI Chat Bot":
    st.title("🤖 Cyber Security Assistant")
    st.caption("Cyber Security Specialist - Powered by GPT-4o-mini")

    # session keys
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    # API key from secrets
    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        st.warning("No API key found in .streamlit/secrets.toml — add OPENAI_API_KEY to enable chat.")

    # Fixed model for this app
    model = "gpt-4o-mini"

    # Sidebar controls for chat
    with st.sidebar:
        st.subheader("Chat Controls")
        message_count = len(st.session_state.ai_chat_history)
        st.metric("Messages", message_count)

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="Higher values make output more random"
        )

        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.ai_chat_history = []
            st.experimental_rerun()

    # Render chat history
    if st.session_state.ai_chat_history:
        for msg in st.session_state.ai_chat_history:
            role = msg.get("role", "assistant")
            content = msg.get("content", "")
            st.chat_message(role).write(content)
    else:
        st.info("Start the conversation by typing a message below.")

    # Chat input form
    with st.form("cyber_chat_form", clear_on_submit=False):
        user_input = st.text_area(
            "Your message",
            placeholder="Ask the Cyber Security Specialist...",
            height=140
        )
        col1, col2 = st.columns([1, 1])
        send = col1.form_submit_button("Send")
        clear = col2.form_submit_button("Clear Conversation")

    if clear:
        st.session_state.ai_chat_history = []
        st.experimental_rerun()

    if send and user_input:
        if not api_key:
            st.error("No API key configured in secrets; cannot call OpenAI.")
        else:
            system_prompt = (
                "You are a cybersecurity expert assistant. Analyze incidents, threats and provide clear, "
                "actionable mitigation steps, triage guidance and investigation pointers. Be concise and safety-conscious."
            )

            history_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.ai_chat_history]
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

            # append to history and rerun to show conversation
            st.session_state.ai_chat_history.append({"role": "user", "content": user_input})
            if assistant_text:
                st.session_state.ai_chat_history.append({"role": "assistant", "content": assistant_text})
            st.experimental_rerun()