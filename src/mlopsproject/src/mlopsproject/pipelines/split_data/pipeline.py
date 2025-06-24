"""
This is a boilerplate pipeline
generated using Kedro 0.18.8
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import split_heart_data

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=split_heart_data,
                inputs="heart_data_ingested",
                outputs=["heart_train", "heart_test"],
                name="split_out_of_sample",
            ),
        ]
    )
