"""
This is a boilerplate test file for pipeline 'feature_engineering'
generated using Kedro 0.19.12.
Please add your pipeline tests here.

Kedro recommends using `pytest` framework, more info about it can be found
in the official documentation:
https://docs.pytest.org/en/latest/getting-started.html
"""
import numpy as np
import pandas as pd
from mlopsproject.pipelines.data_engineering.nodes.feature_engineering import (
    feature_engineering,
)

# --------------------------------------------------------------------------- #
# Sample input – two rows so StandardScaler centres at 0 for each num col     #
# --------------------------------------------------------------------------- #
SAMPLE = pd.DataFrame(
    {
        "age": [45, 65],
        "sex": [1, 0],
        "chest_pain_type": [3, 2],
        "resting_bp_s": [120, 140],
        "cholesterol": [230, 260],
        "fasting_blood_sugar": [0, 1],
        "resting_ecg": [1, 0],
        "max_heart_rate": [150, 130],
        "exercise_angina": [0, 1],
        "oldpeak": [1.0, 3.0],
        "ST_slope": [2, 1],
        "target": [0, 1],
    }
)


def test_row_and_target_integrity():
    out = feature_engineering(SAMPLE)
    # row count should remain unchanged
    assert out.shape[0] == SAMPLE.shape[0]
    # target must survive the transformation
    assert "target" in out.columns
    # no NA values allowed in engineered table
    assert out.isna().sum().sum() == 0


def test_expected_derived_columns_present():
    out = feature_engineering(SAMPLE)
    # numerical derivations – StandardScaler prefix "num__"
    assert any(col.startswith("num__max_hr_deficit") for col in out.columns)
    assert any(col.startswith("num__oldpeak_x_slope") for col in out.columns)

    # categorical bucket / interaction encodings – OneHotEncoder prefix "cat__"
    assert any(col.startswith("cat__age_bucket_") for col in out.columns)
    assert any(col.startswith("cat__sex_x_cp_") for col in out.columns)


def test_numeric_features_are_standardised():
    out = feature_engineering(SAMPLE)
    numeric = [c for c in out.columns if c.startswith("num__")]
    # each numeric column mean should be ~ 0 after scaling on this tiny sample
    assert np.allclose(out[numeric].mean().values, 0.0, atol=1e-6)
