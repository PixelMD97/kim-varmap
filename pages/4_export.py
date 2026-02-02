# pages/4_export.py
import pandas as pd
import streamlit as st
from datetime import datetime

from ui_stepper import render_stepper, render_bottom_nav
from data_store import get_master_df, upsert_overlay_from_upload


# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="KIM VarMap – Export",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_stepper(current_step=5)

st.title("Export")
st.markdown("Review your selected variables and download them as a CSV.")

project_name = (
    st.session_state.get("project_meta", {})
    .get("project_name", "")
    .strip()
)

if project_name:
    st.markdown(f"Project: **{project_name}**")


# -------------------------------------------------
# Load state
# -------------------------------------------------
granularity_rows = st.session_state.get("granularity_rows", [])

if not granularity_rows:
    st.info("No variables selected yet. Go back to **Choose variables**.")
    render_bottom_nav(current_step=5)
    st.stop()

gran_df = pd.DataFrame(granularity_rows)
master_df = get_master_df()


# -------------------------------------------------
# Merge granularity + master data
# -------------------------------------------------
export_df = gran_df.merge(
    master_df,
    how="left",
    left_on="row_key",
    right_on="__row_key__",
)


# -------------------------------------------------
# Origin + inferred Source (DEFENSIVE)
# -------------------------------------------------
export_df["Origin"] = "Base"

if "user_created" in export_df.columns:
    export_df.loc[export_df["user_created"] == True, "Origin"] = "User created"

if "user_uploaded_at" in export_df.columns:
    export_df.loc[export_df["user_uploaded_at"].notna(), "Origin"] = "User upload"


def infer_source(row):
    epic = str(row.get("EPIC ID", "")).strip()
    pdms = str(row.get("PDMS ID", "")).strip()

    if epic and pdms:
        return "Both"
    if epic:
        return "EPIC"
    if pdms:
        return "PDMS"
    return ""


export_df["Source"] = export_df.apply(infer_source, axis=1)


# -------------------------------------------------
# Final display table (DEFENSIVE)
# -------------------------------------------------
DISPLAY_COLUMNS = [
    "Variable",
    "Organ System",
    "Group",
    "Source",
    "EPIC ID",
    "PDMS ID",
    "Unit",
    "Origin",
    "Summary",
    "Time basis",
]

# ensure all columns exist
for col in DISPLAY_COLUMNS:
    if col not in export_df.columns:
        export_df[col] = ""

table_df = export_df[DISPLAY_COLUMNS].copy()
table_df.insert(0, "Delete", False)

st.subheader("Selected variables")

edited = st.data_editor(
    table_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Delete": st.column_config.CheckboxColumn(""),
        "Variable": st.column_config.TextColumn(disabled=True),
        "Organ System": st.column_config.TextColumn(disabled=True),
        "Group": st.column_config.TextColumn(disabled=True),
        "Source": st.column_config.TextColumn(disabled=True),
        "EPIC ID": st.column_config.TextColumn(disabled=True),
        "PDMS ID": st.column_config.TextColumn(disabled=True),
        "Unit": st.column_config.TextColumn(disabled=True),
        "Origin": st.column_config.TextColumn(disabled=True),
        "Summary": st.column_config.TextColumn(disabled=True),
        "Time basis": st.column_config.TextColumn(disabled=True),
    },
)


# -------------------------------------------------
# Delete selected rows
# -------------------------------------------------
if st.button("🗑 Delete selected"):
    keep_mask = ~edited["Delete"]
    kept = gran_df.loc[keep_mask.values].copy()

    st.session_state["granularity_rows"] = kept.to_dict(orient="records")
    st.success("Selected rows removed.")
    st.rerun()


# -------------------------------------------------
# CSV export (WYSIWYG)
# -------------------------------------------------
csv_df = export_df[DISPLAY_COLUMNS].copy()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
safe_project = (project_name or "kim_varmap").replace(" ", "_").lower()

csv_bytes = csv_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv_bytes,
    file_name=f"variablemapping_{safe_project}_{timestamp}.csv",
    mime="text/csv",
)


# -------------------------------------------------
# Add variable
# -------------------------------------------------
st.markdown("---")
st.subheader("Add a variable")

COMMON_UNITS = [
    "", "mmHg", "bpm", "%", "°C", "kg", "g/L",
    "mg/L", "mmol/L", "mL", "L/min", "score", "Other"
]

with st.form("add_variable_form", clear_on_submit=True):
    variable = st.text_input("Variable *", placeholder="e.g. Creatinine")
    organ_system = st.text_input("Organ system", placeholder="e.g. Renal")
    group = st.text_input("Group", placeholder="e.g. Labs")

    epic_id = st.text_input("EPIC ID")
    pdms_id = st.text_input("PDMS ID")

    unit_choice = st.selectbox("Unit", options=COMMON_UNITS)
    unit_other = ""
    if unit_choice == "Other":
        unit_other = st.text_input("Other unit")

    submitted = st.form_submit_button("Add variable")


# -------------------------------------------------
# Helper text (small grey)
# -------------------------------------------------
st.markdown(
    """
<div style="color: rgba(49,51,63,0.65); font-size: 0.9rem; margin-top: -0.5rem;">
You can add new variables to help this project grow organically.<br><br>

• Please provide a <b>clear variable name</b><br>
• Define <b>at least one identifier</b> (EPIC ID or PDMS ID)<br>
• Make an <b>educated guess</b> for organ system and group<br><br>

If your entry matches our standard mapping, it will automatically appear in the correct category.
Otherwise, it will be listed alphabetically under your specified group.<br><br>

We really appreciate contributions that improve and extend the mapping 🙏<br><br>

For questions or batch uploads, please contact:<br>
<b>xxx@insel.ch</b><br>
You can also send batch-mapped variables (EPIC / PDMS IDs) to:<br>
<b>xxx2@insel.ch</b>
</div>
""",
    unsafe_allow_html=True,
)


# -------------------------------------------------
# Handle submit
# -------------------------------------------------
if submitted:
    if not variable.strip():
        st.error("Variable name is required.")
        st.stop()

    epic_clean = epic_id.strip()
    pdms_clean = pdms_id.strip()

    if not epic_clean and not pdms_clean:
        st.error("Please provide at least one identifier (EPIC ID or PDMS ID).")
        st.stop()

    unit_clean = unit_other.strip() if unit_choice == "Other" else unit_choice

    new_row = {
        "Variable": variable.strip(),
        "Organ System": organ_system.strip() or "General",
        "Group": group.strip() or "General",
        "EPIC ID": epic_clean,
        "PDMS ID": pdms_clean,
        "Unit": unit_clean,
    }

    upload_df = pd.DataFrame([new_row])
    added, updated, skipped, processed_df = upsert_overlay_from_upload(upload_df)

    if processed_df is not None and "__row_key__" in processed_df.columns:
        for rk in processed_df["__row_key__"]:
            st.session_state["granularity_rows"].append({
                "row_id": rk,
                "row_key": rk,
                "Variable": variable.strip(),
                "Summary": "Raw",
                "Time basis": "None",
            })

    st.success("Variable added.")
    st.rerun()


st.markdown("---")
render_bottom_nav(current_step=5)
