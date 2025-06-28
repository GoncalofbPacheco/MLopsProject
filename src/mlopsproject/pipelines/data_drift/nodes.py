"""
This is a boilerplate pipeline
generated using Kedro 0.18.8
"""

import logging
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from great_expectations.core import ExpectationSuite, ExpectationConfiguration
import great_expectations as gx

from pathlib import Path

from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings

import matplotlib.pyplot as plt
import nannyml as nml
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset


logger = logging.getLogger(__name__)


def data_drift(
    data_reference: pd.DataFrame,
    data_analysis: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate data drift between a reference dataset and new dataset.

    Numeric features: age, resting_bp_s, cholesterol, max_heart_rate, oldpeak  
    Categorical features: sex, exercise_angina

    Uses nannyml for univariate drift on categorical features and evidently for numeric features.

    Args:
        data_reference: Reference dataset (training data).  
        data_analysis: New dataset (test or production data).

    Returns:
        A dataframe with nannyml univariate drift results for categorical features.
        Also generates HTML reports in 'data/08_reporting/'.
    """

    # Set threshold for drift detection
    constant_threshold = nml.thresholds.ConstantThreshold(lower=None, upper=0.2)
    constant_threshold.thresholds(data_reference)

    # Categorical columns for nannyml univariate drift calculation
    categorical_cols = ['sex', 'exercise_angina']

    univariate_calculator = nml.UnivariateDriftCalculator(
        column_names=categorical_cols,
        treat_as_categorical=categorical_cols,
        chunk_size=50,
        categorical_methods=['jensen_shannon'],
        thresholds={"jensen_shannon": constant_threshold}
    )

    # Fit on reference data and calculate drift on analysis data
    univariate_calculator.fit(data_reference)
    results = univariate_calculator.calculate(data_analysis).filter(
        period='analysis',
        column_names=categorical_cols,
        methods=['jensen_shannon']
    ).to_df()

    # Save nannyml drift plot as HTML
    figure = univariate_calculator.calculate(data_analysis).filter(
        period='analysis',
        column_names=categorical_cols,
        methods=['jensen_shannon']
    ).plot(kind='drift')
    figure.write_html("data/08_reporting/univariate_nml_categorical.html")

    # Numeric columns for evidently data drift report
    numeric_cols = ['age', 'resting_bp_s', 'cholesterol', 'max_heart_rate', 'oldpeak']

    data_drift_report = Report(metrics=[
        DataDriftPreset(cat_stattest='ks', stattest_threshold=0.05)
    ])

    data_drift_report.run(
        current_data=data_analysis[numeric_cols + categorical_cols],
        reference_data=data_reference[numeric_cols + categorical_cols],
        column_mapping=None
    )

    data_drift_report.save_html("data/08_reporting/data_drift_report.html")

    logger.info("Data drift analysis complete. Reports saved to data/08_reporting/")

    return results
