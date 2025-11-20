import streamlit as st
import pandas as pd
import numpy as np

st.title("Hi, I am Saifana! 😎")
st.subheader("This is my first Streamlit program.")

st.header("**About Me:**")
st.markdown("- I **like** `cats` 🐈")
st.markdown("- I **like** `birds` 🐦")

df = pd.DataFrame({
    "name":["Alice","Bob","Charlie"],
    "age":[25,32,29]
})

st.dataframe(df)

st.divider()

data = pd.DataFrame(
    np.random.randn(20,5),
    columns=["A","B","C","D","E"]
)

st.line_chart(data)
st.dataframe(data)

st.divider()

st.image(r"C:\Users\saifa\OneDrive\Pictures\Camera Roll\dance-fun.gif", caption="Dancing Dudes",use_container_width=True)