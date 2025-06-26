"""Project pipelines."""

from typing import Dict
from kedro.pipeline import Pipeline

from mlopsproject.pipelines import (
    ingestion as ingestion_pipeline,
    data_unit_tests as data_unit_tests_pipeline,
    split_data as split_data_pipeline,
    preprocessing_train as preprocess_train_pipeline,
    split_train as split_train_pipeline,
    feature_selection as feature_selection_pipeline,
    model_selection as model_selection_pipeline,
)


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    ingestion = ingestion_pipeline.create_pipeline()
    data_unit_tests = data_unit_tests_pipeline.create_pipeline()
    split_data = split_data_pipeline.create_pipeline()
    preprocess_train = preprocess_train_pipeline.create_pipeline()
    split_train = split_train_pipeline.create_pipeline()
    model_selection = model_selection_pipeline.create_pipeline()
    feature_selection = feature_selection_pipeline.create_pipeline()

    return {
        "ingestion": ingestion,
        "data_unit_tests": data_unit_tests,
        "split_data": split_data,
        "preprocess_train": preprocess_train,
        "split_train": split_train,
        "model_selection": model_selection,
        "feature_selection": feature_selection,
        "production_full_train_process": preprocess_train + split_train,
    }
