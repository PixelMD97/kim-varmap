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


def load_selection_from_query_params_if_needed():
    """
    Persist selection across browser reloads via URL query param ?sel=...
    """
    if "selected_row_keys" in st.session_state and st.session_state["selected_row_keys"]:
        return

    sel = st.query_params.get("sel")
    if not sel:
        return

    # sel can be string or list depending on Streamlit version
    if isinstance(sel, list):
        sel = sel[0] if sel else ""

    sel = str(sel).strip()
    if not sel:
        return

    keys = [k.strip() for k in sel.split(",") if k.strip()]
    st.session_state["selected_row_keys"] = set(keys)


def write_selection_to_query_params(selected_row_keys: set[str]):
    if selected_row_keys:
        st.query_params["sel"] = ",".join(sorted(selected_row_keys))
    else:
        # remove param if empty
        try:
            del st.query_params["sel"]
        except Exception:
            pass


# -----------------------------
# state init
# -----------------------------
if "selected_row_keys" not in st.session_state:
    st.session_state["selected_row_keys"] = set()
if "expanded" not in st.session_state:
    st.session_state["expanded"] = []

load_selection_from_query_params_if_needed()


# -----------------------------
# load + build tree
# -----------------------------
df_master = get_master_df()
nodes, _leaf_lookup_master = build_nodes_and_lookup(df_master)  # stable leaf ids: ROW:<__row_key__>

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
# tree widget (checked = leaves)
# -----------------------------
checked_leaf_values = [f"ROW:{rk}" for rk in sorted(st.session_state["selected_row_keys"])]

selected = tree_select(
    nodes,
    checked=checked_leaf_values,
    expanded=st.session_state["expanded"],
    key="var_tree",
)

checked_now = selected.get("checked", [])
expanded_now = selected.get("expanded", [])

# only keep leaves (ROW:...)
selected_row_keys_now = set()
for v in checked_now:
    if isinstance(v, str) and v.startswith("ROW:"):
        selected_row_keys_now.add(v.replace("ROW:", "", 1))

st.session_state["selected_row_keys"] = selected_row_keys_now
st.session_state["expanded"] = expanded_now

# persist across reloads
write_selection_to_query_params(selected_row_keys_now)


st.markdown("---")
render_bottom_nav(current_step=2)
