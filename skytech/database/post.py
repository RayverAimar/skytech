import requests

base_url = "http://127.0.0.1:5000/flight/"

# Insertar datos (solicitud POST)
flight_data = {
    "price": 500.0,
    "duration": "2 hours",
    "departure_date": "2023-12-01",
    "departure_time": "08:00 AM",
    "arrival_date": "2023-12-01",
    "arrival_time": "10:00 AM",
    "scales": True
}

response_post = requests.post(base_url + "2", json=flight_data)
print("Status Code (POST):", response_post.status_code)
print("Response (POST):", response_post.json())

# Obtener datos (solicitud GET)
response_get = requests.get(base_url + "1")
print("Status Code (GET):", response_get.status_code)
print("Response (GET):", response_get.json())
