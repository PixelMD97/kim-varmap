from data_store import load_base_df

def test_row_key_is_stable_across_calls():
    df1 = load_base_df()
    df2 = load_base_df()

    assert "__row_key__" in df1.columns
    assert "__row_key__" in df2.columns

    # identical keys across calls
    assert df1["__row_key__"].tolist() == df2["__row_key__"].tolist()
