import flask_sales_predictor

find = {"date1": "2017-08-29", "store_nbr": 19}
df_items = flask_sales_predictor.read_parquet_files("items.parquet")
item = df_items.sample(1).index[0]
print(f"item:{item}")
result = flask_sales_predictor.predict(find, item)
if result == 0.0:
    print("Item not found or unit_sales couldn't be predicted for the date")
print(f"Unit sales is {result}")
