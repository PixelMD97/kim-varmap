# tests/conftest.py
import sys
from pathlib import Path
import pandas as pd
import pytest

# -------------------------------------------------
# Make project root importable (fixes CI imports)
# -------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


# -------------------------------------------------
# Fixtures matching CURRENT data model
# -------------------------------------------------
@pytest.fixture
def base_df():
    return pd.DataFrame(
        [
            {
                "Organ System": "Electrolytes",
                "Group": "Blood",
                "Variable": "Sodium",
                "EPIC ID": "EPIC_001",
                "PDMS ID": "",
            },
            {
                "Organ System": "Electrolytes",
                "Group": "Blood",
                "Variable": "Potassium",
                "EPIC ID": "EPIC_002",
                "PDMS ID": "",
            },
        ]
    )


@pytest.fixture
def overlay_df_1():
    # Overrides Sodium EPIC ID
    return pd.DataFrame(
        [
            {
                "Organ System": "Electrolytes",
                "Group": "Blood",
                "Variable": "Sodium",
                "EPIC ID": "EPIC_OVERRIDE_1",
                "PDMS ID": "",
            }
        ]
    )


@pytest.fixture
def overlay_df_2():
    # Second overlay overrides again
    return pd.DataFrame(
        [
            {
                "Organ System": "Electrolytes",
                "Group": "Blood",
                "Variable": "Sodium",
                "EPIC ID": "EPIC_OVERRIDE_2",
                "PDMS ID": "",
            }
        ]
    )


@pytest.fixture
def tmp_base_csv(tmp_path, base_df):
    path = tmp_path / "base.csv"
    base_df.to_csv(path, index=False)
    return path
