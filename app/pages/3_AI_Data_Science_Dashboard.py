import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
from datetime import datetime
from data.datasets import (
    insert_dataset,
    get_all_datasets,
    get_dataset_by_name,
    update_dataset_last_updated,
    update_dataset_record_count,
    delete_dataset,
    get_datasets_by_category,
    get_large_datasets
)

DB_PATH = "DATA/intelligence_platform.db"

# Page config
st.set_page_config(page_title="Datasets Metadata", layout="wide")

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
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

st.title("🗂️ Datasets Metadata Manager")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

# Navigation sections (Analytics / Metadata Manager / AI Chat Bot)
SECTIONS = ["Analytics", "Metadata Manager", "AI Chat Bot"]
st.sidebar.title("Navigation")
selection = st.sidebar.selectbox("Go to", SECTIONS)

# ---------------------------
# Analytics Section
# ---------------------------
if selection == "Analytics":
    st.header("📊 Metadata Analytics")
    st.markdown("*Overview of datasets metadata, counts and size distribution.*")
    st.divider()

    datasets = get_all_datasets()
    if datasets is None:
        datasets = pd.DataFrame()

    # Filters
    st.sidebar.subheader("Filters")
    if not datasets.empty:
        if "category" in datasets.columns:
            cats = ["All"] + sorted(datasets["category"].dropna().unique().tolist())
            cat_sel = st.sidebar.selectbox("Category", cats)
            if cat_sel != "All":
                datasets = datasets[datasets["category"] == cat_sel]

        if "last_updated" in datasets.columns:
            try:
                min_date = pd.to_datetime(datasets["last_updated"]).min()
                max_date = pd.to_datetime(datasets["last_updated"]).max()
                date_range = st.sidebar.slider(
                    "Last Updated Range",
                    min_value=min_date.to_pydatetime(),
                    max_value=max_date.to_pydatetime(),
                    value=(min_date.to_pydatetime(), max_date.to_pydatetime())
                )
                datasets = datasets[
                    (pd.to_datetime(datasets["last_updated"]) >= date_range[0]) &
                    (pd.to_datetime(datasets["last_updated"]) <= date_range[1])
                ]
            except Exception:
                pass

    st.subheader("Filtered Datasets")
    st.dataframe(datasets, use_container_width=True)

    # Visualizations via dropdown (pastel)
    st.subheader("Visualizations")
    chart_choice = st.selectbox("Choose visualization", [
        "Datasets by Category",
        "Record Count Distribution",
        "Size (MB) Distribution"
    ])

    if chart_choice == "Datasets by Category" and not datasets.empty and "category" in datasets.columns:
        cat_counts = datasets["category"].value_counts().reset_index()
        cat_counts.columns = ["category", "count"]
        pastel_palette = ["#FAD9E6", "#DDEBF7", "#E8F8E0", "#FFF1D6", "#F3E8FF", "#FFE4F1"]
        domain = cat_counts["category"].tolist()
        palette = (pastel_palette * ((len(domain) // len(pastel_palette)) + 1))[:len(domain)]
        chart = alt.Chart(cat_counts).mark_bar().encode(
            x="category",
            y="count",
            color=alt.Color("category", scale=alt.Scale(domain=domain, range=palette))
        )
        st.altair_chart(chart, use_container_width=True)

    if chart_choice == "Record Count Distribution" and not datasets.empty and "record_count" in datasets.columns:
        rc = datasets[["dataset_name", "record_count"]].dropna()
        hist = alt.Chart(rc).mark_bar(color="#AFCBFF").encode(
            alt.X("record_count:Q", bin=alt.Bin(maxbins=40), title="Record Count"),
            y='count()'
        )
        st.altair_chart(hist, use_container_width=True)

    if chart_choice == "Size (MB) Distribution" and not datasets.empty and "file_size_mb" in datasets.columns:
        sz = datasets[["dataset_name", "file_size_mb"]].dropna()
        hist = alt.Chart(sz).mark_bar(color="#FFD7A6").encode(
            alt.X("file_size_mb:Q", bin=alt.Bin(maxbins=40), title="File Size (MB)"),
            y='count()'
        )
        st.altair_chart(hist, use_container_width=True)

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
# Metadata Manager Section
# ---------------------------
elif selection == "Metadata Manager":
    st.header("🛠️ Metadata Manager")
    st.markdown("*Insert, update, search or delete dataset metadata.*")
    st.divider()

    datasets = get_all_datasets()
    if datasets is None:
        datasets = pd.DataFrame()

    cola, colb, colc, cold = st.columns(4)
    with cola:
        if st.button("Insert Metadata"):
            st.session_state.form = "A"
    with colb:
        if st.button("Update Last Updated"):
            st.session_state.form = "B"
    with colc:
        if st.button("Update Record Count"):
            st.session_state.form = "C"
    with cold:
        if st.button("Search / Delete"):
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
                new_id = insert_dataset(dataset_name, category, source, last_updated or None, int(record_count), float(file_size_mb))
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
                rows = update_dataset_last_updated(id_val, new_date)
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
                rows = update_dataset_record_count(id_val, int(new_count))
                if rows and rows > 0:
                    st.success(f"Dataset {id_val} record_count updated to {new_count}.")
                else:
                    st.error(f"No dataset found with ID {id_val}.")
                st.rerun()

    # Search and Delete combined
    elif st.session_state.form == "D":
        with st.form("search_delete"):
            query = st.text_input("Search by ID or Name (enter numeric id or part of dataset name)")
            col1, col2 = st.columns([3,1])
            with col1:
                search_btn = st.form_submit_button("Search")
            with col2:
                delete_btn = st.form_submit_button("Delete (by ID)")
            confirm_delete = st.checkbox("I confirm deletion (for delete action)")

        if search_btn and query:
            q = query.strip()
            try:
                id_val = int(q)
                df = get_dataset_by_name(id_val)
            except ValueError:
                conn = sqlite3.connect(DB_PATH)
                df = pd.read_sql_query("SELECT * FROM datasets_metadata WHERE dataset_name LIKE ? ORDER BY id DESC", conn, params=(f"%{q}%",))
                conn.close()

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
                    rows = delete_dataset(id_val)
                    if rows and rows > 0:
                        st.success(f"Dataset id={id_val} deleted.")
                    else:
                        st.error(f"No dataset found with ID {id_val}.")
                    st.rerun()

# ---------------------------
# AI Chat Bot Section
# ---------------------------
elif selection == "AI Chat Bot":
    st.header("🤖 AI Chat Bot")
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