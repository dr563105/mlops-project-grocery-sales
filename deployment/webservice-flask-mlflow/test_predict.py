import flask_sales_predictor

find = {"date1": "2017-08-29", "store_nbr": 19}
df_items = flask_sales_predictor.read_parquet_files("items.parquet")
item = df_items.sample(1)
item_idx, item_family = item.index[0], item["family"].values[0]
print(f"item_idx:{item_idx}, Item belongs to family: {item_family} ")
result = flask_sales_predictor.predict(find, item_idx)
# if result == 0.0:
#     print("Unit_sales couldn't be predicted for the date")
print(
    f"Predicted Unit sales for the item in {item_family} on {find['date1']} is {result}"
)
