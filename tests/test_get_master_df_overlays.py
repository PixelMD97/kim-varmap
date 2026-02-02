import streamlit as st
from data_store import get_master_df


def test_overlay_with_same_epic_id_overrides_base(tmp_base_csv, monkeypatch):
    monkeypatch.setattr("data_store.BASE_CSV_PATH", tmp_base_csv)

    # Overlay keeps SAME EPIC ID, but changes metadata
    overlay_df = st.session_state["overlay_df"] = (
        __import__("pandas").DataFrame(
            [
                {
                    "Organ System": "Electrolytes",
                    "Group": "Blood",
                    "Variable": "Sodium (updated)",
                    "EPIC ID": "EPIC_001",   # SAME ID → override
                    "PDMS ID": "",
                }
            ]
        )
    )

    df = get_master_df()

    # still only two variables
    assert len(df) == 2

    sodium = df[df["EPIC ID"] == "EPIC_001"].iloc[0]
    assert sodium["Variable"] == "Sodium (updated)"


def test_overlay_with_new_epic_id_creates_new_variable(tmp_base_csv, monkeypatch):
    monkeypatch.setattr("data_store.BASE_CSV_PATH", tmp_base_csv)

    # Overlay introduces NEW EPIC ID
    st.session_state["overlay_df"] = (
        __import__("pandas").DataFrame(
            [
                {
                    "Organ System": "Electrolytes",
                    "Group": "Blood",
                    "Variable": "Sodium (alt)",
                    "EPIC ID": "EPIC_OVERRIDE_1",
                    "PDMS ID": "",
                }
            ]
        )
    )

    df = get_master_df()

    # base Sodium + Potassium + new Sodium
    assert len(df) == 3

    assert set(df["EPIC ID"]) == {
        "EPIC_001",
        "EPIC_002",
        "EPIC_OVERRIDE_1",
    }
