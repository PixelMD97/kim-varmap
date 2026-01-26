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

    # columns that define a row (exclude internal __ cols)
    dedup_cols = [c for c in df.columns if not str(c).startswith("__")]

    # drop ONLY exact duplicates
    df = df.drop_duplicates(subset=dedup_cols)

    # assign stable row keys
    row_keys = []
    for _, row in df.iterrows():
        rk = _make_row_key(row.to_dict(), dedup_cols)
        row_keys.append(rk)

    df["__row_key__"] = row_keys

    nodes = []
    leaf_lookup = {}

    df_sorted = df.sort_values(["Organ System", "Group", "Variable"])

    for os_name, os_df in df_sorted.groupby("Organ System"):
        os_node = {
            "label": os_name,
            "value": os_name,
            "children": [],
        }

        for group_name, group_df in os_df.groupby("Group"):
            group_node = {
                "label": group_name,
                "value": f"{os_name}/{group_name}",
                "children": [],
            }

            for _, row in group_df.iterrows():
                var = row["Variable"]
                row_key = row["__row_key__"]

                # build human-readable label
                label_parts = [var]
                source = row.get("Source")
                if source:
                    label_parts.append(f"({source})")

                label = " ".join(label_parts)

                leaf_value = f"{os_name}/{group_name}/{var}|{row_key}"

                leaf = {
                    "label": label,
                    "value": leaf_value,
                }

                group_node["children"].append(leaf)
                leaf_lookup[leaf_value] = row.to_dict()

            os_node["children"].append(group_node)

        nodes.append(os_node)

    return nodes, leaf_lookup
