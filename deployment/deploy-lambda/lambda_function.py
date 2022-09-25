import pandas as pd


def read_parquet_files(filename):
    """
    Read parquet file format for given filename and returns the contents
    """
    df = pd.read_parquet(filename, engine="pyarrow")
    return df


df_test_preds = read_parquet_files("lgb_predictions_wo_family_v1.parquet")

df_items = read_parquet_files("items.parquet")


def predict(find, item):
    """
    Takes the json inputs, processes it and outputs the unit sales
    """
    print("inside predict function")
    idx = pd.IndexSlice
    # df_items.sample(1).index[0]
    x = df_test_preds.loc[idx[find["store_nbr"], item, find["date1"]]][
        "unit_sales"
    ]

    return float(round(x, 2))


def lambda_handler(event, context):
    """
    lambda handler for predict method
    """

    find = event["find"]
    print(f"find is {find}")
    item = df_items.sample(1).index[0]
    print("calling predict method")
    pred_unit_sales = predict(find, item)

    if pred_unit_sales == 0.0:
        print("item either not found or price couldn't be predicted")

    result = {
        "store_nbr": find["store_nbr"],
        "item": int(item),
        "Prediction date": find["date1"],
        "unit_sales": pred_unit_sales,
    }
    return result
