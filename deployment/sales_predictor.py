import pandas as pd

from flask import Flask, request, jsonify

def read_parquet_files(filename):
    """
    Read parquet file format for given filename and returns the contents
    """
    df = pd.read_parquet(filename, engine="pyarrow")
    return df


df_test_preds = read_parquet_files('df_test_preds_wo_family.parquet')

df_items = read_parquet_files("../input/grocery-sales-forecasting-parquet/items.parquet")

app = Flask('unit-sales-prediction')

def predict(info):
    idx=pd.IndexSlice
    item = df_items.sample(1).index[0]
    store = info[0]
    date1 = info[1]
    x = df_test_preds.loc[idx[store, item, date1]]['unit_sales']
    return round(x,2)

@app.route('/predict-sales', methods=['POST'])
def predict_endpoint():
    info = request.get_data()

    pred_unit_sales = predict(info)

    result = {
        'unit_sales': pred_unit_sales
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7200)