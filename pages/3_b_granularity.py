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
st.markdown(
    "Define how each selected variable should be extracted. "
    "You can keep raw values, add summaries, or create multiple variants per variable."
)


# -------------------------------------------------
# helpers
# -------------------------------------------------
SUMMARY_OPTIONS = ["Raw", "Lowest", "Highest", "Mean"]
TIME_OPTIONS = ["None", "Per day", "Per shift"]


def _init_granularity_rows():
    """
    Initialize one RAW row per selected variable
    """
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
            "Summary": "Raw",
            "Time basis": "None",
        })

    return rows


# -------------------------------------------------
# state init
# -------------------------------------------------
if "granularity_rows" not in st.session_state:
    st.session_state["granularity_rows"] = _init_granularity_rows()


# -------------------------------------------------
# build editable table
# -------------------------------------------------
df = pd.DataFrame(st.session_state["granularity_rows"])

if df.empty:
    st.info("No variables selected yet. Go back to **Choose variables**.")
    render_bottom_nav(current_step=4)
    st.stop()

df_display = df.copy()
df_display.insert(0, "Select", False)

edited = st.data_editor(
    df_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Select": st.column_config.CheckboxColumn(required=False),
        "Variable": st.column_config.TextColumn(disabled=True),
        "Summary": st.column_config.SelectboxColumn(
            options=SUMMARY_OPTIONS,
            required=True,
        ),
        "Time basis": st.column_config.SelectboxColumn(
            options=TIME_OPTIONS,
            required=True,
        ),
    },
)


# -------------------------------------------------
# write back edits
# -------------------------------------------------
df["Summary"] = edited["Summary"]
df["Time basis"] = edited["Time basis"]
df["Select"] = edited["Select"]


# -------------------------------------------------
# actions
# -------------------------------------------------
left, mid, right = st.columns([1, 2, 3])

with left:
    if st.button("➕ Duplicate selected"):
        new_rows = []
        for _, r in df[df["Select"]].iterrows():
            new = r.copy()
            new["row_id"] = str(uuid.uuid4())
            new["Select"] = False
            new_rows.append(new)

        if new_rows:
            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

with mid:
    if st.button("🗑 Delete selected"):
        df = df[~df["Select"]].copy()

with right:
    st.caption(
        "Tip: Duplicate a row to apply multiple summaries "
        "(e.g. Raw + Highest per day)."
    )


# -------------------------------------------------
# persist state
# -------------------------------------------------
df = df.drop(columns=["Select"], errors="ignore")
st.session_state["granularity_rows"] = df.to_dict(orient="records")


# -------------------------------------------------
# debug / preview (optional but useful)
# -------------------------------------------------
with st.expander("Preview extraction rows (debug)"):
    st.dataframe(df, use_container_width=True, hide_index=True)


st.markdown("---")
render_bottom_nav(current_step=4)
