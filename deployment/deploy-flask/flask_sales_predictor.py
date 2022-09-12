import pandas as pd
from flask import Flask, jsonify, request


def read_parquet_files(filename):
    """
    Read parquet file format for given filename and returns the contents
    """
    df = pd.read_parquet(filename, engine="pyarrow")
    return df


df_test_preds = read_parquet_files("lgb_predictions_wo_family.parquet")

df_items = read_parquet_files("items.parquet")

app = Flask("flask-unit-sales-prediction")


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


@app.route("/predict-sales", methods=["POST"])
def predict_endpoint():
    """
    flask predict endpoint
    """
    print("entering predict-sales endpoint")

    find = request.get_json()
    print(f"find is {find}")
    item = df_items.sample(1).index[0]
    # print(f"item is{item}")
    print("calling predcit method")
    pred_unit_sales = predict(find, item)
    if pred_unit_sales == 0.0:
        print("item either not found or price couldn't be predicted")
    result = {
        "store_nbr": find["store_nbr"],
        "item": int(item),
        "Prediction date": find["date1"],
        "unit_sales": pred_unit_sales,
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
