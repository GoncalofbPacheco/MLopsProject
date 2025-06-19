"""
This is a boilerplate pipeline 'feature_engineering'
generated using Kedro 0.19.12
"""
import pandas as pd

def add_age_bucket(data: pd.DataFrame, bins: list[int]) -> pd.DataFrame:
    data = data.copy()
    data["age_bucket"] = pd.cut(data["age"], bins=bins, right=False)
    return data


