from scraper import LatamScraper
from datetime import date

origin = 'Arequipa'
destination = 'Lima'
departure_date = date(2024, 5, 3)
return_date = date(2024, 5, 5) # For the moment, it can be set to non-real date 

scraper = LatamScraper(origin=origin,
                       destination=destination,
                       departure_date=departure_date,
                       return_date=return_date,
)

scraper.scrape()
data = scraper.save()