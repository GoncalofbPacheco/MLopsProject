
import pandas as pd
import mlflow

def ingest_data(heart_data_raw: pd.DataFrame) -> pd.DataFrame:
    with mlflow.start_run(run_name="ingestion", nested=True):
        df = heart_data_raw

        # Log initial shape
        mlflow.log_metric("initial_rows", df.shape[0])

        # 1. Remove duplicates
        df = df.drop_duplicates()

        # 2. Remove invalid 'resting bp s' = 0
        df = df[df["resting bp s"] != 0]

        # 3. Remove invalid 'cholesterol' = 0
        df = df[df["cholesterol"] != 0]

        # 4. Remove outliers in 'max heart rate'
        df = df[(df["max heart rate"] >= 72) & (df["max heart rate"] <= 202)]

        # 5. Bin 'age'
        df["age"] = pd.cut(
            df["age"],
            bins=[0, 40, 50, 60, 70, 80, 90],
            labels=["0-40", "41-50", "51-60", "61-70", "71-80", "81-90"]
        )

        # 6. Bin 'cholesterol'
        df["cholesterol"] = pd.cut(
            df["cholesterol"],
            bins=[0, 200, 240, 1000],
            labels=["normal", "borderline high", "high"]
        )

        # Log final shape
        mlflow.log_metric("final_rows", df.shape[0])
        mlflow.log_param("source", "heart_statlog_cleveland_hungary_final.csv")

        return df
