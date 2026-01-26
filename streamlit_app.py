import streamlit as st

st.set_page_config(
    page_title="KIM VarMap",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",  
)

st.title("KIM VarMap")

st.markdown("""
### Workflow
1) **Overview** – what’s in the dataset right now  
2) **Data source** – load / upload mapping CSV  
3) **Choose variables** – select in the tree  
4) **Export** – download selected rows  

Use the sidebar to navigate.
""")
