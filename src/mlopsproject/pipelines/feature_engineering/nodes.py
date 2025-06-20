import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# --------------------------------------------------------------------------- #
# Feature engineering – heart-disease dataset                                 #
# --------------------------------------------------------------------------- #
def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Add domain-driven features & interactions, then return a model-ready
    table (numeric/one-hot, scaled). The target column is preserved at the end.
    """
    df = df.copy()              # keep original intact
    y = df.pop("target")        # stash the label early

    # ------------------------------------------------------------------ #
    # 1.  New scalar & categorical features                               #
    # ------------------------------------------------------------------ #
    df["age_bucket"] = pd.cut(
        df["age"],
        bins=[0, 40, 50, 60, 150],
        labels=["<40", "40-49", "50-59", "≥60"],
        right=False,
    ).astype("category")

    df["max_hr_deficit"] = 220 - df["age"] - df["max_heart_rate"]
    df["oldpeak_flag"]   = (df["oldpeak"] >= 2.0).astype("int8")
    df["chol_to_age"]    = df["cholesterol"] / df["age"]
    df["bp_pulse_pressure"] = df["resting_bp_s"] - (df["resting_bp_s"] / 1.6)

    # ------------------------------------------------------------------ #
    # 2.  Interaction terms                                               #
    # ------------------------------------------------------------------ #
    df["sex_x_cp"] = (
        df["sex"].astype(str) + "_" + df["chest_pain_type"].astype(str)
    ).astype("category")

    df["exang_x_slope"] = (
        df["exercise_angina"].astype(str) + "_" + df["ST_slope"].astype(str)
    ).astype("category")

    df["oldpeak_x_slope"] = df["oldpeak"] * df["ST_slope"]
    df["fbs_x_agebucket"] = (
        df["fasting_blood_sugar"].astype(str) + "_" + df["age_bucket"].astype(str)
    ).astype("category")

    # ------------------------------------------------------------------ #
    # 3.  Encode / scale                                                 #
    # ------------------------------------------------------------------ #
    X = df  # everything left is a feature
    num_cols = X.select_dtypes("number").columns.tolist()
    cat_cols = X.select_dtypes(exclude="number").columns.tolist()

    pre = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
        ],
        remainder="drop",
    )

    X_pre = pre.fit_transform(X)
    X_pre = pd.DataFrame(
        X_pre,
        columns=pre.get_feature_names_out(),
        index=X.index,
    )
    X_pre["target"] = y.values
    return X_pre
