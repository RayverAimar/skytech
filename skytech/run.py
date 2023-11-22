from scraper import LatamScraper
from datetime import date

origin = ''
destination = ''
departure_date = date()
return_date = date()

scraper = LatamScraper(origin=origin,
                       destination=destination,
                       departure_date=departure_date,
                       return_date=return_date,
)

scraper.scrape()
scraper.save()