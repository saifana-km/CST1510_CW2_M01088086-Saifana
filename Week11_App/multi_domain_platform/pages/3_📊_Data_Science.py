import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from models.dataset import Dataset
from services.database_manager import DatabaseManager
from pathlib import Path

# Resolve DB path relative to package root (pages -> parent = multi_domain_platform)
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = str(ROOT / "database" / "platform.db")

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

# Require login
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    st.stop()

def load_datasets_df():
    try:
        df = Dataset.get_all_datasets(db)
        if df is None:
            return pd.DataFrame()
        return df
    except Exception as e:
        st.error(f"Failed to load datasets: {e}")
        return pd.DataFrame()

# Page layout
st.set_page_config(page_title="Datasets Metadata", layout="wide")
st.title("🗂️ Datasets Metadata Viewer")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")
st.divider()

# Top tabs navigation (replace sidebar navigation)
SECTIONS = ["Analytics", "Metadata Manager", "AI Chat Bot"]
tab_analytics, tab_manager, tab_ai = st.tabs(SECTIONS)

# ---------------------------
# Analytics Tab
# ---------------------------
with tab_analytics:
    st.header("📊 Metadata Analytics")
    st.markdown("*Overview of datasets metadata, counts and size distribution.*")

    datasets = load_datasets_df()

    main_col, side_col = st.columns([4, 1])
    with side_col:
        st.subheader("Filters")
        cat_sel = "All"
        date_range = None
        if not datasets.empty and "category" in datasets.columns:
            cats = ["All"] + sorted(datasets["category"].dropna().unique().tolist())
            cat_sel = st.selectbox("Category", cats, key="analytics_category")
        if not datasets.empty and "last_updated" in datasets.columns:
            try:
                min_date = pd.to_datetime(datasets["last_updated"]).min()
                max_date = pd.to_datetime(datasets["last_updated"]).max()
                date_range = st.slider(
                    "Last Updated Range",
                    min_value=min_date.to_pydatetime(),
                    max_value=max_date.to_pydatetime(),
                    value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
                    key="analytics_date"
                )
            except Exception:
                date_range = None

    with main_col:
        df = datasets.copy()
        if cat_sel != "All" and "category" in df.columns:
            df = df[df["category"] == cat_sel]
        if date_range is not None and not df.empty and "last_updated" in df.columns:
            try:
                df = df[
                    (pd.to_datetime(df["last_updated"]) >= date_range[0]) &
                    (pd.to_datetime(df["last_updated"]) <= date_range[1])
                ]
            except Exception:
                pass

        with st.expander("Filtered Datasets (click to expand)", expanded=False):
            st.dataframe(df, use_container_width=True)

        with st.expander("Visualizations (click to expand)", expanded=False):
            st.write("Choose a chart from the dropdown to display it.")
            chart_choice = st.selectbox("Choose visualization", [
                "Datasets by Category",
                "Record Count Distribution",
                "Size (MB) Distribution",
                "Large Datasets (by size)"
            ], key="analytics_chart")

            if chart_choice == "Datasets by Category" and not df.empty and "category" in df.columns:
                cat_counts = Dataset.get_datasets_by_category(db)
                pastel_palette = ["#FAD9E6", "#DDEBF7", "#E8F8E0", "#FFF1D6", "#F3E8FF", "#FFE4F1"]
                domain = cat_counts["category"].tolist()
                palette = (pastel_palette * ((len(domain) // len(pastel_palette)) + 1))[:len(domain)]
                chart = alt.Chart(cat_counts).mark_bar().encode(
                    x="category",
                    y="count",
                    color=alt.Color("category", scale=alt.Scale(domain=domain, range=palette))
                )
                st.altair_chart(chart, use_container_width=True)

            if chart_choice == "Record Count Distribution" and not df.empty and "record_count" in df.columns:
                rc = df[["dataset_name", "record_count"]].dropna()
                hist = alt.Chart(rc).mark_bar(color="#AFCBFF").encode(
                    alt.X("record_count:Q", bin=alt.Bin(maxbins=40), title="Record Count"),
                    y='count()'
                )
                st.altair_chart(hist, use_container_width=True)

            if chart_choice == "Size (MB) Distribution" and not df.empty and "file_size_mb" in df.columns:
                sz = df[["dataset_name", "file_size_mb"]].dropna()
                hist = alt.Chart(sz).mark_bar(color="#FFD7A6").encode(
                    alt.X("file_size_mb:Q", bin=alt.Bin(maxbins=40), title="File Size (MB)"),
                    y='count()'
                )
                st.altair_chart(hist, use_container_width=True)

            if chart_choice == "Large Datasets (by size)":
                large = Dataset.get_large_datasets(db, min_size_mb=100)
                if large is None or large.empty:
                    st.info("No large datasets found (threshold 100 MB).")
                else:
                    chart = alt.Chart(large).mark_bar(color="#FFCC99").encode(
                        x=alt.X("dataset_name:N", sort='-y', title="Dataset"),
                        y=alt.Y("file_size_mb:Q", title="Size (MB)"),
                        tooltip=["dataset_name", "file_size_mb"]
                    )
                    st.altair_chart(chart, use_container_width=True)

    # Metrics
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Datasets", len(datasets))
    with col2:
        total_records = int(datasets["record_count"].sum()) if "record_count" in datasets.columns else 0
        st.metric("Total Records", total_records)
    with col3:
        total_size = float(datasets["file_size_mb"].sum()) if "file_size_mb" in datasets.columns else 0.0
        st.metric("Total Size (MB)", f"{total_size:.1f}")

# ---------------------------
# Metadata Manager Tab
# ---------------------------
with tab_manager:
    st.header("🛠️ Metadata Manager")
    st.markdown("*Insert, update, search or delete dataset metadata.*")
    st.divider()

    datasets = load_datasets_df()
    st.subheader("All Datasets")
    st.dataframe(datasets, use_container_width=True)
    st.divider()
    st.info("Please input the correct values and ID when filing reports.")
    cola, colb, colc, cold = st.columns(4)
    with cola:
        if st.button("Insert Metadata", key="ds_insert"):
            st.session_state.form = "A"
    with colb:
        if st.button("Update Last Updated", key="ds_update_last"):
            st.session_state.form = "B"
    with colc:
        if st.button("Update Record Count", key="ds_update_count"):
            st.session_state.form = "C"
    with cold:
        if st.button("Search / Delete", key="ds_search_del"):
            st.session_state.form = "D"

    # Create
    if st.session_state.form == "A":
        with st.form("new_metadata"):
            dataset_name = st.text_input("Dataset Name", help="e.g. customers.csv")
            category = st.text_input("Category", help="e.g. Finance")
            source = st.text_input("Source", help="e.g. internal / external")
            last_updated = st.text_input("Last Updated (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"))
            record_count = st.number_input("Record Count", min_value=0, step=1, value=0)
            file_size_mb = st.number_input("File Size (MB)", min_value=0.0, step=0.1, value=0.0)
            submitted = st.form_submit_button("Create Metadata")

        if submitted:
            if not dataset_name or not category or not source:
                st.warning("Please provide dataset name, category and source.")
            else:
                new_id = Dataset.insert_dataset(
                    db,
                    dataset_name,
                    category,
                    source,
                    last_updated or None,
                    int(record_count),
                    float(file_size_mb)
                )
                st.success(f"Metadata record created (id={new_id}).")
                st.rerun()

    # Update last_updated
    elif st.session_state.form == "B":
        with st.form("update_last"):
            dataset_id = st.text_input("Dataset ID (numeric)", help="Use the numeric 'id' shown in the table")
            new_date = st.text_input("New Last Updated Date (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"))
            submitted = st.form_submit_button("Update Last Updated")

        if submitted and dataset_id:
            try:
                id_val = int(dataset_id.strip())
            except ValueError:
                st.warning("Please enter a numeric dataset ID.")
            else:
                rows = Dataset.update_dataset_last_updated(db, id_val, new_date)
                if rows and rows > 0:
                    st.success(f"Dataset {id_val} last_updated set to {new_date}.")
                else:
                    st.error(f"No dataset found with ID {id_val}.")
                st.rerun()

    # Update record_count
    elif st.session_state.form == "C":
        with st.form("update_count"):
            dataset_id = st.text_input("Dataset ID (numeric)", help="Use the numeric 'id' shown in the table")
            new_count = st.number_input("New Record Count", min_value=0, step=1, value=0)
            submitted = st.form_submit_button("Update Record Count")

        if submitted and dataset_id:
            try:
                id_val = int(dataset_id.strip())
            except ValueError:
                st.warning("Please enter a numeric dataset ID.")
            else:
                rows = Dataset.update_dataset_record_count(db, id_val, int(new_count))
                if rows and rows > 0:
                    st.success(f"Dataset {id_val} record_count updated to {new_count}.")
                else:
                    st.error(f"No dataset found with ID {id_val}.")
                st.rerun()

    # Search and Delete combined
    elif st.session_state.form == "D":
        with st.form("search_delete"):
            query = st.text_input("Search by ID or Name (enter numeric id or part of dataset name)")
            col1, col2 = st.columns([3, 1])
            with col1:
                search_btn = st.form_submit_button("Search")
            with col2:
                delete_btn = st.form_submit_button("Delete (by ID)")
            confirm_delete = st.checkbox("I confirm deletion (for delete action)")

        if search_btn and query:
            q = query.strip()
            df = Dataset.get_dataset_by_name(db, q)
            if df is None or df.empty:
                st.warning("No matching dataset found.")
            else:
                st.write("### Matches")
                st.dataframe(df, use_container_width=True)

        if delete_btn and query:
            q = query.strip()
            try:
                id_val = int(q)
            except ValueError:
                st.warning("Deletion requires the numeric dataset ID.")
            else:
                if not confirm_delete:
                    st.warning("Please check the confirmation box to delete.")
                else:
                    rows = Dataset.delete_dataset(db, id_val)
                    if rows and rows > 0:
                        st.success(f"Dataset id={id_val} deleted.")
                    else:
                        st.error(f"No dataset found with ID {id_val}.")
                    st.rerun()

# ---------------------------
# AI Chat Bot Tab
# ---------------------------
with tab_ai:
    st.header("🤖 ChatGPT - OpenAI API")
    st.caption("Data Science Specialist - Powered by GPT-4o-mini")

    # session history
    if "ds_ai_chat_history" not in st.session_state:
        st.session_state.ds_ai_chat_history = []

    # API key (from secrets)
    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        st.warning("No API key found in .streamlit/secrets.toml — add OPENAI_API_KEY to enable chat.")

    # Fixed model
    model = "gpt-4o-mini"

    # Render chat history in a scrollable chat interface
    if st.session_state.ds_ai_chat_history:
        for msg in st.session_state.ds_ai_chat_history:
            role = msg.get("role", "assistant")
            content = msg.get("content", "")
            st.chat_message(role).write(content)
    else:
        st.info("Start the conversation by typing a message below.")

    # Chat insert
    user_input = st.chat_input("Ask the Data Science Specialist...")

    if user_input:
        if not api_key:
            st.error("No API key configured; cannot call OpenAI.")
        else:
            # retrieve temperature from session (set via controls below)
            temperature = st.session_state.get("ds_ai_temperature", 1.0)

            system_prompt = (
                "You are an AI & Data Science expert. Provide guidance on data modelling, ML workflow, "
                "evaluation, tooling, and reproducible experiments. Give clear, actionable suggestions and explain trade-offs."
            )

            history_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.ds_ai_chat_history]
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
            st.session_state.ds_ai_chat_history.append({"role": "user", "content": user_input})
            if assistant_text:
                st.session_state.ds_ai_chat_history.append({"role": "assistant", "content": assistant_text})

            st.rerun()

    # Controls at the bottom (expander)
    st.divider()
    with st.expander("⚙️ Chat Settings", expanded=False):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.metric("Messages", len(st.session_state.ds_ai_chat_history))
        with col2:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state.get("ds_ai_temperature", 1.0),
                step=0.1,
                help="Higher values make output more random",
                key="ds_ai_temperature"
            )
        with col3:
            if st.button("🗑 Clear Chat", use_container_width=True, key="ds_clear_chat"):
                st.session_state.ds_ai_chat_history = []
                st.rerun()

# ---------------------------
# Logout
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