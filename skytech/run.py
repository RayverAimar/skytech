from scraper import LatamScraper
from datetime import date

import requests

origin = 'Arequipa'
destination = 'Lima'
departure_date = date(2024, 2, 3)
return_date = date(2024, 2, 5) # For the moment, it can be set to non-real date 

scraper = LatamScraper(origin=origin,
                       destination=destination,
                       departure_date=departure_date,
                       return_date=return_date,
)

scraper.scrape()
data = scraper.save()

base_url = "http://127.0.0.1:5000/flight/"

for index, flight_data in enumerate(data, start=1):
    response_post = requests.post(base_url + str(index), json=flight_data)
    print(f"Status Code (POST {index}):", response_post.status_code)
    #print(f"Response (POST {index}):", response_post.json())

