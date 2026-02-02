import streamlit as st
from data_store import get_master_df

def test_overlay_overrides_base(tmp_base_csv, overlay_df_1, monkeypatch):
    monkeypatch.setattr("data_store.BASE_CSV_PATH", tmp_base_csv)

    # inject overlay via session state
    st.session_state["overlay_df"] = overlay_df_1

    df = get_master_df()

    sodium = df[df["Variable"] == "Sodium"].iloc[0]
    assert sodium["EPIC ID"] == "EPIC_OVERRIDE_1"


def test_multiple_overlays_last_write_wins(
    tmp_base_csv, overlay_df_1, overlay_df_2, monkeypatch
):
    monkeypatch.setattr("data_store.BASE_CSV_PATH", tmp_base_csv)

    # simulate sequential uploads
    st.session_state["overlay_df"] = overlay_df_1
    st.session_state["overlay_df"] = overlay_df_2

    df = get_master_df()

    sodium = df[df["Variable"] == "Sodium"].iloc[0]
    assert sodium["EPIC ID"] == "EPIC_OVERRIDE_2"
