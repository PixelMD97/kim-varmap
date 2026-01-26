import streamlit as st
import pandas as pd

from ui_stepper import render_stepper, render_bottom_nav
from data_store import get_master_df, upsert_overlay_from_upload


# -----------------------------
# Page config (must be first)
# -----------------------------
st.set_page_config(
    page_title="KIM VarMap – Data source",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_stepper(current_step=1)


# -----------------------------
# Minimal styling (card + rules box)
# -----------------------------
st.markdown(
    """
<style>
.kim-card {
  max-width: 920px;
  margin: 0 auto;
  padding: 1.4rem 1.6rem;
  border-radius: 16px;
  border: 1px solid rgba(49, 51, 63, 0.12);
  box-shadow: 0 10px 24px rgba(0,0,0,0.06);
  background: white;
}
.kim-muted { opacity: 0.75; font-size: 0.95rem; }
.kim-rules {
  border-radius: 12px;
  padding: 0.9rem 1rem;
  border: 1px solid rgba(49, 51, 63, 0.12);
  background: rgba(49, 51, 63, 0.03);
}
</style>
""",
    unsafe_allow_html=True,
)


def reset_overlay():
    st.session_state["overlay_df"] = pd.DataFrame()
    st.session_state.pop("last_import_summary", None)
    st.session_state.pop("last_upload_df", None)
    st.rerun()


# -----------------------------
# Header
# -----------------------------
st.title("Data source")
st.markdown(
    "<div class='kim-muted'>Choose how you want to define the variable mapping for this session.</div>",
    unsafe_allow_html=True,
)
st.markdown("")


# -----------------------------
# Status (simple)
# -----------------------------
overlay_df = st.session_state.get("overlay_df")
has_overlay = overlay_df is not None and len(overlay_df) > 0
total_rows = len(get_master_df())

if has_overlay:
    st.success(f"**Current dataset:** Base mapping + uploaded overlay  \n**Total rows:** {total_rows}")
else:
    st.info(f"**Current dataset:** Base mapping  \n**Total rows:** {total_rows}")

last_summary = st.session_state.get("last_import_summary")
if last_summary:
    added, updated, skipped = last_summary
    st.caption(f"Last upload — Added: {added} | Updated: {updated} | Skipped: {skipped}")

st.markdown("")


# -----------------------------
# Main setup card
# -----------------------------
st.markdown("<div class='kim-card'>", unsafe_allow_html=True)

st.markdown("### Variable mapping setup")
st.markdown(
    "<div class='kim-muted'>Select how you want to define the mapping before choosing variables.</div>",
    unsafe_allow_html=True,
)
st.markdown("")

default_index = 1 if has_overlay else 0
choice = st.radio(
    "Mapping option",
    ["Use standard mapping (recommended)", "Upload custom mapping CSV (optional)"],
    index=default_index,
    label_visibility="collapsed",
)

if choice.startswith("Use standard"):
    st.markdown(
        "**Use standard mapping (recommended)**  \n"
        "The centrally maintained base mapping will be used. No upload is required."
    )

    if has_overlay:
        st.warning("An uploaded overlay is currently active.")
        if st.button("Reset upload (back to base mapping)", use_container_width=True):
            reset_overlay()

else:
    st.markdown(
        "**Upload custom mapping CSV (optional)**  \n"
        "Add or update variables by uploading your own mapping file."
    )
    st.markdown("")

    st.markdown("<div class='kim-rules'>", unsafe_allow_html=True)
    st.markdown(
        """
**Upload rules**

**Required**
- `Variable` must be present and non-empty

**Supported**
- Add new variables
- Update existing variables (**exact match only**)

**Not supported**
- Deleting base variables
- Ambiguous updates
"""
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="upload_master_csv")

    if uploaded_file is not None:
        try:
            raw_upload_df = pd.read_csv(uploaded_file)
            added, updated, skipped, processed_df = upsert_overlay_from_upload(raw_upload_df)

            st.session_state["last_import_summary"] = (added, updated, skipped)
            st.session_state["last_upload_df"] = processed_df.copy()

            st.success(f"Upload applied ✅ Added: {added} | Updated: {updated} | Skipped: {skipped}")

        except Exception as e:
            st.error(f"Import failed: {e}")

    # After upload actions
    overlay_df = st.session_state.get("overlay_df")
    has_overlay = overlay_df is not None and len(overlay_df) > 0
    if has_overlay:
        btn_cols = st.columns([1, 2, 5])

        with btn_cols[0]:
            if st.button("Reset upload", use_container_width=True):
                reset_overlay()

        with btn_cols[1]:
            with st.expander("Preview uploaded rows"):
                preview_df = st.session_state.get("last_upload_df")
                if preview_df is None or len(preview_df) == 0:
                    preview_df = overlay_df
                st.dataframe(preview_df.head(20), use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Continue
# -----------------------------
st.markdown("")
st.markdown("---")

st.page_link("pages/3_choose_variable.py", label="Continue → Choose variables", use_container_width=True)
render_bottom_nav(current_step=1)
