import streamlit as st
# You can import a shared navigation function here if you create one
# from navigation_helper import nav_menu

st.title("Page 1")
st.write("Welcome to Page 1! This page has unique content.")

# You can also use st.page_link for specific navigation links on the page body
if st.button("Go to Home"):
    st.switch_page("streamlit_app.py")
