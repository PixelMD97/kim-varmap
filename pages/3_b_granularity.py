# pages/granularity.py
import uuid
import pandas as pd
import streamlit as st

from ui_stepper import render_stepper, render_bottom_nav
from data_store import get_master_df


# -------------------------------------------------
# page config
# -------------------------------------------------
st.set_page_config(
    page_title="KIM VarMap – Granularity",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_stepper(current_step=4)

st.title("Granularity")


# -------------------------------------------------
# EARLY EXIT: standard extraction
# -------------------------------------------------
if not st.session_state.get("use_custom_granularity", False):
    st.markdown(
        """
### Standard extraction selected

You chose to **keep standard extraction**.

- All selected variables will be exported as **raw values**
- No aggregation (mean / min / max)
- No time grouping (per day / per shift)

This is the recommended option for most use cases.
"""
    )

    st.caption(
        "If you want to derive daily summaries or other aggregates, "
        "you can enable custom granularity below."
    )

    if st.button("Enable custom granularity"):
        st.session_state["use_custom_granularity"] = True
        st.rerun()

    st.markdown("---")
    render_bottom_nav(current_step=4)
    st.stop()


# -------------------------------------------------
# Custom granularity editor (opt-in)
# -------------------------------------------------
st.markdown(
    """
Define **how** each selected variable should be extracted.

- Keep raw values
- Add summaries (lowest / highest / mean)
- Create multiple variants per variable
"""
)

SUMMARY_OPTIONS = ["Keep raw values", "Lowest", "Highest", "Mean"]
TIME_OPTIONS = ["None", "Per day", "Per shift"]


def _init_granularity_rows():
    master_df = get_master_df()
    selected = st.session_state.get("checked", [])

    rows = []
    for leaf_value in selected:
        row_key = leaf_value.replace("ROW:", "")
        row = master_df.loc[master_df["__row_key__"] == row_key]
        if row.empty:
            continue

        r = row.iloc[0]
        rows.append({
            "row_id": str(uuid.uuid4()),
            "row_key": row_key,
            "Variable": r.get("Variable", ""),
            "Summary": "Keep raw values",
            "Time basis": "None",
        })

    return rows


# -------------------------------------------------
# state init
# -------------------------------------------------
if "granularity_rows" not in st.session_state:
    st.session_state["granularity_rows"] = _init_granularity_rows()


df = pd.DataFrame(st.session_state["granularity_rows"])

if df.empty:
    st.info("No variables selected yet. Go back to **Choose variables**.")
    render_bottom_nav(current_step=4)
    st.stop()


# -------------------------------------------------
# editor
# -------------------------------------------------
df_display = df.copy()
df_display.insert(0, "Select", False)

edited = st.data_editor(
    df_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Select": st.column_config.CheckboxColumn(),
        "Variable": st.column_config.TextColumn(disabled=True),
        "Summary": st.column_config.SelectboxColumn(options=SUMMARY_OPTIONS),
        "Time basis": st.column_config.SelectboxColumn(options=TIME_OPTIONS),
    },
)

df["Summary"] = edited["Summary"]
df["Time basis"] = edited["Time basis"]
df["Select"] = edited["Select"]


# -------------------------------------------------
# actions
# -------------------------------------------------
left, mid, right = st.columns([1, 2, 3])

with left:
    if st.button("➕ Duplicate selected"):
        clones = []
        for _, r in df[df["Select"]].iterrows():
            c = r.copy()
            c["row_id"] = str(uuid.uuid4())
            c["Select"] = False
            clones.append(c)
        if clones:
            df = pd.concat([df, pd.DataFrame(clones)], ignore_index=True)

with mid:
    if st.button("🗑 Delete selected"):
        df = df[~df["Select"]].copy()

with right:
    st.caption(
        "Duplicate rows to create multiple summaries "
        "(e.g. raw + highest per day)."
    )


# -------------------------------------------------
# persist
# -------------------------------------------------
df = df.drop(columns=["Select"], errors="ignore")
st.session_state["granularity_rows"] = df.to_dict(orient="records")


st.markdown("---")
render_bottom_nav(current_step=4)
