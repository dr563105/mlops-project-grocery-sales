import mlflow
import pandas as pd
import os

RUN_ID = os.getenv("RUN_ID")  # "5651db4644334361b10296c51ba3af3e"  
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME") #"mlops-project-sales-forecast-bucket"
EXPERIMENT_ID = 1
FILE_ADDRESS = "artifacts/predictions/lgb_preds.parquet"
pred_s3_location = f"s3://{S3_BUCKET_NAME}/{EXPERIMENT_ID}/{RUN_ID}/{FILE_ADDRESS}"


def read_parquet_files(filename: str):
    """
    Read parquet file format for given filename and returns the contents
    """
    df = pd.read_parquet(filename, engine="pyarrow")
    return df

if os.path.exists("lgb_preds.parquet"):
    df_test_preds = read_parquet_files("lgb_preds.parquet")
else:
    s3_file = mlflow.artifacts.download_artifacts(
        artifact_uri=pred_s3_location, dst_path="./"
    )
    df_test_preds = read_parquet_files(s3_file)


df_items = read_parquet_files("items.parquet")


def predict(find, item_idx: int):
    """
    Takes the json inputs, processes it and outputs the unit sales
    """
    try:
        idx = pd.IndexSlice
        # df_items.sample(1).index[0]
        x = df_test_preds.loc[idx[find["store_nbr"], item_idx, find["date1"]]][
            "unit_sales"
        ]
    except KeyError:
        print("This item is not present this store. Try some other item")
        return -0.0
    else:
        return float(round(x, 2))


def lambda_handler(event, context=None) -> dict:
    """
    lambda handler for predict method
    """

    find = event["find"]
    item = df_items.sample(1)
    item_idx, item_family = item.index[0], item["family"].values[0]
    pred_unit_sales = predict(find, item_idx)

    # if pred_unit_sales == 0.0:
    #     print("item either not found or price couldn't be predicted")

    result = {
        " Store": find["store_nbr"],
        " item": int(item_idx),
        "Family": item_family,
        "Prediction date": find["date1"],
        "Unit_sales": pred_unit_sales,
    }
    return result
