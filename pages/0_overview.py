import streamlit as st
from ui_stepper import render_stepper

render_stepper(current_step=0)

st.title("KIM VarMap")
st.caption(
    "A lightweight tool to browse, select, and export clinical variables "
    "with the corresponding EPIC/PDMS mapping."
)

st.markdown("### Project information")
project_name = st.text_input(
    "Project name"
)

# store centrally for later steps
if project_name:
    st.session_state["project_name"] = project_name.strip()

st.markdown("### How it works")
st.markdown(
    """
1. **Data source** – Choose whether you want to load the base mapping table (standard) and optionally upload your own files to work on.
2. **Choose variables** – Browse or search the complete available list of variables and select the variables you need.
3. **Export** – Review your selection and download as a CSV.
"""
)

st.markdown("### What you get")
st.markdown(
    "- A clean CSV export of selected variables (with identifiers and metadata), "
    "named using your project and the export date."
)

st.markdown("---")

st.page_link("pages/0_loadfrom.py", label="Start →", use_container_width=True)
