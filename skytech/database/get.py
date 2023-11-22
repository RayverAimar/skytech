import requests

base_url = "http://127.0.0.1:5000/flight/"

response = requests.get(base_url + str(1))

print(response.status_code)
print(response.json())