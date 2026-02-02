import pandas as pd
import streamlit as st
from data_store import get_master_df


def test_overlay_with_same_id_overrides_base(tmp_base_csv, monkeypatch):
    monkeypatch.setattr("data_store.BASE_CSV_PATH", tmp_base_csv)

    # same EPIC ID → override
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

    assert len(df) == 2

    sodium = df[df["EPIC ID"] == "EPIC_001"].iloc[0]
    assert sodium["Variable"] == "Sodium (updated)"


def test_overlay_with_new_id_creates_new_row(tmp_base_csv, monkeypatch):
    monkeypatch.setattr("data_store.BASE_CSV_PATH", tmp_base_csv)

    # new EPIC ID → new variable
    st.session_state["overlay_df"] = pd.DataFrame(
        [
            {
                "Organ System": "Electrolytes",
                "Group": "Blood",
                "Variable": "Sodium (alt)",
                "EPIC ID": "EPIC_ALT_1",
                "PDMS ID": "",
            }
        ]
    )

    df = get_master_df()

    assert len(df) == 3
    assert "EPIC_ALT_1" in set(df["EPIC ID"])
