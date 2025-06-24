"""
This is the split_data pipeline
adapted for the heart project.
"""

import logging
import pandas as pd

#logger = logging.getLogger(__name__)


def split_heart_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits the heart dataset into training and testing sets using random sampling.

    Args:
        df: Raw heart dataset.

    Returns:
        A tuple containing:
            - heart_train: 80% of the data for training.
            - heart_test: 20% of the data for testing.
    """
    heart_train = df.sample(frac=0.8, random_state=42)
    heart_test = df.drop(heart_train.index)

    #logger.info(f"Split completed — Train shape: {heart_train.shape}, Test shape: {heart_test.shape}")

    return heart_train, heart_test
