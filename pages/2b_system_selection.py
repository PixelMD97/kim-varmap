import streamlit as st
from ui_stepper import render_stepper, render_bottom_nav

st.set_page_config(
    page_title="KIM VarMap – Data source system",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_stepper(current_step=2)

st.title("Data source system")
st.markdown(
    "Select which system(s) you want to extract variables from. "
    "This only affects visibility – data itself is not deleted."
)

st.caption(
    "You can change this later. All variables remain available in the background."
)

choice = st.radio(
    "Available source",
    options=["Both", "EPIC", "PDMS"],
    index=["Both", "EPIC", "PDMS"].index(
        st.session_state.get("source_filter", "Both")
    ),
)

# 🔐 single source of truth
st.session_state["source_filter"] = choice

render_bottom_nav(current_step=2)

