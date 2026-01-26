import streamlit as st
import pandas as pd

from ui_stepper import render_stepper, render_bottom_nav
from data_store import get_master_df, upsert_overlay_from_upload


st.set_page_config(
    page_title="KIM VarMap – Data source",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_stepper(current_step=1)


def reset_overlay():
    st.session_state["overlay_df"] = pd.DataFrame()
    st.session_state.pop("last_import_summary", None)
    st.session_state.pop("last_upload_df", None)
    st.rerun()


# ---- Header (minimal) ----
st.title("Data source")
st.caption("Choose how you want to define the variable mapping for this session.")

# ---- Status (only show the actual state; keep it short) ----
overlay_df = st.session_state.get("overlay_df")
has_overlay = overlay_df is not None and len(overlay_df) > 0
total_rows = len(get_master_df())

if has_overlay:
    st.success(f"Current dataset: **Base mapping + uploaded overlay**  \nTotal rows: **{total_rows}**")
else:
    st.info(f"Current dataset: **Base mapping**  \nTotal rows: **{total_rows}**")

st.markdown("")

# ---- Setup choice ----
st.subheader("Variable mapping setup")
st.caption("Select how you want to define the mapping before choosing variables.")

default_index = 1 if has_overlay else 0
choice = st.radio(
    label="Mapping option",
    options=[
        "Use standard mapping (recommended)",
        "Upload custom mapping CSV (optional)",
    ],
    index=default_index,
    label_visibility="collapsed",
)

# Small grey description next to the option (your request)
st.markdown(
    """
<style>
.kim-small-grey { color: rgba(49, 51, 63, 0.65); font-size: 0.9rem; }
</style>
""",
    unsafe_allow_html=True,
)

if choice.startswith("Use standard"):
    st.markdown(
        "<div class='kim-small-grey'>NOTE: For the "Standard Mapping", the centrally maintained base mapping will be used. No upload is required.</div>",
        unsafe_allow_html=True,
    )

    # only show reset if there is an overlay
    if has_overlay:
        st.markdown("")
        if st.button("Reset upload (back to base mapping)", use_container_width=False):
            reset_overlay()

else:
    st.markdown(
        "<div class='kim-small-grey'>Upload a CSV to add/update mappings for this session.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("")
    st.markdown("**Upload rules**")
    st.markdown(
        """
- **Required:** `Variable` must be present and non-empty  
- **Supported:** add new variables; update existing variables (**exact match only**)  
- **Not supported:** deleting base variables; ambiguous updates
"""
    )

    st.markdown("**Example rows (Source column)**")
    st.code(
        "Variable,Source,EPIC ID,PDMS ID,Organ System,Group\n"
        "Heart Rate,Both,E-HR-001,P-EHR-001,Cardiology,Heart\n"
        "Sodium,EPIC,E-NA-001,,Electrolytes,Blood\n"
        "Intracranial Pressure,PDMS,,P-ICP-001,Neurology,Brain",
        language="text",
    )

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="upload_master_csv")

    if uploaded_file is not None:
        try:
            raw_upload_df = pd.read_csv(uploaded_file)
            added, updated, skipped, processed_df = upsert_overlay_from_upload(raw_upload_df)

            st.session_state["last_import_summary"] = (added, updated, skipped)
            st.session_state["last_upload_df"] = processed_df.copy()

            st.success(f"Upload applied ✅ Added: {added} | Updated: {updated} | Skipped: {skipped}")

            with st.expander("Preview uploaded rows"):
                st.dataframe(processed_df.head(20), use_container_width=True)

        except Exception as e:
            st.error(f"Import failed: {e}")

    # show reset if overlay exists
    overlay_df = st.session_state.get("overlay_df")
    has_overlay = overlay_df is not None and len(overlay_df) > 0
    if has_overlay:
        st.markdown("")
        if st.button("Reset upload", use_container_width=False):
            reset_overlay()

st.markdown("---")
render_bottom_nav(current_step=1)
