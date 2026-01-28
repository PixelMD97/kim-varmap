# pages/3_choose_variable.py
import streamlit as st
from streamlit_tree_select import tree_select

from tree_utils import build_nodes_and_lookup
from data_store import get_master_df
from ui_stepper import render_stepper, render_bottom_nav


st.set_page_config(
    page_title="KIM VarMap – Choose variables",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_stepper(current_step=2)

st.title("Choose variables")
st.markdown("Expand the categories and select the variables you need.")
st.markdown(
    "<div style='opacity:0.6; font-size:0.85rem;'>Tip: Use <b>Ctrl+F</b> in your browser to quickly find text on the page.</div>",
    unsafe_allow_html=True,
)

project_name = st.session_state.get("project_name", "").strip()
if project_name:
    st.markdown(f"Project: **{project_name}**")


# -----------------------------
# helpers
# -----------------------------
def reset_tree_widget_state():
    # tree_select stores its internal state under the widget key
    if "var_tree" in st.session_state:
        del st.session_state["var_tree"]


def compute_all_expand_values(tree_nodes):
    expanded_values = set()

    def walk(node_list):
        for node in node_list:
            if isinstance(node, dict) and node.get("children"):
                expanded_values.add(node.get("value"))
                walk(node.get("children", []))

    walk(tree_nodes)
    return sorted([v for v in expanded_values if v is not None])


def normalize_checked_values_to_row_format(checked_values: list) -> list[str]:
    """
    Convert any legacy leaf values to the new stable format.

    New format:  "ROW:<__row_key__>"
    Old format:  "<os>/<group>/<var>|<row_key>"

    We keep only:
    - values starting with ROW:
    - OR convert legacy values that contain a trailing "|<row_key>"
    """
    normalized = []

    for v in checked_values or []:
        if not isinstance(v, str):
            continue

        v = v.strip()
        if not v:
            continue

        # already new format
        if v.startswith("ROW:"):
            normalized.append(v)
            continue

        # legacy format: "...|<row_key>"
        if "|" in v:
            maybe_row_key = v.split("|")[-1].strip()
            if maybe_row_key:
                normalized.append(f"ROW:{maybe_row_key}")
            continue

        # everything else is ignored (OS:..., GR:..., etc.)
    # de-dup while preserving order
    seen = set()
    out = []
    for x in normalized:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


# -----------------------------
# state init (keep old keys)
# -----------------------------
if "checked_all_list" not in st.session_state:
    st.session_state["checked_all_list"] = []
if "checked" not in st.session_state:
    st.session_state["checked"] = []
if "expanded" not in st.session_state:
    st.session_state["expanded"] = []

# normalize once on load so older sessions don't break
st.session_state["checked_all_list"] = normalize_checked_values_to_row_format(st.session_state["checked_all_list"])
st.session_state["checked"] = normalize_checked_values_to_row_format(st.session_state["checked"])


# -----------------------------
# load + build tree
# IMPORTANT: do NOT drop __row_key__ anymore
# -----------------------------
df_master = get_master_df()
nodes, leaf_lookup_master = build_nodes_and_lookup(df_master)

# store lookup for other pages if they still rely on it
st.session_state["leaf_lookup_master"] = leaf_lookup_master

all_expand_values = compute_all_expand_values(nodes)


# -----------------------------
# controls row
# -----------------------------
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


# -----------------------------
# tree
# -----------------------------
selected = tree_select(
    nodes,
    checked=st.session_state["checked_all_list"],
    expanded=st.session_state["expanded"],
    key="var_tree",
)

checked_now = selected.get("checked", [])
expanded_now = selected.get("expanded", [])

# normalize checked output too (defensive)
checked_now_normalized = normalize_checked_values_to_row_format(checked_now)

st.session_state["checked_all_list"] = checked_now_normalized
st.session_state["checked"] = checked_now_normalized  # used by export
st.session_state["expanded"] = expanded_now


st.markdown("---")
render_bottom_nav(current_step=2)
