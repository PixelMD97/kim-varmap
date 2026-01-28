import hashlib
import json


def _make_row_key(row: dict, cols: list[str]) -> str:
    """
    Create a stable short hash from relevant row content.
    """
    payload = {c: row.get(c) for c in cols}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:10]


def build_nodes_and_lookup(df):
    df = df.copy()

    # fill hierarchy columns
    for col in ["Organ System", "Group", "Variable"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str)

    if "__row_key__" not in df.columns:
        raise ValueError("Expected '__row_key__' in dataframe. Use data_store.get_master_df().")

    # ensure unique rows by row key (overlay may contain duplicates pre-merge)
    df = df.drop_duplicates(subset=["__row_key__"], keep="last")

    nodes = []
    leaf_lookup = {}

    df_sorted = df.sort_values(["Organ System", "Group", "Variable"])

    for os_name, os_df in df_sorted.groupby("Organ System"):
        os_node = {
            "label": os_name,
            "value": f"OS:{os_name}",
            "children": [],
        }

        for group_name, group_df in os_df.groupby("Group"):
            group_node = {
                "label": group_name,
                "value": f"GR:{os_name}/{group_name}",
                "children": [],
            }

            for _, row in group_df.iterrows():
                var = row["Variable"]
                row_key = str(row["__row_key__"])

                # label
                label_parts = [var]
                source = row.get("Source")
                if source:
                    label_parts.append(f"({source})")
                label = " ".join(label_parts)

                # IMPORTANT: leaf value must be stable and independent of columns
                leaf_value = f"ROW:{row_key}"

                leaf = {"label": label, "value": leaf_value}
                group_node["children"].append(leaf)
                leaf_lookup[leaf_value] = row.to_dict()

            os_node["children"].append(group_node)

        nodes.append(os_node)

    return nodes, leaf_lookup


def compute_row_key_from_df_row(row: dict, dedup_cols: list[str]) -> str:
    """
    Compute the same stable __row_key__ that build_nodes_and_lookup uses,
    based on the same dedup_cols definition.
    """
    return _make_row_key(row, dedup_cols)
