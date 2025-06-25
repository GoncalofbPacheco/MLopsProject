# src/mlopsproject/pipelines/preprocess_train/pipeline.py

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import clean_data, feature_engineer

def create_pipeline(**kwargs) -> Pipeline:
    """Kedro pipeline for preprocessing train data."""

    return pipeline(
        [
            node(
                func=clean_data,
                inputs="heart_train",  # Your dataset from catalog
                outputs=["heart_train_cleaned","reporting_data_train"],  # cleaned data output
                name="clean_data_node",
            ),
            node(
                func=feature_engineer,
                inputs="heart_train_cleaned",
                outputs=["heart_train_preprocessed", "encoder"],  # processed data + encoder
                name="feature_engineering_node",
            ),
        ]
    )
