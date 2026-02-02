# tests/test_get_master_df_base.py
from data_store import get_master_df

def test_base_csv_only(tmp_base_csv, monkeypatch):
    monkeypatch.setattr(
        "data_store.BASE_CSV_PATH",
        tmp_base_csv,
    )

    df = get_master_df()

    assert len(df) == 2
    assert set(df["variable"]) == {"Sodium", "Potassium"}
