import pandas as pd

def build_nodes_and_lookup(df: pd.DataFrame):
    df = df.copy()
    df[["Organ System", "Group", "Variable"]] = (
        df[["Organ System", "Group", "Variable"]].fillna("Unknown").astype(str)
    )

    nodes = []
    leaf_lookup = {}  # key: "OS/Group/Variable" -> row dict

    df_sorted = df.sort_values(["Organ System", "Group", "Variable"])

    for os_name, os_df in df_sorted.groupby("Organ System"):
        os_node = {"label": os_name, "value": os_name, "children": []}

        for group_name, group_df in os_df.groupby("Group"):
            group_node = {"label": group_name, "value": f"{os_name}/{group_name}", "children": []}

            # keep first row per variable (avoid duplicates)
            group_df_unique = group_df.drop_duplicates(subset=["Variable"])

            for _, row in group_df_unique.iterrows():
                var = row["Variable"]
                leaf_value = f"{os_name}/{group_name}/{var}"

                group_node["children"].append({"label": var, "value": leaf_value})
                leaf_lookup[leaf_value] = row.to_dict()

            os_node["children"].append(group_node)

        nodes.append(os_node)

    return nodes, leaf_lookup
