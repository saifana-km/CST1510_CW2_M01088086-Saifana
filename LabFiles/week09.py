import streamlit as st
import pandas as pd
import numpy as np

st.title("***Hello***")
st.text("Hi How R U")
st.markdown("Hi, *this is* `CST1510` class")

if st.button("Click me!"):
    st.write("Clicked!")

data = pd.DataFrame(
    np.random.randn(20,3),
    columns=["A","B","C"]
)
st.line_chart(data)
st.write(data)

with st.expander("See details"):
    st.write("Hidden Content")
    st.dataframe(data)


    