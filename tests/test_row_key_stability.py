# tests/test_row_key_stability.py
from tree_utils import compute_row_key_from_df_row
import pandas as pd

def test_row_key_is_stable_across_calls():
    row = pd.Series(
        {
            "organ_system": "Electrolytes",
            "group": "Blood",
            "variable": "Sodium",
        }
    )

    key1 = compute_row_key_from_df_row(row)
    key2 = compute_row_key_from_df_row(row)

    assert key1 == key2
