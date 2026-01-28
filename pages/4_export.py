import pandas as pd
import streamlit as st
from datetime import datetime

from ui_stepper import render_stepper, render_bottom_nav
from data_store import get_master_df, upsert_overlay_from_upload

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


def load_selection_from_query_params_if_needed():
    if "selected_row_keys" in st.session_state and st.session_state["selected_row_keys"]:
        return

    sel = st.query_params.get("sel")
    if not sel:
        if "selected_row_keys" not in st.session_state:
            st.session_state["selected_row_keys"] = set()
        return

    if isinstance(sel, list):
        sel = sel[0] if sel else ""

    sel = str(sel).strip()
    keys = [k.strip() for k in sel.split(",") if k.strip()]
    st.session_state["selected_row_keys"] = set(keys)


def write_selection_to_query_params(selected_row_keys: set[str]):
    if selected_row_keys:
        st.query_params["sel"] = ",".join(sorted(selected_row_keys))
    else:
        try:
            del st.query_params["sel"]
        except Exception:
            pass


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

    preferred = ["Variable", "Organ System", "Group", "Source", "EPIC ID", "PDMS ID", "Unit", "Origin"]
    cols = [c for c in preferred if c in df_out.columns]

    hide_these = {"user_created", "user_uploaded_at"}
    extras = [c for c in df_out.columns if c not in cols and c not in hide_these]

    return df_out[cols + extras]


# -----------------------------
# selection state
# -----------------------------
if "selected_row_keys" not in st.session_state:
    st.session_state["selected_row_keys"] = set()

load_selection_from_query_params_if_needed()


# -----------------------------
# Selected variables table
# -----------------------------
st.subheader("Selected variables")

master_df = get_master_df()
selected_keys = st.session_state["selected_row_keys"]

if not selected_keys:
    st.info("No variables selected yet. Go to **Choose variables** and select some items.")
else:
    selected_df_raw = master_df[master_df["__row_key__"].astype(str).isin(set(map(str, selected_keys)))].copy()
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
# Add variable
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
        added, updated, skipped, processed_df = upsert_overlay_from_upload(upload_df)

        # Select newly created/updated rows by stable __row_key__
        new_keys = processed_df["__row_key__"].astype(str).tolist()

        selected_keys = set(st.session_state.get("selected_row_keys", set()))
        selected_keys.update(new_keys)

        st.session_state["selected_row_keys"] = selected_keys
        write_selection_to_query_params(selected_keys)

        st.success("Variable added and selected.")
        st.rerun()

st.markdown("---")
render_bottom_nav(current_step=3)
