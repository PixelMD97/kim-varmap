import streamlit as st

_STEP_PAGES = {
    0: ("Overview", "pages/1_overview.py"),
    1: ("Data source", "pages/2_data_source.py"),
    2: ("Choose variables", "pages/3_choose_variable.py"),
    3: ("Export", "pages/4_export.py"),
}

 

def render_stepper(current_step: int):
    st.markdown(
        """
        <style>
        .stepper-bar {
            background-color: #f3f7fb;
            padding: 0.6rem 1.2rem 0.4rem 1.2rem;
            border-bottom: 1px solid rgba(49,51,63,0.08);
            margin-bottom: 1.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='stepper-bar'>", unsafe_allow_html=True)

    cols = st.columns([1.2, 1.2, 1.8, 1.0])

    labels = ["Overview", "1. Data source", "2. Choose variables", "3. Export"]

    for col, label in zip(cols, labels):
        col.markdown(f"**{label}**" if label.startswith(str(current_step)) else label)

    st.markdown("</div>", unsafe_allow_html=True)


def render_bottom_nav(current_step: int):
    back_step = current_step - 1 if current_step > 0 else None
    next_step = current_step + 1 if current_step < 3 else None

    left, spacer, right = st.columns([1, 6, 1])

    with left:
        if back_step is not None:
            _, back_page = _STEP_PAGES[back_step]
            st.page_link(back_page, label="← Back", use_container_width=True)

    with right:
        if next_step is not None:
            _, next_page = _STEP_PAGES[next_step]
            st.page_link(next_page, label="Next →", use_container_width=True)
