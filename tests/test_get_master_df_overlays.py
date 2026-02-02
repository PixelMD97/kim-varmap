# tests/test_get_master_df_overlays.py
from data_store import get_master_df

def test_overlay_overrides_base(tmp_base_csv, overlay_df_1, monkeypatch):
    monkeypatch.setattr("data_store.BASE_CSV_PATH", tmp_base_csv)

    df = get_master_df(overlays=[overlay_df_1])

    sodium = df[df["variable"] == "Sodium"].iloc[0]
    assert sodium["epic_id"] == "EPIC_OVERRIDE_1"


def test_multiple_overlays_last_write_wins(
    tmp_base_csv, overlay_df_1, overlay_df_2, monkeypatch
):
    monkeypatch.setattr("data_store.BASE_CSV_PATH", tmp_base_csv)

    df = get_master_df(overlays=[overlay_df_1, overlay_df_2])

    sodium = df[df["variable"] == "Sodium"].iloc[0]
    assert sodium["epic_id"] == "EPIC_OVERRIDE_2"
