import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import logging


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()

    # Standardizing string columns
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    
    # Replace string values with lowercase
    if df["cholesterol"].dtype == object:
        df["cholesterol"] = df["cholesterol"].str.lower()
    
    df["cholesterol"] = df["cholesterol"].replace({"high": 1, "normal": 0})
    df.fillna(-9999, inplace=True)

    return df


def feature_engineer(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()

    # Age binning
    df["age"] = df["age"].astype(str).str.extract(r"(\d+)", expand=False).astype(float)
    df["age_group"] = pd.cut(df["age"], bins=[0, 40, 60, 120], labels=["young", "middle", "old"])

    # Z-score of oldpeak
    df["oldpeak_zscore"] = (df["oldpeak"] - df["oldpeak"].mean()) / df["oldpeak"].std()

    # OneHot Encode categorical
    categorical_cols = ["sex", "chest_pain_type", "resting_ecg", "exercise_angina", "st_slope", "age_group"]
    df[categorical_cols] = df[categorical_cols].astype(str)

    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    encoded = pd.DataFrame(encoder.fit_transform(df[categorical_cols]), index=df.index)
    encoded.columns = encoder.get_feature_names_out(categorical_cols)

    # Drop old categorical columns and concatenate
    df.drop(columns=categorical_cols, inplace=True)
    df = pd.concat([df, encoded], axis=1)

    # Separate target
    if "target" in df.columns:
        target = df.pop("target")
        df["target"] = target

    logging.getLogger(__name__).info(f"Final engineered shape: {df.shape}")

    return df
