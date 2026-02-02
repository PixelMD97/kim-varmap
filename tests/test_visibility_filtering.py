# tests/test_visibility_filtering.py
from data_store import get_master_df

def test_invisible_rows_not_resurrected(tmp_base_csv, monkeypatch):
    monkeypatch.setattr("data_store.BASE_CSV_PATH", tmp_base_csv)

    df = get_master_df()

    # Simulate user hiding Potassium
    df.loc[df["variable"] == "Potassium", "is_visible"] = False

    # Re-run master merge
    df2 = get_master_df(previous_df=df)

    visible_vars = df2[df2["is_visible"]]["variable"].tolist()
    assert "Potassium" not in visible_vars
