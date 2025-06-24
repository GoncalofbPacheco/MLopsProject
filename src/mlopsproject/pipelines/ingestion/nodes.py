
"""
Boilerplate pipeline – Kedro 0.18.8
Adapted for the Heart project
"""
import logging
from typing import Any, Dict, List

import pandas as pd
from great_expectations.core import ExpectationSuite, ExpectationConfiguration
import hopsworks
from pathlib import Path
from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings

logger = logging.getLogger(__name__)

# ───────────────────────────────────────────
# Credentials (Kedro conf/credentials.yml)
# ───────────────────────────────────────────
conf_path = str(Path("") / settings.CONF_SOURCE)
conf_loader = OmegaConfigLoader(conf_source=conf_path)
credentials = conf_loader["credentials"]  # e.g. credentials["feature_store"]

# ───────────────────────────────────────────
# Build GE expectation-suite helpers
# ───────────────────────────────────────────
def build_expectation_suite(
    expectation_suite_name: str,
    feature_group: str
) -> ExpectationSuite:
    """
    Create a Great-Expectations suite tailored to a feature group.
    """
    suite = ExpectationSuite(expectation_suite_name=expectation_suite_name)

    if feature_group == "numerical_features":
        for col in ["age", "resting_bp_s", "cholesterol", "max_heart_rate", "oldpeak"]:
            suite.add_expectation(
                ExpectationConfiguration(
                    expectation_type="expect_column_values_to_be_of_type",
                    kwargs={"column": col, "type_": "float64"},
                )
            )

        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_min_to_be_between",
                kwargs={"column": "age", "min_value": 0, "max_value": 90},
            )
        )

        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={"column": "resting_bp_s", "min_value": 60, "max_value": 200},
            )
        )

        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={"column": "cholesterol", "min_value": 100, "max_value": 500},
            )
        )

        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={"column": "max_heart_rate", "min_value": 60, "max_value": 220},
            )
        )

    if feature_group == "categorical_features":
        allowed_values: Dict[str, List[int]] = {
            "sex": [0, 1],
            "chest_pain_type": [1, 2, 3, 4],
            "fasting_blood_sugar": [0, 1],
            "resting_ecg": [0, 1, 2],
            "exercise_angina": [0, 1],
            "st_slope": [0, 1, 2, 3],
        }
        for col, allowed in allowed_values.items():
            suite.add_expectation(
                ExpectationConfiguration(
                    expectation_type="expect_column_distinct_values_to_be_in_set",
                    kwargs={"column": col, "value_set": allowed},
                )
            )

    if feature_group == "target":
        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_distinct_values_to_be_in_set",
                kwargs={"column": "target", "value_set": [0, 1]},
            )
        )

    return suite

# ───────────────────────────────────────────
# Helper to push data to Hopsworks Feature-Store
# ───────────────────────────────────────────
def to_feature_store(
    data: pd.DataFrame,
    group_name: str,
    feature_group_version: int,
    description: str,
    group_description: list,
    validation_expectation_suite: ExpectationSuite,
    credentials_input: dict,
):
    """Upload a DataFrame to Hopsworks with validation attached."""
    project = hopsworks.login(
        api_key_value=credentials_input["FS_API_KEY"],
        project=credentials_input["FS_PROJECT_NAME"],
    )
    feature_store = project.get_feature_store()

    feature_group = feature_store.get_or_create_feature_group(
        name=group_name,
        version=feature_group_version,
        description=description,
        primary_key=["index"],
        event_time="datetime",
        online_enabled=False,
        expectation_suite=validation_expectation_suite,
    )
    assert isinstance(data, pd.DataFrame), f"Data is not a DataFrame: {type(data)}"
    print("Sending columns to Hopsworks:", data.columns.tolist())

    feature_group.insert(
        features=data,
        overwrite=False,
        write_options={"wait_for_job": True},
    )

    for desc in group_description:
        feature_group.update_feature_description(desc["name"], desc["description"])

    feature_group.statistics_config = {"enabled": True, "histograms": True, "correlations": True}
    feature_group.update_statistics_config()
    feature_group.compute_statistics()

    return feature_group

# ───────────────────────────────────────────
# Main Kedro node - ingestion for heart data
# ───────────────────────────────────────────
def ingestion_heart(
    heart_data: pd.DataFrame,
    parameters: Dict[str, Any],
) -> pd.DataFrame:
    """
    • Drops duplicates
    • Cleans column names
    • Adds a datetime column (June 2024, day 1)
    • Splits numeric / categorical / target features explicitly
    • Optionally pushes each split to the Hopsworks Feature-Store
    • Returns the full cleaned DataFrame
    """


    # 1 – clean & timestamp
    df = heart_data.copy().drop_duplicates().reset_index()
    df["datetime"] = pd.to_datetime("2024-06-01")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    print("Colunas no DataFrame após limpeza:")
    print(df.columns.tolist())

    logger.info("Loaded heart dataset - shape %s", df.shape)

    # 2 – explicit feature splits
    numerical_features = ["age", "resting_bp_s", "cholesterol", "max_heart_rate", "oldpeak"]
    categorical_features = ["sex", "chest_pain_type", "fasting_blood_sugar", "resting_ecg", "exercise_angina", "st_slope"]
    target_column = "target"

    used_cols = ["index", "datetime"]
    df_numeric = df[used_cols + numerical_features]
    df_categorical = df[used_cols + categorical_features]
    df_target = df[used_cols + [target_column]]

    # 3 – GE suites
    suite_numeric     = build_expectation_suite("heart_numeric_suite", "numerical_features")
    suite_categorical = build_expectation_suite("heart_categorical_suite", "categorical_features")
    suite_target      = build_expectation_suite("heart_target_suite", "target")

    # 4 – optional upload
    if parameters.get("to_feature_store", False):
        fs_creds = credentials["feature_store"]
        to_feature_store(df_numeric,     "heart_numeric",     1, "Heart Numeric Features",     [], suite_numeric,     fs_creds)
        to_feature_store(df_categorical, "heart_categorical", 1, "Heart Categorical Features", [], suite_categorical, fs_creds)
        to_feature_store(df_target,      "heart_target",      1, "Heart Target Features",      [], suite_target,      fs_creds)

    # 5 – return for downstream nodes
    return df

