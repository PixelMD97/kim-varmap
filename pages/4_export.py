import pandas as pd
import streamlit as st
from datetime import datetime

from ui_stepper import render_stepper, render_bottom_nav
from data_store import get_master_df, upsert_overlay_from_upload
from tree_utils import build_nodes_and_lookup


st.set_page_config(page_title="KIM VarMap – Export", layout="wide", initial_sidebar_state="collapsed")

render_stepper(current_step=3)

st.title("Export")
st.markdown("Review your selected variables and download them as a CSV.")

project_name = st.session_state.get("project_name", "").strip()
if project_name:
    st.markdown(f"Project: **{project_name}**")


def refresh_master_lookup():
    df_master = get_master_df()
    df_master_for_tree = df_master.drop(
        columns=[c for c in df_master.columns if str(c).startswith("__")],
        errors="ignore",
    )
    _, leaf_lookup_master = build_nodes_and_lookup(df_master_for_tree)
    st.session_state["leaf_lookup_master"] = leaf_lookup_master
    return leaf_lookup_master


# Ensure lookup exists even if user jumps directly to Export
leaf_lookup_master = st.session_state.get("leaf_lookup_master")
if not leaf_lookup_master:
    leaf_lookup_master = refresh_master_lookup()

checked = st.session_state.get("checked", [])
selected_rows = [leaf_lookup_master[v] for v in checked if v in leaf_lookup_master]

st.subheader("Selected variables")

if not selected_rows:
    st.info("No variables selected yet. Go to **Choose variables** and select some items.")
else:
    selected_df = pd.DataFrame(selected_rows)

    preferred_order = ["Variable", "Organ System", "Group", "Source", "EPIC ID", "PDMS ID", "Unit"]
    ordered_cols = [c for c in preferred_order if c in selected_df.columns] + \
                   [c for c in selected_df.columns if c not in preferred_order]
    selected_df = selected_df[ordered_cols]

    st.dataframe(selected_df, use_container_width=True, hide_index=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_project = (project_name or "kim_varmap").replace(" ", "_").replace("/", "_").lower()
    file_name = f"variablemapping_{safe_project}_{timestamp}.csv"

    csv_bytes = selected_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name=file_name,
        mime="text/csv",
    )

st.markdown("---")

st.subheader("Add a variable")
st.markdown("Add a custom variable here. It will be appended to your selected variables above.")

COMMON_UNITS = ["", "mmHg", "bpm", "%", "°C", "kg", "g/L", "mg/L", "mmol/L", "mL", "L/min", "score", "Other"]

with st.form("add_variable_form", clear_on_submit=True):
    variable = st.text_input("Variable *", placeholder="e.g. Creatinine")
    organ_system = st.text_input("Organ System", placeholder="e.g. Renal")
    group = st.text_input("Group", placeholder="e.g. Labs")
    source = st.selectbox("Source", options=["Both", "EPIC", "PDMS"], index=0)
    epic_id = st.text_input("EPIC ID", placeholder="e.g. E-CREA-001")
    pdms_id = st.text_input("PDMS ID", placeholder="e.g. P-CREA-001")

    unit_choice = st.selectbox("Unit", options=COMMON_UNITS, index=0)
    unit_other = ""
    if unit_choice == "Other":
        unit_other = st.text_input("Other unit", placeholder="e.g. U/L")

    submitted = st.form_submit_button("Add variable")

if submitted:
    variable_clean = variable.strip()
    if not variable_clean:
        st.error("Variable is required.")
    else:
        organ_system_clean = organ_system.strip() or "General"
        group_clean = group.strip() or "General"
        unit_clean = (unit_other.strip() if unit_choice == "Other" else unit_choice.strip())

        new_row = {
            "Variable": variable_clean,
            "Organ System": organ_system_clean,
            "Group": group_clean,
            "Source": source,
            "EPIC ID": epic_id.strip(),
            "PDMS ID": pdms_id.strip(),
            "Unit": unit_clean,
        }

        upload_df = pd.DataFrame([new_row])
        upsert_overlay_from_upload(upload_df)

        # IMPORTANT: refresh lookup so export can immediately display the new row
        leaf_lookup_master = refresh_master_lookup()

        # Select it globally
        leaf_value = f"{organ_system_clean}/{group_clean}/{variable_clean}"

        checked_set = set(st.session_state.get("checked", []))
        checked_all_set = set(st.session_state.get("checked_all_list", []))

        checked_set.add(leaf_value)
        checked_all_set.add(leaf_value)

        st.session_state["checked"] = sorted(list(checked_set))
        st.session_state["checked_all_list"] = sorted(list(checked_all_set))

        st.success("Variable added and selected.")
        st.rerun()

st.markdown("---")
render_bottom_nav(current_step=3)
