import streamlit as st
import pandas as pd
from data_store import load_base_df, get_master_df, upsert_overlay_from_upload

from ui_stepper import render_stepper
render_stepper(current_step=1)


st.set_page_config(page_title="KIM VarMap – Load Data", layout="wide")
st.title("Load / Import Data")

st.markdown("""
This page defines **which data exists** in the application.
blaaaaaaaaaaaaaaaaaaaaaaaaaaah""")

# ---------------------------
# Base dataset
# ---------------------------
base_df = load_base_df()
st.subheader("Base dataset")
st.caption(f"{len(base_df)} rows loaded from base file")
st.dataframe(base_df.head(20), use_container_width=True)

# ---------------------------
# Upload CSV
# ---------------------------
st.subheader("Upload mapping CSV")

with st.expander("Rules for upload"):
    st.markdown("""
**Allowed**
- Add new rows 
**Required**
- `Variable` must exist and be non-empty

**Stable updates only**blaaaaaaaaaaaaaaaaaaaaah
""")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="upload_master_csv")

if uploaded_file is not None:
    try:
        raw_upload_df = pd.read_csv(uploaded_file)
        added, updated, skipped, processed_df = upsert_overlay_from_upload(raw_upload_df)

        # ---------------------------
        # Auto-check every uploaded row in the Tree
        # ---------------------------
        checked_set = set(st.session_state.get("checked", []))

        for _, row in processed_df.iterrows():
            os_name = str(row.get("Organ System", "New")).strip() or "New"
            group = str(row.get("Group", "New")).strip() or "New"
            var = str(row.get("Variable", "")).strip()

            if var:
                leaf_value = f"{os_name}/{group}/{var}"
                checked_set.add(leaf_value)

        st.session_state["checked"] = list(checked_set)

        # Optional: collapse tree so user sees a clean tree when navigating
        st.session_state["expanded"] = []

        st.success(f"Import successful ✅ Added: {added} | Updated: {updated} | Skipped: {skipped}")
        st.info("All uploaded rows were automatically selected in the Tree.")
        st.info("Go to the **Tree** or **Selected Table** page to continue.")

    except Exception as e:
        st.error(f"Import failed: {e}")


# ---------------------------
# Debug / transparency
# ---------------------------
st.subheader("Current master dataset (debug)")
master_df = get_master_df()
st.caption(f"Total rows in master view: {len(master_df)}")
st.dataframe(master_df.head(50), use_container_width=True)
