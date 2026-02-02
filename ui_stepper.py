import streamlit as st

# -------------------------------------------------
# Step registry (single source of truth)
# -------------------------------------------------
_STEP_PAGES = {
    0: ("Overview", "pages/1_overview.py"),
    1: ("Data source", "pages/2_data_source.py"),
    2: ("Data source system", "pages/2b_source_selection.py"),
    3: ("Choose variables", "pages/3_choose_variable.py"),
    4: ("Granularity", "pages/granularity.py"),
    5: ("Export", "pages/4_export.py"),
}

_MAX_STEP = max(_STEP_PAGES.keys())


# -------------------------------------------------
# Top stepper (clickable past steps)
# -------------------------------------------------
def render_stepper(current_step: int):
    cols = st.columns(len(_STEP_PAGES))

    for step_number, col in zip(_STEP_PAGES.keys(), cols):
        title, page = _STEP_PAGES[step_number]

        if step_number < current_step:
            # completed → clickable
            col.page_link(page, label=f"{step_number}. {title}")
        elif step_number == current_step:
            # active
            col.markdown(f"**{step_number}. {title}**")
        else:
            # future
            col.markdown(f"{step_number}. {title}")

    st.markdown(
        "<hr style='margin: 0.6rem 0 1.0rem 0; opacity: 0.25;'>",
        unsafe_allow_html=True,
    )


# -------------------------------------------------
# Bottom navigation (Back / Next)
# -------------------------------------------------
def render_bottom_nav(current_step: int):
    back_step = current_step - 1 if current_step > 0 else None
    next_step = current_step + 1 if current_step < _MAX_STEP else None

    left, spacer, right = st.columns([1, 6, 1])

    with left:
        if back_step is not None:
            _, back_page = _STEP_PAGES[back_step]
            st.page_link(back_page, label="← Back", use_container_width=True)

    with right:
        if next_step is not None:
            _, next_page = _STEP_PAGES[next_step]
            st.page_link(next_page, label="Next →", use_container_width=True)
