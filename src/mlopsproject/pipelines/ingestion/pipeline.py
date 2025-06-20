# src/mlopsproject/pipelines/ingestion/pipeline.py

from kedro.pipeline import Pipeline, node
from .nodes import ingest_data

def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=ingest_data,
                inputs="heart_data_raw",
                outputs="heart_data_ingested",
                name="ingest_data_node"
            )
        ]
    )



