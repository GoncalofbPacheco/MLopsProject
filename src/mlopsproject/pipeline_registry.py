"""Project pipelines."""

from typing import Dict
from kedro.pipeline import Pipeline

from mlopsproject.pipelines import (
    ingestion as data_ingestion,
    data_unit_tests as data_tests,
    split_data as split_data,
    preprocessing_train as preprocess_train,
    split_train as split_train,
    model_train as model_train_pipeline,
    model_selection as model_selection_pipeline,
    feature_selection as feature_selection_pipeline,
    preprocessing_batch as preprocessing_batch,
    model_predict as model_predict,
    data_drift as data_drift,
)


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    ingestion_pipeline = data_ingestion.create_pipeline()
    data_unit_tests_pipeline = data_tests.create_pipeline()
    split_data_pipeline = split_data.create_pipeline()
    preprocess_train_pipeline = preprocess_train.create_pipeline()
    split_train_pipeline = split_train.create_pipeline()
    model_train = model_train_pipeline.create_pipeline()
    model_selection = model_selection_pipeline.create_pipeline()
    feature_selection = feature_selection_pipeline.create_pipeline()
    preprocess_batch_pipeline = preprocessing_batch.create_pipeline()
    model_predict_pipeline = model_predict.create_pipeline()
    data_drift = data_drift.create_pipeline()

    return {
        "ingestion": ingestion_pipeline,
        "data_unit_tests": data_unit_tests_pipeline,
        "split_data": split_data_pipeline,
        "preprocess_train": preprocess_train_pipeline,
        "split_train": split_train_pipeline,
        "model_selection": model_selection,
        "model_train": model_train,
        "feature_selection": feature_selection,
        "preprocess_batch": preprocess_batch_pipeline,
        "model_predict": model_predict_pipeline,
        "data_drift": data_drift,
    }
