
import logging
import pandas as pd
from great_expectations.core import ExpectationSuite, ExpectationConfiguration
import great_expectations as gx

logger = logging.getLogger(__name__)

def get_validation_results(checkpoint_result):
    validation_result_key, validation_result_data = next(iter(checkpoint_result["run_results"].items()))
    validation_result_ = validation_result_data.get('validation_result', {})
    results = validation_result_["results"]
    meta = validation_result_["meta"]

    df_validation = pd.DataFrame(columns=[
        "Success", "Expectation Type", "Column", "Column Pair",
        "Max Value", "Min Value", "Element Count", "Unexpected Count",
        "Unexpected Percent", "Value Set", "Unexpected Value", "Observed Value"
    ])

    for result in results:
        success = result.get('success', '')
        expectation_type = result.get('expectation_config', {}).get('expectation_type', '')
        column = result.get('expectation_config', {}).get('kwargs', {}).get('column', '')
        column_A = result.get('expectation_config', {}).get('kwargs', {}).get('column_A', '')
        column_B = result.get('expectation_config', {}).get('kwargs', {}).get('column_B', '')
        value_set = result.get('expectation_config', {}).get('kwargs', {}).get('value_set', '')
        max_value = result.get('expectation_config', {}).get('kwargs', {}).get('max_value', '')
        min_value = result.get('expectation_config', {}).get('kwargs', {}).get('min_value', '')
        element_count = result.get('result', {}).get('element_count', '')
        unexpected_count = result.get('result', {}).get('unexpected_count', '')
        unexpected_percent = result.get('result', {}).get('unexpected_percent', '')
        observed_value = result.get('result', {}).get('observed_value', '')

        if isinstance(observed_value, list):
            unexpected_value = [item for item in observed_value if item not in value_set]
        else:
            unexpected_value = []

        df_validation = pd.concat([
            df_validation,
            pd.DataFrame([{
                "Success": success,
                "Expectation Type": expectation_type,
                "Column": column,
                "Column Pair": (column_A, column_B),
                "Max Value": max_value,
                "Min Value": min_value,
                "Element Count": element_count,
                "Unexpected Count": unexpected_count,
                "Unexpected Percent": unexpected_percent,
                "Value Set": value_set,
                "Unexpected Value": unexpected_value,
                "Observed Value": observed_value
            }])
        ], ignore_index=True)

    return df_validation

def test_heart_data(df: pd.DataFrame) -> pd.DataFrame:
    context = gx.get_context(context_root_dir="../../gx")
    datasource_name = "heart_datasource"

    try:
        datasource = context.sources.add_pandas(datasource_name)
        logger.info("Data Source created.")
    except Exception:
        logger.info("Data Source already exists.")
        datasource = context.datasources[datasource_name]

    suite_heart = context.add_or_update_expectation_suite(expectation_suite_name="Heart")

    # Add expectations aligned with ingestion node
    suite_heart.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_distinct_values_to_be_in_set",
        kwargs={"column": "sex", "value_set": [0, 1]},
    ))

    suite_heart.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "age", "min_value": 0, "max_value": 90},
    ))

    suite_heart.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "cholesterol", "min_value": 100, "max_value": 500},
    ))

    suite_heart.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "resting bp s", "min_value": 60, "max_value": 200},
    ))

    suite_heart.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "max heart rate", "min_value": 60, "max_value": 220},
    ))

    suite_heart.add_expectation(ExpectationConfiguration(
        expectation_type="expect_column_distinct_values_to_be_in_set",
        kwargs={"column": "target", "value_set": [0, 1]},
    ))

    context.add_or_update_expectation_suite(expectation_suite=suite_heart)

    try:
        data_asset = datasource.add_dataframe_asset(name="test", dataframe=df)
    except Exception:
        logger.info("The data asset already exists. It will be loaded.")
        data_asset = datasource.get_asset("test")

    batch_request = data_asset.build_batch_request(dataframe=df)

    checkpoint = gx.checkpoint.SimpleCheckpoint(
        name="checkpoint_heart",
        data_context=context,
        validations=[{
            "batch_request": batch_request,
            "expectation_suite_name": "Heart",
        }],
    )
    checkpoint_result = checkpoint.run()
    df_validation = get_validation_results(checkpoint_result)

    # Safety check with GX's quick API
    pd_df_ge = gx.from_pandas(df)
    assert pd_df_ge.expect_column_values_to_be_of_type("age", "int64").success
    assert pd_df_ge.expect_column_values_to_be_of_type("sex", "int64").success

    logger.info("✅ Heart data passed unit data tests.")
    return df_validation

