import streamlit as st
import pandas as pd

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
    "Define how each selected variable should be aggregated and over which time reference."
)

# -------------------------------------------------
# ensure state
# -------------------------------------------------
st.session_state.setdefault("granularity_config", {})
checked = st.session_state.get("checked", [])

if not checked:
    st.info("No variables selected yet. Please select variables first.")
    render_bottom_nav(current_step=4)
    st.stop()

# -------------------------------------------------
# load selected variables
# -------------------------------------------------
df_master = get_master_df()
row_lookup = {f"ROW:{rk}": row for rk, row in zip(df_master["__row_key__"], df_master.to_dict("records"))}

selected_rows = [row_lookup[v] for v in checked if v in row_lookup]
df_selected = pd.DataFrame(selected_rows)

st.subheader("Selected variables")

st.dataframe(
    df_selected[["Variable", "Organ System", "Group", "Source"]],
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# -------------------------------------------------
# Granularity editor (placeholder)
# -------------------------------------------------
st.subheader("Granularity settings")

AGGREGATIONS = ["mean", "min", "max", "median", "first", "last"]
TIME_ANCHORS = [
    "ICU admission",
    "Hospital admission",
    "Randomization",
    "Procedure start",
]
TIME_WINDOWS = [
    "Instant",
    "0–6h",
    "0–24h",
    "24–48h",
    "Entire stay",
]

for _, row in df_selected.iterrows():
    row_key = row["__row_key__"]
    label = f'{row["Variable"]} ({row["Source"]})'

    with st.expander(label, expanded=False):
        cfg = st.session_state["granularity_config"].get(row_key, {})

        agg = st.selectbox(
            "Aggregation",
            AGGREGATIONS,
            index=AGGREGATIONS.index(cfg.get("aggregation", "mean")),
            key=f"agg_{row_key}",
        )

        anchor = st.selectbox(
            "Time anchor",
            TIME_ANCHORS,
            index=TIME_ANCHORS.index(cfg.get("time_anchor", "ICU admission")),
            key=f"anchor_{row_key}",
        )

        window = st.selectbox(
            "Time window",
            TIME_WINDOWS,
            index=TIME_WINDOWS.index(cfg.get("time_window", "Instant")),
            key=f"window_{row_key}",
        )

        allow_dup = st.checkbox(
            "Allow multiple values (duplicates)",
            value=cfg.get("allow_duplicates", False),
            key=f"dup_{row_key}",
        )

        # persist
        st.session_state["granularity_config"][row_key] = {
            "aggregation": agg,
            "time_anchor": anchor,
            "time_window": window,
            "allow_duplicates": allow_dup,
        }

st.markdown("---")

# -------------------------------------------------
# Debug / transparency (temporary)
# -------------------------------------------------
with st.expander("🔍 Current granularity config (debug)"):
    st.json(st.session_state["granularity_config"])

render_bottom_nav(current_step=4)
