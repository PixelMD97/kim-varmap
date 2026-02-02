from data_store import get_master_df

def test_base_csv_only(tmp_base_csv, monkeypatch):
    # point data_store to temp CSV
    monkeypatch.setattr("data_store.BASE_CSV_PATH", tmp_base_csv)

    df = get_master_df()

    # correct number of rows
    assert len(df) == 2

    # canonical column names
    assert set(df["Variable"]) == {"Sodium", "Potassium"}

    # stable identity exists
    assert "__row_key__" in df.columns
    assert df["__row_key__"].nunique() == 2
