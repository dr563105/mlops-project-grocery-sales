import requests

find = {"date1": "2017-08-21", "store_nbr": 19}

# print(find["date1"])
url = "http://localhost:9696/predict-sales"
response = requests.post(url, json=find, timeout=5)
print(response.json())
