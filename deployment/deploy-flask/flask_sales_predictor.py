import pandas as pd
from flask import Flask, jsonify, request


def read_parquet_files(filename):
    """
    Read parquet file format for given filename and returns the contents
    """
    df = pd.read_parquet(filename, engine="pyarrow")
    return df


df_test_preds = read_parquet_files("lgb_predictions_wo_family_v1.parquet")
print(df_test_preds.index)

df_items = read_parquet_files("items.parquet")

app = Flask("flask-unit-sales-prediction")


def predict(find, item):
    """
    Takes the json inputs, processes it and outputs the unit sales
    """
    idx = pd.IndexSlice
    # df_items.sample(1).index[0]
    print(f"item inside predict function:{item}")
    print(f"Store is: {find['store_nbr']}")
    print(f"date is: {find['date1']}")
    print(f"loc is: {idx[find['store_nbr'], item, find['date1']]}")
    # x = df_test_preds.loc[idx[find["store_nbr"], item, find["date1"]]]["unit_sales"]

    return 1.1  # float(round(x, 2))


@app.route("/predict-sales", methods=["POST"])
def predict_endpoint():
    """
    flask predict endpoint
    """
    find = request.get_json()
    print(f"find is {find}")
    item = df_items.sample(1).index[0]
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
