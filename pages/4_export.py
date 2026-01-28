# pages/4_export.py
import pandas as pd
import streamlit as st
from datetime import datetime

from ui_stepper import render_stepper, render_bottom_nav
from data_store import get_master_df, upsert_overlay_from_upload
from tree_utils import build_nodes_and_lookup


st.set_page_config(
    page_title="KIM VarMap – Export",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_stepper(current_step=3)

st.title("Export")
st.markdown("Review your selected variables and download them as a CSV.")

project_name = st.session_state.get("project_name", "").strip()
if project_name:
    st.markdown(f"Project: **{project_name}**")


# -----------------------------
# helpers
# -----------------------------
def refresh_master_lookup():
    """
    Rebuild a lookup from the current master df.

    IMPORTANT:
    - With the updated tree_utils.py, build_nodes_and_lookup requires __row_key__.
    - Do NOT drop __ columns here anymore.
    """
    df_master = get_master_df()
    _, leaf_lookup_master = build_nodes_and_lookup(df_master)
    st.session_state["leaf_lookup_master"] = leaf_lookup_master
    return leaf_lookup_master


def normalize_checked_values_to_row_format(checked_values: list) -> list[str]:
    """
    Convert any legacy leaf values to the new stable format.

    New format:  "ROW:<__row_key__>"
    Old format:  "<os>/<group>/<var>|<row_key>"
    """
    normalized = []

    for v in checked_values or []:
        if not isinstance(v, str):
            continue

        v = v.strip()
        if not v:
            continue

        if v.startswith("ROW:"):
            normalized.append(v)
            continue

        if "|" in v:
            maybe_row_key = v.split("|")[-1].strip()
            if maybe_row_key:
                normalized.append(f"ROW:{maybe_row_key}")
            continue

    # de-dup while preserving order
    seen = set()
    out = []
    for x in normalized:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


def build_export_view(df_selected: pd.DataFrame) -> pd.DataFrame:
    df_out = df_selected.copy()

    # Hide internal columns
    df_out = df_out.drop(columns=[c for c in df_out.columns if str(c).startswith("__")], errors="ignore")

    # Ensure provenance columns exist
    if "user_created" not in df_out.columns:
        df_out["user_created"] = False
    if "user_uploaded_at" not in df_out.columns:
        df_out["user_uploaded_at"] = pd.NA

    # Friendly origin column
    df_out["Origin"] = "Base"
    df_out.loc[df_out["user_uploaded_at"].notna(), "Origin"] = "User upload"
    df_out.loc[df_out["user_created"] == True, "Origin"] = "User created"

    # Visible columns
    preferred = ["Variable", "Organ System", "Group", "Source", "EPIC ID", "PDMS ID", "Unit", "Origin"]
    cols = [c for c in preferred if c in df_out.columns]

    # Append other non-provenance columns (optional)
    hide_these = {"user_created", "user_uploaded_at"}
    extras = [c for c in df_out.columns if c not in cols and c not in hide_these]

    return df_out[cols + extras]


# -----------------------------
# ensure state keys exist
# -----------------------------
if "checked" not in st.session_state:
    st.session_state["checked"] = []
if "checked_all_list" not in st.session_state:
    st.session_state["checked_all_list"] = []

# normalize (handles users who still have legacy leaf values in state)
st.session_state["checked"] = normalize_checked_values_to_row_format(st.session_state["checked"])
st.session_state["checked_all_list"] = normalize_checked_values_to_row_format(st.session_state["checked_all_list"])


# -----------------------------
# Ensure lookup exists even if user jumps directly to Export
# -----------------------------
leaf_lookup_master = st.session_state.get("leaf_lookup_master")
if not leaf_lookup_master:
    leaf_lookup_master = refresh_master_lookup()


# -----------------------------
# Selected variables
# -----------------------------
st.write("DEBUG checked count:", len(st.session_state.get("checked", [])))
st.write("DEBUG checked sample:", st.session_state.get("checked", [])[:5])

checked = st.session_state.get("checked", [])
selected_rows = [leaf_lookup_master[v] for v in checked if v in leaf_lookup_master]

st.subheader("Selected variables")

if not selected_rows:
    st.info("No variables selected yet. Go to **Choose variables** and select some items.")
else:
    selected_df_raw = pd.DataFrame(selected_rows)
    export_view = build_export_view(selected_df_raw)

    st.dataframe(export_view, use_container_width=True, hide_index=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_project = (project_name or "kim_varmap").replace(" ", "_").replace("/", "_").lower()
    file_name = f"variablemapping_{safe_project}_{timestamp}.csv"

    csv_bytes = export_view.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name=file_name,
        mime="text/csv",
    )

st.markdown("---")


# -----------------------------
# Add a variable
# -----------------------------
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

        # Refresh lookup so export can immediately display the new row
        leaf_lookup_master = refresh_master_lookup()

        # Keep prior selections + select the new row
        checked_set = set(st.session_state.get("checked", []))
        checked_all_set = set(st.session_state.get("checked_all_list", []))

        # Find the leaf value that matches the new row in the refreshed lookup
        leaf_value_to_select = None
        for leaf_value, row_dict in leaf_lookup_master.items():
            if (
                str(row_dict.get("Variable", "")).strip() == variable_clean
                and str(row_dict.get("Organ System", "")).strip() == organ_system_clean
                and str(row_dict.get("Group", "")).strip() == group_clean
                and str(row_dict.get("Source", "")).strip() == str(source).strip()
                and str(row_dict.get("EPIC ID", "")).strip() == epic_id.strip()
                and str(row_dict.get("PDMS ID", "")).strip() == pdms_id.strip()
                and str(row_dict.get("Unit", "")).strip() == unit_clean
            ):
                leaf_value_to_select = leaf_value
                break

        if leaf_value_to_select is None:
            st.warning("Variable added, but could not auto-select it in the tree. Please select it manually.")
        else:
            # leaf_value_to_select will be "ROW:<row_key>" now
            checked_set.add(leaf_value_to_select)
            checked_all_set.add(leaf_value_to_select)

            st.session_state["checked"] = sorted(list(checked_set))
            st.session_state["checked_all_list"] = sorted(list(checked_all_set))

            st.success("Variable added and selected.")
            st.rerun()

st.markdown("---")
render_bottom_nav(current_step=3)

