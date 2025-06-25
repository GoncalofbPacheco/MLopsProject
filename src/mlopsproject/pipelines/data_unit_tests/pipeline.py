# mlopsproject/pipelines/data_unit_tests/pipeline.py

from kedro.pipeline import Pipeline, node
from .nodes import test_heart_data

def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                func=test_heart_data,
                inputs="heart_data_ingested",
                outputs="heart_data_validated",
                name="test_heart_data_node",
            )
        ]
    )
