from data_store import load_base_df


def test_row_keys_are_stable_across_calls():
    df1 = load_base_df()
    df2 = load_base_df()

    assert df1["__row_key__"].tolist() == df2["__row_key__"].tolist()
