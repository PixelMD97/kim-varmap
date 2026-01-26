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


# ---------- helpers ----------
def reset_overlay():
    st.session_state["overlay_df"] = pd.DataFrame()
    st.session_state.pop("last_import_summary", None)
    st.session_state.pop("last_upload_df", None)
    st.rerun()


def overlay_is_active() -> bool:
    overlay_df = st.session_state.get("overlay_df")
    return overlay_df is not None and len(overlay_df) > 0


# ---------- header ----------
st.title("Data source")


# ---------- setup choice ----------
st.subheader("Variable mapping setup")
st.caption("Select how you want to define the mapping before choosing variables.")

# small grey style
st.markdown(
    """
<style>
.kim-small-grey { color: rgba(49, 51, 63, 0.65); font-size: 0.9rem; }
.kim-small-grey-inline { color: rgba(49, 51, 63, 0.65); font-size: 0.9rem; margin-top: -0.2rem; }
</style>
""",
    unsafe_allow_html=True,
)

has_overlay = overlay_is_active()
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

# Only show dataset status if something "special" happened:
# - overlay is active OR
# - last upload summary exists
last_summary = st.session_state.get("last_import_summary")
if has_overlay or last_summary:
    total_rows = len(get_master_df())
    if has_overlay:
        st.markdown(
            f"<div class='kim-small-grey'>Current dataset: <b>Base mapping + uploaded overlay</b> · Total rows: <b>{total_rows}</b></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='kim-small-grey'>Current dataset: <b>Base mapping</b> · Total rows: <b>{total_rows}</b></div>",
            unsafe_allow_html=True,
        )

    if last_summary:
        added, updated, skipped = last_summary
        st.markdown(
            f"<div class='kim-small-grey'>Last upload: Added <b>{added}</b> · Updated <b>{updated}</b> · Skipped <b>{skipped}</b></div>",
            unsafe_allow_html=True,
        )

st.markdown("")  # space


# ---------- option: standard ----------
if choice.startswith("Use standard"): st.markdown( "<div class='kim-small-grey'>NOTE: For the "Standard Mapping", the centrally maintained base mapping will be used. No upload is required.</div>", unsafe_allow_html=True, )
    # show reset only if overlay exists
    if has_overlay:
        st.markdown("")
        if st.button("Reset upload (back to base mapping)", use_container_width=False):
            reset_overlay()


# ---------- option: upload ----------
else:
    st.markdown(
        "<div class='kim-small-grey-inline'>Upload a CSV to add/update mappings for this session.</div>",
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

    # reset button if overlay exists
    if overlay_is_active():
        st.markdown("")
        if st.button("Reset upload", use_container_width=False):
            reset_overlay()


st.markdown("---")
render_bottom_nav(current_step=1)
