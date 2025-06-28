import logging
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from typing import Any, Dict, Tuple
from pathlib import Path

from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings

conf_path = str(Path("") / settings.CONF_SOURCE)
conf_loader = OmegaConfigLoader(conf_source=conf_path)
credentials = conf_loader["credentials"]


logger = logging.getLogger(__name__)





def feature_engineer(data: pd.DataFrame, encoder: OneHotEncoder):
    """
    Aplica a feature engineering no dataset dado, usando um OneHotEncoder pré-treinado.
    - Binning da idade em intervalos
    - Cálculo do z-score para features numéricas
    - Encoding das variáveis categóricas usando o encoder fornecido (somente transform)

    Args:
        data: DataFrame com os dados a transformar.
        encoder: OneHotEncoder já treinado (fit).

    Returns:
        - df_final: DataFrame processado pronto para modelo.
    """
    logger = logging.getLogger(__name__)
    df = data.copy()

    # Binning da idade
    bins = [0, 30, 50, 70, 90]
    labels = ["0-30", "31-50", "51-70", "71-90"]
    df["age_group"] = pd.cut(
        df["age"], bins=bins, labels=labels, right=True, include_lowest=True
    )

    # Calcular z-score para features numéricas
    numeric_cols = ["oldpeak", "cholesterol", "resting_bp_s", "max_heart_rate"]
    for col in numeric_cols:
        df[f"{col}_zscore"] = (df[col] - df[col].mean()) / df[col].std()

    # Garantir que as colunas categóricas estejam em string
    categorical_cols = [
        "sex",
        "chest_pain_type",
        "fasting_blood_sugar",
        "resting_ecg",
        "exercise_angina",
        "st_slope",
        "age_group",
    ]
    df[categorical_cols] = df[categorical_cols].astype(str)

    # Aplicar transformação usando o encoder pré-treinado
    encoded_cat = pd.DataFrame(
        encoder.transform(df[categorical_cols]), index=df.index
    )
    encoded_cat.columns = encoder.get_feature_names_out(categorical_cols)

    # Remover colunas categóricas originais e concatenar as codificadas
    df = df.drop(columns=categorical_cols)
    df_final = pd.concat([df, encoded_cat], axis=1)

    logger.info(f"Feature engineering applied to new data. Result has {len(df_final.columns)} columns.")

    return df_final
