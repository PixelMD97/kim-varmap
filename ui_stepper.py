import streamlit as st

_STEP_LABELS = {
    0: "Overview",
    1: "1. Data source",
    2: "2. Choose variables",
    3: "3. Export",
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
        .step-inactive {
            color: rgba(49,51,63,0.55);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='stepper-bar'>", unsafe_allow_html=True)

    cols = st.columns([1.2, 1.2, 1.8, 1.0])

    for step, col in zip([0, 1, 2, 3], cols):
        label = _STEP_LABELS[step]

        if step == current_step:
            col.markdown(f"**{label}**")
        else:
            col.markdown(f"<span class='step-inactive'>{label}</span>", unsafe_allow_html=True)

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
