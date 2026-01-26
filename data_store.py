import uuid
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_CSV_PATH = Path("data/clinical_variable_mapping_50_entries.csv")

CORE_COLS = ["Organ System", "Group", "Variable"]
ID_COLS = ["EPIC ID", "PDMS ID"]


def ensure_required_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in CORE_COLS:
        if col not in df.columns:
            df[col] = None
    for col in ID_COLS + ["Source"]:
        if col not in df.columns:
            df[col] = ""
    return df


def normalize_grouping(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Organ System"] = df["Organ System"].fillna("").astype(str).str.strip()
    df["Group"] = df["Group"].fillna("").astype(str).str.strip()
    df["Variable"] = df["Variable"].fillna("").astype(str).str.strip()

    # force New branch if missing (for display/grouping)
    df.loc[df["Organ System"] == "", "Organ System"] = "New"
    df.loc[df["Group"] == "", "Group"] = "New"
    return df


def normalize_ids(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["EPIC ID", "PDMS ID", "Source"]:
        df[col] = df[col].fillna("").astype(str).str.strip()
    return df


def stable_id_key_from_row(row: pd.Series) -> str:
    """
    Stable identity ONLY if EPIC ID or PDMS ID exists.
    Otherwise return empty string => meaning "no stable identity".
    """
    epic_id = str(row.get("EPIC ID", "")).strip()
    pdms_id = str(row.get("PDMS ID", "")).strip()

    if epic_id:
        return f"EPIC:{epic_id}"
    if pdms_id:
        return f"PDMS:{pdms_id}"
    return ""


def load_base_df() -> pd.DataFrame:
    """
    Base rows:
    - if EPIC/PDMS exists => stable key (EPIC:... / PDMS:...)
    - else => stable-ish base-only key so base rows remain unique (but NOT updateable via upload)
    """
    base_df = pd.read_csv(BASE_CSV_PATH)
    base_df = ensure_required_cols(base_df)
    base_df = normalize_grouping(base_df)
    base_df = normalize_ids(base_df)

    # Build keys
    base_keys = []
    for i, row in base_df.iterrows():
        stable_key = stable_id_key_from_row(row)
        if stable_key:
            base_keys.append(stable_key)
        else:
            # base-only fallback (does NOT enable "updates" without IDs)
            # this is just to keep base rows uniquely addressable
            var = row.get("Variable", "")
            os_name = row.get("Organ System", "")
            group = row.get("Group", "")
            src = row.get("Source", "")
            base_keys.append(f"BASE:{var}|OS:{os_name}|GR:{group}|SRC:{src}|IDX:{i}")

    base_df["__row_key__"] = base_keys
    base_df["__origin__"] = "base"
    return base_df


def get_master_df() -> pd.DataFrame:
    """
    master = base + overlay
    overlay wins if same __row_key__ (i.e., same EPIC/PDMS ID)
    """
    base_df = load_base_df()

    overlay_df = st.session_state.get("overlay_df")
    if overlay_df is None or len(overlay_df) == 0:
        return base_df

    overlay_df = overlay_df.copy()
    overlay_df = ensure_required_cols(overlay_df)
    overlay_df = normalize_grouping(overlay_df)
    overlay_df = normalize_ids(overlay_df)

    # overlay must already have __row_key__; if not, we keep it safe
    if "__row_key__" not in overlay_df.columns:
        overlay_df["__row_key__"] = [f"NEW:{uuid.uuid4()}" for _ in range(len(overlay_df))]

    overlay_df["__origin__"] = "user"

    combined = pd.concat([base_df, overlay_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=["__row_key__"], keep="last")
    return combined

def upsert_overlay_from_upload(upload_df: pd.DataFrame) -> tuple[int, int, int, pd.DataFrame]:
    """
    Import policy:
    - Stable identity ONLY if EPIC ID or PDMS ID exists.
    - If EPIC/PDMS exists AND already present in base/overlay => UPDATE (user_created=False)
    - If EPIC/PDMS exists AND not present yet => NEW (user_created=True, user_uploaded_at set)
    - If no EPIC/PDMS => ALWAYS NEW (unique key) (user_created=True, user_uploaded_at set)

    Returns: (added, updated, skipped, processed_df_for_auto_checking)
    """
    import uuid
    import pandas as pd
    import streamlit as st

    upload_df = upload_df.copy()
    upload_df.columns = [str(c).strip() for c in upload_df.columns]

    upload_df = ensure_required_cols(upload_df)
    upload_df = normalize_grouping(upload_df)
    upload_df = normalize_ids(upload_df)

    # skip rows without Variable
    upload_df["Variable"] = upload_df["Variable"].fillna("").astype(str).str.strip()
    valid_mask = upload_df["Variable"] != ""
    skipped = int((~valid_mask).sum())
    upload_df = upload_df.loc[valid_mask].copy()

    # -------- build set of existing stable keys (EPIC:/PDMS:) from base + overlay --------
    base_df = load_base_df()
    existing_overlay = st.session_state.get("overlay_df")

    existing_stable_keys = set()
    for k in base_df["__row_key__"].astype(str).tolist():
        if k.startswith("EPIC:") or k.startswith("PDMS:"):
            existing_stable_keys.add(k)

    if existing_overlay is not None and len(existing_overlay) > 0 and "__row_key__" in existing_overlay.columns:
        for k in existing_overlay["__row_key__"].astype(str).tolist():
            if k.startswith("EPIC:") or k.startswith("PDMS:"):
                existing_stable_keys.add(k)

    # -------- assign keys + mark new vs update --------
    now_iso = pd.Timestamp.now().isoformat(timespec="seconds")

    row_keys = []
    is_new_flags = []

    for _, row in upload_df.iterrows():
        stable_key = stable_id_key_from_row(row)

        if stable_key:
            # If stable key already exists => UPDATE (not user_created)
            if stable_key in existing_stable_keys:
                row_keys.append(stable_key)
                is_new_flags.append(False)
            else:
                # NEW stable identity
                row_keys.append(stable_key)
                is_new_flags.append(True)
                existing_stable_keys.add(stable_key)  # avoid counting duplicates within same upload as new twice
        else:
            # No IDs => ALWAYS NEW
            row_keys.append(f"NEW:{uuid.uuid4()}")
            is_new_flags.append(True)

    upload_df["__row_key__"] = row_keys
    upload_df["__origin__"] = "user"

    # Only truly new rows are user_created + get uploaded_at
    upload_df["user_created"] = is_new_flags
    upload_df["user_uploaded_at"] = [now_iso if flag else "" for flag in is_new_flags]

    # -------- merge into overlay --------
    if existing_overlay is None or len(existing_overlay) == 0:
        st.session_state["overlay_df"] = upload_df
        added = int(sum(is_new_flags))
        updated = int(len(upload_df) - added)
        return added, updated, skipped, upload_df

    existing_overlay = existing_overlay.copy()
    if "__row_key__" not in existing_overlay.columns:
        existing_overlay["__row_key__"] = [f"NEW:{uuid.uuid4()}" for _ in range(len(existing_overlay))]

    before_keys = set(existing_overlay["__row_key__"].astype(str).tolist())
    incoming_keys = set(upload_df["__row_key__"].astype(str).tolist())

    updated = 0
    for k in incoming_keys:
        if (k.startswith("EPIC:") or k.startswith("PDMS:")) and (k in before_keys):
            updated += 1

    added = len(incoming_keys - before_keys)

    combined = pd.concat([existing_overlay, upload_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=["__row_key__"], keep="last")

    st.session_state["overlay_df"] = combined
    return added, updated, skipped, upload_df

