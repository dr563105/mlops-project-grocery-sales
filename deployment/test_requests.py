import requests

find = {"date1": "2022-09-15", "store_nbr": 19}

url = "http://localhost:9696/predict-sales"
response = requests.post(url, json=find, timeout=5)
print(response.json())
