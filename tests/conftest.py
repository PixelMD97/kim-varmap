# tests/conftest.py
import pandas as pd
import pytest
from pathlib import Path

@pytest.fixture
def base_df():
    return pd.DataFrame(
        [
            {
                "organ_system": "Electrolytes",
                "group": "Blood",
                "variable": "Sodium",
                "epic_id": "EPIC_001",
                "is_visible": True,
            },
            {
                "organ_system": "Electrolytes",
                "group": "Blood",
                "variable": "Potassium",
                "epic_id": "EPIC_002",
                "is_visible": True,
            },
        ]
    )


@pytest.fixture
def overlay_df_1():
    # Overrides Sodium epic_id
    return pd.DataFrame(
        [
            {
                "organ_system": "Electrolytes",
                "group": "Blood",
                "variable": "Sodium",
                "epic_id": "EPIC_OVERRIDE_1",
            }
        ]
    )


@pytest.fixture
def overlay_df_2():
    # Second overlay overrides again
    return pd.DataFrame(
        [
            {
                "organ_system": "Electrolytes",
                "group": "Blood",
                "variable": "Sodium",
                "epic_id": "EPIC_OVERRIDE_2",
            }
        ]
    )


@pytest.fixture
def tmp_base_csv(tmp_path, base_df):
    path = tmp_path / "base.csv"
    base_df.to_csv(path, index=False)
    return path
