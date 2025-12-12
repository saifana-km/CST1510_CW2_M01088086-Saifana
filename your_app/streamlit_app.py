import streamlit as st

st.set_page_config(page_title="Dropdown Navigation Example")

PAGES = {
    "Home": "home_page",
    "Page 1": "page_1",
    "Page 2": "page_2"
}

st.sidebar.title("Navigation")
selection = st.sidebar.selectbox("Go to", list(PAGES.keys()))

st.title(selection)

if selection == "Home":
    st.write("This is the home page.")
elif selection == "Page 1":
    st.write("This is page 1.")
elif selection == "Page 2":
    st.write("This is page 2.")