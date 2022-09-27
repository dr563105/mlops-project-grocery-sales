import requests

event = {"find": {"date1": "2017-08-28", "store_nbr": 19}}

# print(find["date1"])
url = "http://localhost:9123/2015-03-31/functions/function/invocations"  # To test lambda function locally.
response = requests.post(url, json=event, timeout=5)
print(response.json())
