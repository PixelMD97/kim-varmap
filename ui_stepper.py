import streamlit as st

_STEP_PAGES = {
    0: ("Overview", "pages/1_overview.py"),
    1: ("Data source", "pages/2_data_source.py"),
    2: ("Choose variables", "pages/3_choose_variable.py"),
    3: ("Export", "pages/4_export.py"),
}


def render_stepper(current_step: int):
    steps_order = [0, 1, 2, 3]

    def label_for(step_number: int, title: str) -> str:
        if step_number <= current_step:
            # active or completed
            return f"**{title}**" if step_number == 0 else f"**{step_number}. {title}**"
        else:
            # future
            return f"⬜ {title}" if step_number == 0 else f"{step_number}. {title}"

    cols = st.columns([1.2, 1.2, 1.8, 1.0])
    for col, step_number in zip(cols, steps_order):
        title, _ = _STEP_PAGES[step_number]
        col.markdown(label_for(step_number, title))

    st.markdown(
        "<hr style='margin: 0.6rem 0 1.0rem 0; opacity: 0.25;'>",
        unsafe_allow_html=True,
    )


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
