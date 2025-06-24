from kedro.pipeline import Pipeline, node, pipeline
from .nodes import clean_data, feature_engineer

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=clean_data,
            inputs="raw_preprocessed_data",
            outputs="cleaned_data",
            name="clean_data_node"
        ),
        node(
            func=feature_engineer,
            inputs="cleaned_data",
            outputs="engineered_data",
            name="feature_engineering_node"
        )
    ])
