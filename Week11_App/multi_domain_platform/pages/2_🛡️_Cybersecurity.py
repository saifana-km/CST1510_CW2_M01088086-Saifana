import streamlit as st
import pandas as pd
import altair as alt
from services.database_manager import DatabaseManager
from models.security_incident import SecurityIncident
from datetime import datetime
from pathlib import Path

# Resolve DB path relative to package root (pages -> parent = multi_domain_platform)
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = str(ROOT / "database" / "platform.db")

# DB helper — require existing DB
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

# Require login
if not st.session_state.logged_in:
    st.error("You must be logged in to view the Cybersecurity page.")
    st.stop()

# Helpers to convert SecurityIncident objects to DataFrame
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
    try:
        incidents = SecurityIncident.load_all(db)
        # if model returns objects convert, otherwise if it's already a DataFrame return it
        if isinstance(incidents, pd.DataFrame):
            return incidents
        return incidents_to_df(incidents)
    except Exception as e:
        st.error(f"Failed to load incidents: {e}")
        return pd.DataFrame()

# Page layout
st.set_page_config(page_title="Cybersecurity", layout="wide")
st.title("🗂️ Cybersecurity Incidents Viewer")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")
st.divider()

# Top tabs navigation
SECTIONS = ["Analytics", "Incidents Manager", "AI Chat Bot"]
tab_analytics, tab_manager, tab_ai = st.tabs(SECTIONS)

# ---------- Analytics Tab ----------
with tab_analytics:
    st.header("📊 Cybersecurity Analytics")
    st.markdown("*Overview of Cybersecurity incidents, analytics and visualizations.*")
    incidents = load_incidents_df()

    # use a right-side column for tab-specific controls (visible only when this tab is rendered)
    main_col, side_col = st.columns([4, 1])
    with side_col:
        st.subheader("Filters")
        date_range = None
        if not incidents.empty and "date" in incidents.columns:
            try:
                min_date = pd.to_datetime(incidents["date"]).min()
                max_date = pd.to_datetime(incidents["date"]).max()
                date_range = st.slider(
                    "Date Range",
                    min_value=min_date.to_pydatetime(),
                    max_value=max_date.to_pydatetime(),
                    value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
                    key="analytics_date_slider"
                )
            except Exception:
                date_range = None

        sev_filter = st.multiselect("Severity", ["Low", "Medium", "High", "Critical"], default=["Low", "Medium", "High", "Critical"], key="analytics_sev")
        status_filter = st.multiselect("Status", ["Open", "Investigating", "Resolved", "Closed"], default=["Open", "Investigating", "Resolved", "Closed"], key="analytics_status")

    # content in main column
    with main_col:
        # apply filters after side_col so they affect the page only when present
        if date_range and not incidents.empty and "date" in incidents.columns:
            try:
                start_dt = pd.to_datetime(date_range[0])
                end_dt = pd.to_datetime(date_range[1])
                incidents = incidents[
                    (pd.to_datetime(incidents["date"]) >= start_dt) &
                    (pd.to_datetime(incidents["date"]) <= end_dt)
                ]
            except Exception:
                pass

        if "severity" in incidents.columns:
            incidents = incidents[incidents["severity"].isin(sev_filter)]
        if "status" in incidents.columns:
            incidents = incidents[incidents["status"].isin(status_filter)]

        with st.expander("Filtered Incidents (click to expand)", expanded=False):
            st.dataframe(incidents, use_container_width=True)

        with st.expander("Visualizations (click to expand)", expanded=False):
            st.write("Choose a chart")
            choice = st.selectbox("Chart", ["Incidents by Severity", "Incidents by Status", "Trend Over Time"], key="analytics_chart")
            if choice == "Incidents by Severity" and not incidents.empty:
                counts = incidents["severity"].value_counts().reset_index()
                counts.columns = ["severity", "count"]
                severity_order = ["Critical", "High", "Medium", "Low"]
                severity_palette = ["#FFB3B3", "#FFD7A6", "#AFCBFF", "#BFFCC6"]
                chart = alt.Chart(counts).mark_bar().encode(
                    x=alt.X("severity:N", sort=severity_order, title="Severity"),
                    y=alt.Y("count:Q", title="Count"),
                    color=alt.Color(
                        "severity:N",
                        scale=alt.Scale(domain=severity_order, range=severity_palette),
                        legend=None
                    )
                )
                st.altair_chart(chart, use_container_width=True)
    
            if choice == "Incidents by Status" and not incidents.empty:
                counts = incidents["status"].value_counts().reset_index()
                counts.columns = ["status", "count"]
                status_order = ["Open", "Investigating", "Resolved", "Closed"]
                status_palette = ["#B3D9FF", "#FFEBB3", "#C8F7C5", "#E6D5FF"]
                chart = alt.Chart(counts).mark_bar().encode(
                    x=alt.X("status:N", sort=status_order, title="Status"),
                    y=alt.Y("count:Q", title="Count"),
                    color=alt.Color(
                        "status:N",
                        scale=alt.Scale(domain=status_order, range=status_palette),
                        legend=None
                    )
                )
                st.altair_chart(chart, use_container_width=True)
    
            if choice == "Trend Over Time" and not incidents.empty:
                if "date" in incidents.columns and "incident_type" in incidents.columns:
                    df = incidents.copy()
                    df["date"] = pd.to_datetime(df["date"]).dt.date
                    grouped = df.groupby(["date", "incident_type"]).size().reset_index(name="count")
                    grouped["date"] = pd.to_datetime(grouped["date"])
                    chart = alt.Chart(grouped).mark_line(point=True).encode(
                        x=alt.X("date:T", title="Date"),
                        y=alt.Y("count:Q", title="Count"),
                        color=alt.Color("incident_type:N", title="Incident Type"),
                        tooltip=[
                            alt.Tooltip("date:T", title="Date"),
                            alt.Tooltip("incident_type:N", title="Type"),
                            alt.Tooltip("count:Q", title="Count")
                        ]
                    ).interactive()
                    st.altair_chart(chart, use_container_width=True)
                else:
                    if "date" in incidents.columns:
                        ts = pd.to_datetime(incidents["date"]).dt.date.value_counts().sort_index().reset_index()
                        ts.columns = ["date", "count"]
                        chart = alt.Chart(ts).mark_line(color="#9BB7D4", point=True).encode(
                            x=alt.X("date:T", title="Date"),
                            y=alt.Y("count:Q", title="Count")
                        )
                        st.altair_chart(chart, use_container_width=True)

        st.subheader("Key Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Incidents", len(incidents))
        col2.metric("Critical/High", incidents[incidents["severity"].isin(["Critical", "High"])].shape[0] if not incidents.empty else 0)
        col3.metric("Open/Investigating", incidents[incidents["status"].isin(["Open", "Investigating"])].shape[0] if not incidents.empty else 0)

