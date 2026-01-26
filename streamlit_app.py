import streamlit as st

st.set_page_config(
    page_title="KIM VarMap",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.switch_page("pages/1_overview.py")
