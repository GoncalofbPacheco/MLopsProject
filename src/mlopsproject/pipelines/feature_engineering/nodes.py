import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from joblib import dump

def _make_preprocessor(num_cols: list[str], cat_cols: list[str], *, sparse: bool = True) -> ColumnTransformer:
    """Create a reusable ColumnTransformer for numeric scaling & categorical one‑hot."""
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=sparse),
                cat_cols,
            ),
        ],
        remainder="drop",
    )


# --------------------------------------------------------------------------- #
# Node function                                                               #
# --------------------------------------------------------------------------- #

def feature_engineering(
    df: pd.DataFrame,
    *,
    age_bins: list[int] | None = None,
    oldpeak_threshold: float = 2.0,
    save_preprocessor_path: str | None = None,
) -> tuple[pd.DataFrame, ColumnTransformer]:
    """Add domain‑driven features & interactions, then return a model‑ready
    table (numeric/one‑hot, scaled) **plus** the fitted preprocessor.

    Parameters
    ----------
    df : pd.DataFrame
        Raw input containing the original columns **and** ``target``.
    age_bins : list[int], optional
        Custom bin edges for ``age_bucket``. Defaults to ``[0, 40, 50, 60, 150]``.
    oldpeak_threshold : float, optional
        Threshold that triggers ``oldpeak_flag``. Defaults to ``2.0``.
    save_preprocessor_path : str, optional
        If provided, the fitted ``ColumnTransformer`` is persisted to this path
        with :pyfunc:`joblib.dump` for re‑use at inference time.

    Returns
    -------
    tuple[pd.DataFrame, ColumnTransformer]
        ``features`` and the fitted ``preprocessor``.
    """
    age_bins = age_bins or DEFAULT_AGE_BINS

    df = df.copy()
    y = df.pop("target").astype("int8")

    # ------------------------------------------------------------------ #
    # 1.  Simple domain‑driven features                                   #
    # ------------------------------------------------------------------ #
    df["age_bucket"] = pd.cut(
        df["age"],
        bins=age_bins,
        labels=DEFAULT_AGE_LABELS[: len(age_bins) - 1],
        right=True,  # inclusive upper edge
    ).astype("category")

    df["max_hr_deficit"] = (220 - df["age"] - df["max_heart_rate"]).astype("float32")
    df["oldpeak_flag"] = (df["oldpeak"] >= oldpeak_threshold).astype("int8")
    df["chol_to_age"] = (df["cholesterol"] / df["age"]).astype("float32")

    # Prefer classical pulse pressure if diastolic BP is available
    if "resting_bp_d" in df.columns:
        df["bp_pulse_pressure"] = (
            df["resting_bp_s"] - df["resting_bp_d"]
        ).astype("float32")
    else:
        # Fallback proxy (legacy): systolic minus 1.6‑ratio surrogate
        df["bp_pulse_pressure"] = (
            df["resting_bp_s"] - (df["resting_bp_s"] / 1.6)
        ).astype("float32")

    # ------------------------------------------------------------------ #
    # 2.  Interaction terms                                               #
    # ------------------------------------------------------------------ #
    df["sex_x_cp"] = (
        df["sex"].astype(str) + "_" + df["chest_pain_type"].astype(str)
    ).astype("category")

    df["exang_x_slope"] = (
        df["exercise_angina"].astype(str) + "_" + df["ST_slope"].astype(str)
    ).astype("category")

    df["oldpeak_x_slope"] = (df["oldpeak"] * df["ST_slope"]).astype("float32")
    df["fbs_x_agebucket"] = (
        df["fasting_blood_sugar"].astype(str) + "_" + df["age_bucket"].astype(str)
    ).astype("category")

    # ------------------------------------------------------------------ #
    # 3.  Encode & scale                                                  #
    # ------------------------------------------------------------------ #
    num_cols = df.select_dtypes("number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()

    pre = _make_preprocessor(num_cols, cat_cols, sparse=True)
    X_pre = pre.fit_transform(df)

    # Convert sparse matrix if necessary
    if hasattr(X_pre, "toarray"):
        X_pre = X_pre.toarray()

    X_pre = pd.DataFrame(
        X_pre,
        columns=pre.get_feature_names_out(),
        index=df.index,
    ).astype("float32")

    X_pre["target"] = y.values

    # Optionally persist the fitted transformer
    if save_preprocessor_path:
        dump(pre, save_preprocessor_path)

    return X_pre, pre