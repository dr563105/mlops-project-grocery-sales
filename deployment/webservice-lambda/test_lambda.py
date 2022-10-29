import lambda_function

event = {"find": {"date1": "2017-08-24", "store_nbr": 9}}

response = lambda_function.lambda_handler(event, None)
print(response)
