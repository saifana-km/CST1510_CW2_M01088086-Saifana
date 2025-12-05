import streamlit as st
import pandas as pd
from datetime import datetime
from data.db import connect_database
from data.datasets import (
    get_dataset_by_name,
    get_all_datasets,
    get_datasets_by_category,
    get_large_datasets,
    insert_dataset,
    update_dataset_last_updated,
    update_dataset_record_count,
    delete_dataset
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
st.title("📊 AI Data Science Records")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

conn = connect_database('DATA/intelligence_platform.db')
tickets = get_all_datasets()
st.dataframe(tickets, use_container_width=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Accuracy","94.2%")
with col2:
    st.metric("Precision","91.8%")
with col3:
    st.metric("Recall","89.5%")

history = pd.DataFrame({
    "epoch":[1,2,3,4,5],
    "loss":[0.45,0.32,0.24,0.18,0.15],
    "accuracy":[0.78,0.85,0.89,0.92,0.94]
})
st.line_chart(history, x="epoch", y=["loss","accuracy"])