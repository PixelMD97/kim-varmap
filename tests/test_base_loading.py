from data_store import get_master_df


def test_base_mapping_loads(tmp_base_csv, monkeypatch):
    monkeypatch.setattr("data_store.BASE_CSV_PATH", tmp_base_csv)

    df = get_master_df()

    # basic sanity
    assert len(df) == 2

    # canonical columns
    for col in ["Variable", "Organ System", "Group", "EPIC ID", "PDMS ID"]:
        assert col in df.columns

    # stable identity
    assert "__row_key__" in df.columns
    assert df["__row_key__"].nunique() == len(df)

    # expected variables
    assert set(df["Variable"]) == {"Sodium", "Potassium"}
