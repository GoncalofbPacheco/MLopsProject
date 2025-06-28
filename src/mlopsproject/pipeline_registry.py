"""Project pipelines."""

from typing import Dict
from kedro.pipeline import Pipeline, pipeline

from mlopsproject.pipelines import (
    ingestion as data_ingestion,
    data_unit_tests as data_tests,
    preprocessing_train as preprocess_train,
    split_train as split_train,
    model_selection as model_selection,
    model_train as model_train,
    feature_selection as feature_selection,
    split_data,
    preprocessing_batch,
    model_predict,
    data_drift,
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
    model_train_pipeline = model_train.create_pipeline()
    model_selection_pipeline = model_selection.create_pipeline()
    feature_selection_pipeline = feature_selection.create_pipeline()
    preprocess_batch_pipeline = preprocessing_batch.create_pipeline()
    model_predict_pipeline = model_predict.create_pipeline()
    data_drift_pipeline = data_drift.create_pipeline()

    return {
        "ingestion": ingestion_pipeline,
        "data_unit_tests": data_unit_tests_pipeline,
        "split_data": split_data_pipeline,
        "preprocess_train": preprocess_train_pipeline,
        "split_train": split_train_pipeline,
        "model_selection": model_selection_pipeline,
        "model_train": model_train_pipeline,
        "feature_selection": feature_selection_pipeline,
        "production_full_train_process": preprocess_train_pipeline
        + split_train_pipeline
        + model_train_pipeline,
        "preprocess_batch": preprocess_batch_pipeline,
        "inference": model_predict_pipeline,
        "production_full_prediction_process": preprocess_batch_pipeline
        + model_predict_pipeline,
        "data_drift": data_drift_pipeline,
    }
