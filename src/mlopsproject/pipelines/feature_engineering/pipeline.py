from kedro.pipeline import node, pipeline
from .nodes import feature_engineering

def create_pipeline(**kwargs):
    return pipeline(
        [
            node(
                func=feature_engineering,
                inputs=dict(
                    df="heart_raw",
                    age_bins="params:feature_engineering.age_bins",
                    oldpeak_threshold="params:feature_engineering.oldpeak_threshold",
                    save_preprocessor_path="params:feature_engineering.save_preprocessor_path",
                ),
                outputs=["heart_fe", "fe_preprocessor"],
                name="feature_engineering",
            )
        ]
    )