# ---------- Incidents Manager Tab ----------
with tab_manager:
    st.header("⚠️ Incidents Manager")
    st.markdown("**Cybersecurity** Incidents system manager.")
    incidents_df = load_incidents_df()

    # Show table then CRUD buttons below it in four columns
    st.subheader("All Incidents")
    st.dataframe(incidents_df, use_container_width=True)
    st.divider()
    st.info("Please input the correct values and ID when filing reports.")
    cola, colb, colc, cold = st.columns(4)
    with cola:
        if st.button("Insert Incident", key="mgr_insert"):
            st.session_state.form = "A"
    with colb:
        if st.button("Update Incident", key="mgr_update"):
            st.session_state.form = "B"
    with colc:
        if st.button("Search Incident", key="mgr_search"):
            st.session_state.form = "C"
    with cold:
        if st.button("Delete Incident", key="mgr_delete"):
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
            st.rerun()

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
                st.rerun()

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
                    st.rerun()

# ---------- AI Chat Bot Tab ----------
with tab_ai:
    st.header("🤖 ChatGPT - OpenAI API")
    st.caption("Cyber Security Specialist - Powered by GPT-4o-mini")

    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        st.warning("No API key found in .streamlit/secrets.toml — add OPENAI_API_KEY to enable chat.")

    model = "gpt-4o-mini"

    # Render chat history in a scrollable chat interface
    if st.session_state.ai_chat_history:
        for msg in st.session_state.ai_chat_history:
            role = msg.get("role", "assistant")
            content = msg.get("content", "")
            st.chat_message(role).write(content)
    else:
        st.info("Start the conversation by typing a message below.")

    # Chat insert
    user_input = st.chat_input("Ask the Cyber Security Specialist...")

    if user_input:
        if not api_key:
            st.error("No API key configured in secrets; cannot call OpenAI.")
        else:
            # retrieve temperature from session (set via controls below)
            temperature = st.session_state.get("ai_temperature", 1.0)

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

            # Append user and assistant messages once
            st.session_state.ai_chat_history.append({"role": "user", "content": user_input})
            if assistant_text:
                st.session_state.ai_chat_history.append({"role": "assistant", "content": assistant_text})

            st.rerun()

    # Controls at the bottom (expander or columns)
    st.divider()
    with st.expander("⚙️ Chat Settings", expanded=False):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.metric("Messages", len(st.session_state.ai_chat_history))
        with col2:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state.get("ai_temperature", 1.0),
                step=0.1,
                help="Higher values make output more random",
                key="ai_temperature"
            )
        with col3:
            if st.button("🗑 Clear Chat", use_container_width=True, key="clear_chat"):
                st.session_state.ai_chat_history = []
                st.rerun()

# Logout (sidebar) -- keep global
st.sidebar.divider()
if st.sidebar.button("Log out"):
    st.session_state.logged_in = False
    if "username" in st.session_state:
        st.session_state.username = ""
    st.info("You have been logged out.")
    try:
        st.switch_page("1_Home.py")
    except Exception:
        st.rerun()