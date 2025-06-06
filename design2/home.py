import streamlit as st

st.set_page_config(page_title="Welcome", layout="centered")

st.markdown("<h1 style='text-align: center;'>🌍 Pollution Tracker App</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Use the sidebar to navigate through the application.</p>", unsafe_allow_html=True)

st.image("assets/air.jpeg", width=600)  # optional image
