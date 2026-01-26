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
# Minimal "card" styling
# -----------------------------
st.markdown(
    """
<style>
/* Center the main card a bit and give it a soft feel */
.kim-card {
    max-width: 920px;
    margin: 0 auto;
    padding: 1.6rem 1.8rem;
    border-radius: 16px;
    border: 1px solid rgba(49, 51, 63, 0.12);
    box-shadow: 0 10px 24px rgba(0,0,0,0.06);
    background: white;
}
.kim-card h3 {
    margin-top: 0;
    margin-bottom: 0.25rem;
}
.kim-muted {
    opacity: 0.75;
    font-size: 0.95rem;
}
.kim-rules {
    border-radius: 12px;
    padding: 0.9rem 1rem;
    border: 1px solid rgba(49, 51, 63, 0.12);
    background: rgba(49, 51, 63, 0.03);
}
.kim-actions {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------
# Title + helper text
# -----------------------------
st.title("Data source")
st.markdown(
    "<div class='kim-muted'>Choose how you want to define the variable mapping for this session.</div>",
    unsafe_allow_html=True,
)

st.markdown("")


# -----------------------------
# Status summary (small, reassuring)
# -----------------------------
overlay_df = st.session_state.get("overlay_df")
has_overlay = overlay_df is not None and len(overlay_df) > 0

master_df = get_master_df()
total_rows = len(master_df)

status_left, status_right = st.columns([2, 3])

with status_left:
    if has_overlay:
        st.success(f"**Current dataset:** Base mapping + uploaded overlay\n\n**Total rows:** {total_rows}")
    else:
        st.info(f"**Current dataset:** Base mapping\n\n**Total rows:** {total_rows}")

with status_right:
    last_summary = st.session_state.get("last_import_summary")
    if last_summary:
        added, updated, skipped = last_summary
        st.write("**Last upload:**")
        st.write(f"- Added: **{added}**")
        st.write(f"- Updated: **{updated}**")
        st.write(f"- Skipped: **{skipped}**")


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

# Default selection: use base mapping, unless overlay already exists
default_choice = "Upload custom mapping CSV (optional)" if has_overlay else "Use standard mapping (recommended)"

choice = st.radio(
    "Mapping option",
    options=[
        "Use standard mapping (recommended)",
        "Upload custom mapping CSV (optional)",
    ],
    index=0 if default_choice.startswith("Use standard") else 1,
    label_visibility="collapsed",
)

# ---- Option 1: Base mapping ----
if choice.startswith("Use standard"):
    st.markdown(
        """
**Use standard mapping (recommended)**  
The centrally maintained base mapping will be used. No upload is required.
"""
    )

    # If user currently has overlay but chooses base, allow one-click reset
    if has_overlay:
        st.warning("You currently have an uploaded overlay active. Reset it to return to base mapping only.")
        if st.button("Reset upload (back to base mapping)", use_container_width=True):
            st.session_state["overlay_df"] = pd.DataFrame()
            st.session_state.pop("last_import_summary", None)
            st.session_state.pop("last_uploaded_preview", None)
            st.rerun()

# ---- Option 2: Upload overlay ----
else:
    st.markdown(
        """
**Upload custom mapping CSV (optional)**  
Add or update variables by uploading your own mapping file.
"""
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

            # store summary for the top status box
            st.session_state["last_import_summary"] = (added, updated, skipped)

            # store a preview for this page (not the full dataset)
            st.session_state["last_uploaded_preview"] = processed_df.copy()

            st.success(f"Upload applied ✅  Added: {added} | Updated: {updated} | Skipped: {skipped}")

        except Exception as e:
            st.error(f"Import failed: {e}")

    # After upload actions (only if overlay exists)
    overlay_df = st.session_state.get("overlay_df")
    has_overlay_now = overlay_df is not None and len(overlay_df) > 0

    if has_overlay_now:
        st.markdown("")
        action_cols = st.columns([1, 1, 3])

        with action_cols[0]:
            if st.button("Reset upload", use_container_width=True):
                st.session_state["overlay_df"] = pd.DataFrame()
                st.session_state.pop("last_import_summary", None)
                st.session_state.pop("last_uploaded_preview", None)
                st.rerun()

        with action_cols[1]:
            preview_df = st.session_state.get("last_uploaded_preview")
            if preview_df is not None and len(preview_df) > 0:
                with st.expander("Preview uploaded rows"):
                    st.dataframe(preview_df.head(20), use_container_width=True)
            else:
                # fallback: show overlay preview if we don't have the processed_df stored
                with st.expander("Preview uploaded rows"):
                    st.dataframe(overlay_df.head(20), use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Bottom CTA
# -----------------------------
st.markdown("")
st.markdown("---")

st.page_link(
    "pages/3_choose_variable.py",
    label="Continue → Choose variables",
    use_container_width=True,
)

render_bottom_nav(current_step=1)
