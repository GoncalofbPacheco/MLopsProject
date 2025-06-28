"""
This is a boilerplate pipeline
generated using Kedro 0.18.8
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import model_predict


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=model_predict,
                inputs=[
                    "heart_train_preprocessed",
                    "production_model",
                    "production_columns",
                ],
                outputs=["model_prediction_results_df", "predict_describe"],
                name="predict",
            ),
        ]
    )
