# tree_utils.py
import hashlib
import json


def _make_row_key(row: dict, cols: list[str]) -> str:
    """
    Create a stable short hash from relevant row content.

    IMPORTANT:
    - This should only be used when you *first* create __row_key__ for rows.
    - Do NOT call this inside build_nodes_and_lookup(), because selection must
      remain stable even if the dataframe columns change.
    """
    payload = {c: row.get(c) for c in cols}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:10]


def build_nodes_and_lookup(df):
    """
    Build the tree nodes and a lookup dict from leaf_value -> row_dict.

    KEY POINT:
    - Leaves are identified by a STABLE value: "ROW:<__row_key__>"
    - This function expects '__row_key__' to already exist in df.
      (Create it once in your data loading/upsert logic, not here.)
    """
    df = df.copy()

    # Fill hierarchy columns for grouping
    for col in ["Organ System", "Group", "Variable"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str)

    # We require row identity to be present and stable
    if "__row_key__" not in df.columns:
        raise ValueError(
            "build_nodes_and_lookup expects '__row_key__' to already exist in df. "
            "Create it once in data_store.get_master_df() / upsert_overlay_from_upload()."
        )

    # Ensure row_key is string and unique
    df["__row_key__"] = df["__row_key__"].astype(str)

    # Keep last occurrence for duplicates (overlay updates, etc.)
    df = df.drop_duplicates(subset=["__row_key__"], keep="last")

    nodes = []
    leaf_lookup = {}

    # Sort for stable tree ordering
    df_sorted = df.sort_values(["Organ System", "Group", "Variable"])

    for os_name, os_df in df_sorted.groupby("Organ System", dropna=False):
        os_name = str(os_name)

        os_node = {
            "label": os_name,
            "value": f"OS:{os_name}",
            "children": [],
        }

        for group_name, group_df in os_df.groupby("Group", dropna=False):
            group_name = str(group_name)

            group_node = {
                "label": group_name,
                "value": f"GR:{os_name}/{group_name}",
                "children": [],
            }

            for _, row in group_df.iterrows():
                var = str(row.get("Variable", "")).strip()
                row_key = str(row["__row_key__"]).strip()

                # human label
                label_parts = [var] if var else ["(Unnamed variable)"]
                source = row.get("Source")
                if source:
                    label_parts.append(f"({source})")
                label = " ".join(label_parts)

                # STABLE leaf value (selection-safe)
                leaf_value = f"ROW:{row_key}"

                leaf = {"label": label, "value": leaf_value}
                group_node["children"].append(leaf)

                # lookup leaf -> full row dict
                leaf_lookup[leaf_value] = row.to_dict()

            os_node["children"].append(group_node)

        nodes.append(os_node)

    return nodes, leaf_lookup


def compute_row_key_from_df_row(row: dict, dedup_cols: list[str]) -> str:
    """
    Compute a stable __row_key__ for a row, given the exact columns that define identity.

    Use this in:
    - initial base dataset creation (if needed)
    - upload/upsert logic (to match existing rows)
    """
    return _make_row_key(row, dedup_cols)
