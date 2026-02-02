import streamlit as st
from ui_stepper import render_stepper

st.set_page_config(
    page_title="KIM VarMap – Overview",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_stepper(current_step=0)


st.title("KIM VarMap")
st.caption(
    "A lightweight tool to browse, select, and export clinical variables "
    "with the corresponding EPIC/PDMS mapping."
)
st.markdown("### Project information")

left, right = st.columns([6, 1])

with left:
    project_name_input = st.text_input(
        "Project name",
        value=st.session_state.get("project_meta", {}).get("project_name", ""),
        key="project_name_input",
        placeholder="e.g., TEST STUDY …",
    )

    owner_email_input = st.text_input(
        "Your email",
        value=st.session_state.get("project_meta", {}).get("owner_email", ""),
        key="owner_email_input",
        placeholder="firstname.lastname@insel.ch",
        help="Primary contact person for this project",
    )

    collaborators_input = st.text_area(
        "Additional collaborators (optional)",
        value=", ".join(
            st.session_state.get("project_meta", {}).get("collaborators", [])
        ),
        key="collaborators_input",
        placeholder="email1@insel.ch, email2@insel.ch",
        help="Comma-separated list of collaborators invited to work on this project",
    )

with right:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)  # align vertically
    is_saved = bool(project_name_input.strip())
    if is_saved:
        st.markdown(
            "<div style='text-align:right; color: rgba(49,51,63,0.65); font-size: 0.95rem;'>✓ </div>",
            unsafe_allow_html=True,
        )

# store centrally for later steps
def _parse_emails(raw: str) -> list[str]:
    return [
        e.strip()
        for e in raw.split(",")
        if e.strip()
    ]


if project_name_input.strip():
    st.session_state["project_meta"] = {
        "project_name": project_name_input.strip(),
        "owner_email": owner_email_input.strip(),
        "collaborators": _parse_emails(collaborators_input),
    }


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

st.markdown(
    """
### Data usage & responsibilities

- blah blah 
retrospective data analysis.z u handen IDS-C. **datenschutzkonforme** manner
  and comply with applicable institutional and legal requirements. 

  
- If you receive an IDS-C dataset based on this mapping,  we will ask you to 
also ask to keep increasing mappings 
  **please return the final dataset or derived variable list **.
 
- all data processing complies with institutional DLF and data protection policies.
"""
)


st.markdown("---")
 
st.page_link("pages/2_data_source.py", label="Start →", use_container_width=True)


