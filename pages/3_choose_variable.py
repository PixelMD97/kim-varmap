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


# ---- helpers ----
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


# ---- state init ----
if "checked_all_list" not in st.session_state:
    st.session_state["checked_all_list"] = []
if "expanded" not in st.session_state:
    st.session_state["expanded"] = []


# ---- load + build tree ----
df_master = get_master_df()
df_master_for_tree = df_master.drop(
    columns=[c for c in df_master.columns if str(c).startswith("__")],
    errors="ignore",
)
nodes, leaf_lookup_master = build_nodes_and_lookup(df_master_for_tree)
st.session_state["leaf_lookup_master"] = leaf_lookup_master

all_expand_values = compute_all_expand_values(nodes)


# ---- controls row ----
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


# ---- tree ----
selected = tree_select(
    nodes,
    checked=st.session_state["checked_all_list"],
    expanded=st.session_state["expanded"],
    key="var_tree",
)

checked_now = selected.get("checked", [])
expanded_now = selected.get("expanded", [])

st.session_state["checked_all_list"] = checked_now
st.session_state["checked"] = checked_now  # used by export
st.session_state["expanded"] = expanded_now


st.markdown("---")
render_bottom_nav(current_step=2)
