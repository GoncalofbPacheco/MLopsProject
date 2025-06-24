# src/mlopsproject/pipelines/ingestion/pipeline.py

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import ingestion_heart

def create_pipeline(**kwargs) -> Pipeline:
    """Kedro pipeline for the ingestion step."""
    return pipeline(
        [
            node(
                func=ingestion_heart,
                inputs=["heart_data_raw", "params:ingestion"],  # adjust names if different
                outputs="heart_data_ingested",
                name="ingestion_heart_node",
            )
        ]
    )



