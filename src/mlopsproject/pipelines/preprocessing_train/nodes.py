import logging
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from typing import Any, Dict, Tuple
from pathlib import Path

from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings

conf_path = str(Path('') / settings.CONF_SOURCE)
conf_loader = OmegaConfigLoader(conf_source=conf_path)
credentials = conf_loader["credentials"]


logger = logging.getLogger(__name__)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean data according to Great Expectations rules."""
    logger = logging.getLogger(__name__)

    df_clean = df.copy()

    before_rows = df_clean.shape[0]

    df_clean = df_clean[
        (df_clean["age"] >= 0) & (df_clean["age"] <= 90) &
        (df_clean["resting_bp_s"] >= 60) & (df_clean["resting_bp_s"] <= 200) &
        (df_clean["cholesterol"] >= 100) & (df_clean["cholesterol"] <= 500) &
        (df_clean["max_heart_rate"] >= 60) & (df_clean["max_heart_rate"] <= 220)
    ]

    after_rows = df_clean.shape[0]
    logger.info(f"Cleaned data: removed {before_rows - after_rows} rows due to outliers.")

    df_clean.reset_index(drop=True, inplace=True)
    # Summary statistics dictionary for reporting
    reporting_data = df.describe().to_dict()
    
    return df_clean, reporting_data


def feature_engineer(data: pd.DataFrame):
    """
    Perform feature engineering on the heart_train dataset.
    - Binning age into intervals
    - Z-score standardization of numeric features: oldpeak, cholesterol, resting_bp_s, max_heart_rate
    - Encoding categorical variables with OneHotEncoder
    
    Returns:
        - df_final: processed dataframe ready for modeling
        - encoder: fitted OneHotEncoder object (useful for inference)
    """
    logger = logging.getLogger(__name__)
    df = data.copy()

    # Bin age into intervals: 0-30, 31-50, 51-70, 71-90
    bins = [0, 30, 50, 70, 90]
    labels = ["0-30", "31-50", "51-70", "71-90"]
    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels, right=True, include_lowest=True)

    # Calculate z-score for numeric features
    numeric_cols = ["oldpeak", "cholesterol", "resting_bp_s", "max_heart_rate"]
    for col in numeric_cols:
        df[f"{col}_zscore"] = (df[col] - df[col].mean()) / df[col].std()

    # Ensure categorical columns are string type for encoding
    categorical_cols = ["sex", "chest_pain_type", "fasting_blood_sugar", "resting_ecg", "exercise_angina", "st_slope", "age_group"]
    df[categorical_cols] = df[categorical_cols].astype(str)

    # OneHotEncode categorical columns
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    encoded_cat = pd.DataFrame(encoder.fit_transform(df[categorical_cols]), index=df.index)
    encoded_cat.columns = encoder.get_feature_names_out(categorical_cols)

    # Drop original categorical columns and concatenate encoded columns
    df = df.drop(columns=categorical_cols)
    df_final = pd.concat([df, encoded_cat], axis=1)

    log = logging.getLogger(__name__)
    log.info(f"The final dataframe has {len(df_final.columns)} columns.")

    return df_final, encoder
