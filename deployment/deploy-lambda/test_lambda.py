import lambda_function

event = {"find": {"date1": "2022-09-15", "store_nbr": 19}}

url = "http://localhost:9696/predict-sales"
response = lambda_function.lambda_handler(event, None)
print(response)
