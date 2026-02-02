import pandas as pd
import streamlit as st
from data_store import get_master_df, load_base_df


def test_overlay_without_row_key_creates_new_row(tmp_base_csv, monkeypatch):
    monkeypatch.setattr("data_store.BASE_CSV_PATH", tmp_base_csv)

    # Same EPIC ID, but NO row_key → treated as new variable
    st.session_state["overlay_df"] = pd.DataFrame(
        [
            {
                "Organ System": "Electrolytes",
                "Group": "Blood",
                "Variable": "Sodium (updated)",
                "EPIC ID": "EPIC_001",
                "PDMS ID": "",
            }
        ]
    )

    df = get_master_df()

    # base Sodium + Potassium + new Sodium
    assert len(df) == 3


def test_overlay_with_matching_row_key_overrides_base(tmp_base_csv, monkeypatch):
    monkeypatch.setattr("data_store.BASE_CSV_PATH", tmp_base_csv)

    base_df = load_base_df()
    sodium_row = base_df[base_df["EPIC ID"] == "EPIC_001"].iloc[0]

    # Explicit override using SAME row_key
    st.session_state["overlay_df"] = pd.DataFrame(
        [
            {
                "Organ System": "Electrolytes",
                "Group": "Blood",
                "Variable": "Sodium (updated)",
                "EPIC ID": "EPIC_001",
                "PDMS ID": "",
                "__row_key__": sodium_row["__row_key__"],
            }
        ]
    )

    df = get_master_df()

    assert len(df) == 2

    sodium = df[df["EPIC ID"] == "EPIC_001"].iloc[0]
    assert sodium["Variable"] == "Sodium (updated)"
