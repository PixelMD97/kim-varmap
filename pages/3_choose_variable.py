# pages/3_choose_variable.py
import streamlit as st
from streamlit_tree_select import tree_select

from tree_utils import build_nodes_and_lookup
from data_store import get_master_df
from ui_stepper import render_stepper, render_bottom_nav


# -------------------------------------------------
# page config
# -------------------------------------------------
st.set_page_config(
    page_title="KIM VarMap – Choose variables",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_stepper(current_step=3)

st.title("Choose variables")
st.markdown("Expand the categories and select the variables you need.")
st.markdown(
    "<div style='opacity:0.6; font-size:0.85rem;'>"
    "Tip: Use <b>Ctrl+F</b> in your browser to quickly find text on the page."
    "</div>",
    unsafe_allow_html=True,
)

project_name = (
    st.session_state.get("project_meta", {})
    .get("project_name", "")
    .strip()
)
if project_name:
    st.markdown(f"Project: **{project_name}**")


# -------------------------------------------------
# helpers
# -------------------------------------------------
def reset_tree_widget_state():
    if "var_tree" in st.session_state:
        del st.session_state["var_tree"]


def compute_all_expand_values(tree_nodes):
    expanded = set()

    def walk(nodes):
        for n in nodes:
            if isinstance(n, dict) and n.get("children"):
                expanded.add(n.get("value"))
                walk(n["children"])

    walk(tree_nodes)
    return sorted(v for v in expanded if v is not None)


def normalize_checked_values_to_row_format(values: list[str]) -> list[str]:
    """
    Enforce canonical format: ROW:<row_key>
    """
    out = []
    seen = set()

    for v in values or []:
        if not isinstance(v, str):
            continue

        v = v.strip()
        if not v:
            continue

        if v.startswith("ROW:"):
            rk = v.replace("ROW:", "")
        elif "|" in v:
            rk = v.split("|")[-1].strip()
        else:
            continue

        if rk and rk not in seen:
            out.append(f"ROW:{rk}")
            seen.add(rk)

    return out


# -------------------------------------------------
# state init
# -------------------------------------------------
st.session_state.setdefault("checked", [])
st.session_state.setdefault("checked_all_list", [])
st.session_state.setdefault("expanded", [])

st.session_state["checked"] = normalize_checked_values_to_row_format(
    st.session_state["checked"]
)
st.session_state["checked_all_list"] = normalize_checked_values_to_row_format(
    st.session_state["checked_all_list"]
)


# -------------------------------------------------
# load + filter data
# -------------------------------------------------
df_master = get_master_df()

# apply EPIC / PDMS / BOTH
source_filter = st.session_state.get("source_filter", "Both")
if source_filter != "Both":
    df_master = df_master[
        df_master["source"].str.upper() == source_filter.upper()
    ]

# apply visibility
df_master = df_master[df_master["is_visible"] == True]

# -------------------------------------------------
# HARD safety: remove selections for hidden rows
# -------------------------------------------------
valid_row_keys = set(df_master["__row_key__"].astype(str))

def _filter_checked(values):
    return [
        v for v in values
        if v.startswith("ROW:")
        and v.replace("ROW:", "") in valid_row_keys
    ]

st.session_state["checked"] = _filter_checked(st.session_state["checked"])
st.session_state["checked_all_list"] = _filter_checked(
    st.session_state["checked_all_list"]
)

# -------------------------------------------------
# build tree (AFTER filtering!)
# -------------------------------------------------
nodes, leaf_lookup_master = build_nodes_and_lookup(df_master)
st.session_state["leaf_lookup_master"] = leaf_lookup_master

all_expand_values = compute_all_expand_values(nodes)


# -------------------------------------------------
# controls
# -------------------------------------------------
ctrl_cols = st.columns([1, 1, 6])

with ctrl_cols[0]:
    if st.button("Expand all", use_container_width=True):
        st.session_state["expanded"] = all_expand_values
        reset_tree_widget_state()
        st.rerun()

with ctrl_cols[1]:
    if st.button("Collapse all", use_container_width=True):
        st.session_state["expanded"] = []
        reset_tree_widget_state()
        st.rerun()


# -------------------------------------------------
# tree widget
# -------------------------------------------------
selected = tree_select(
    nodes,
    checked=st.session_state["checked_all_list"],
    expanded=st.session_state["expanded"],
    key="var_tree",
)

checked_now = normalize_checked_values_to_row_format(
    selected.get("checked", [])
)

st.session_state["checked"] = checked_now
st.session_state["checked_all_list"] = checked_now
st.session_state["expanded"] = selected.get("expanded", [])


st.markdown("---")
render_bottom_nav(current_step=3)
