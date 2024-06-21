import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import date, timedelta, datetime
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, NoSuchElementException
from .utils import *
from .config import *
from .definitions import *

class LatamScraper:
    def __init__(self, origin, destination, departure_date, return_date):
        self.origin = origin
        self.destination = destination
        self.departure_date = departure_date
        self.return_date = return_date
        self.flights = []

    def __get_flight_query_latam(self):
        if not dict_of_acronyms[self.origin]:
            raise NameError(f'\'{self.origin}\' is not a valid place.')
        if not dict_of_acronyms[self.destination]:
            raise NameError(f'\'{self.destination}\' is not a valid place.')
        if self.departure_date <= datetime.now().date():
            raise ValueError(f'{self.departure_date} is not a valid date to query flights.')
        if self.departure_date > self.return_date:
            raise ValueError(f'{self.return_date} should be equal or higher than the date of departure.')

        origin = f'origin={dict_of_acronyms[self.origin]}'
        destination = f'destination={dict_of_acronyms[self.destination]}'
        departure_date = f'outbound={self.departure_date}T12%3A00%3A00.000Z'
        return_date = f'inbound={self.return_date}T12%3A00%3A00.000Z'
        adt = 'adt=1'
        chd = 'chd=0'
        inf = 'inf=0'
        trip = 'trip=RT'
        cabin = 'cabin=Economy'
        redemption = 'redemption=false'
        sort = 'sort=PRICE%2Casc'
        query_tuple=(origin,
                     departure_date,
                     destination,
                     return_date,
                     adt,
                     chd,
                     inf,
                     trip,
                     cabin,
                     redemption,
                     sort,
        )
        url = 'https://www.latamairlines.com/pe/es/ofertas-vuelos?'
        query = url + "&".join(query_tuple)
        return query
    
    def __get_data(self):
        latam_scraper_dict_list = []
        for flight in self.flights:
            latam_scraper_dict_list.append(flight.get_dict())
        return latam_scraper_dict_list
    
    def save(self, title="flights_latam_"):
        if not self.flights:
            print('Please scrape before saving data.')
        title='./data/'+title +'outbound_'+self.origin+'_'+self.departure_date.__str__()+'.json'
        with open(title, "w") as outfile:
            json.dump(self.__get_data(), outfile)
            print(f'Data collected of Flights from {self.departure_date} saved successfully in \'{title}\'')
        return self.__get_data()

    def __get_element(self, driver, xpath, get_text=False):
        try:
            element = driver.find_element(By.XPATH, xpath)
            if get_text:
                return element.get_attribute(TEXT)
            return element
        except StaleElementReferenceException:
            return None
        except NoSuchElementException:
            return None
            
    def __get_elements(self, driver, xpath):
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            return elements
        except StaleElementReferenceException:
            return None
        except NoSuchElementException:
            return None

    def scrape(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--incognito')
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        driver.get(self.__get_flight_query_latam()) # See if dates are correct -> Should be later than today 
        try:
            import time
            time.sleep(2)
            WebDriverWait(driver, timeout=TIMEOUT_PER_PAGE).until(EC.presence_of_element_located((By.XPATH, f'//li[contains(@class, "{CLASS_BODY_FLIGHTS}")]')))
            flights = self.__get_elements(driver, f'//li[contains(@class, "{CLASS_BODY_FLIGHTS}")]')
            print(f'There were found {len(flights)} flights for {self.departure_date}')
            print(f'Initializing scraping...')
            for index, flight in enumerate(flights):
                try: 
                    print(f"Processing flight ({index+1}/{len(flights)})")
                    # Get the currency
                    currency_str = self.__get_element(flight, f'.//span[contains(@class, "{CLASS_CURRENCY}")]', get_text=True)
                    currency = currency_str.upper()[:3] if currency_str else None
                    # Currency and price have the same tags and classes, they only differ in one word
                    #price = self.__get_element(flight, f'.//span[contains(@class, "{CLASS_BASIC_PRICE}")][2]', get_text=True)
                    price = currency_str[3:]
                    price = float(price) if price else None
                    box_info = self.__get_element(flight, f'.//div[contains(@class, "{CLASS_BOX_INFO}")]')
                    
                    # Get the duration of total flight 
                    duration_str = self.__get_element(flight, '/html/body/div[1]/div[1]/main/div/div/div/div/ol/li[1]/div/div/div[1]/div[2]/div[1]/div[3]/span[2]', get_text=True)
                    if duration_str:
                        duration_hours = get_hours_from_str(duration_str)
                        duration_minutes = get_minutes_from_str(duration_str) if len(duration_str) > 4 else 0
                        duration = timedelta(
                            hours=duration_hours,
                            minutes=duration_minutes,
                        )

                    # Get the time of departure
                    departure_time_str = self.__get_element(flight, '/html/body/div[1]/div[1]/main/div/div/div/div/ol/li[1]/div/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]', get_text=True)
                    
                    if departure_time_str:    
                        departure_datetime_hour, departure_datetime_minutes = get_hours_and_minutes_from_time(departure_time_str)
                        departure_datetime = datetime(self.departure_date.year,
                                                    self.departure_date.month,
                                                    self.departure_date.day,
                                                    departure_datetime_hour,
                                                    departure_datetime_minutes,
                        )

                    # Get the time of arrival
                    arrival_datetime = departure_datetime + duration if duration_str and departure_time_str else None
                    # Get the prices per each fee
                    fees_button = self.__get_element(flight, f'.//div[contains(@class, "{CLASS_FEES_BUTTON}")]')
                    fees_button.click()
                    WebDriverWait(driver, timeout=TIMEOUT_PER_BUTTON).until(EC.presence_of_element_located((By.XPATH, f'.//button[contains(@class, "{CLASS_CLOSE_FEES_BUTTON}")]')))

                    fees = []
                    fees.append(Fee(name='basic',
                        price=price,
                    ))
                    
                    # Get the number of scales 
                    scale = self.__get_element(flight, f'.//a[contains(@class, "{CLASS_SCALE}")]/span', get_text=True)
                    
                    if scale != "Directo" or scale != "Directo*":
                        # Scale is either just one number (digit) or a complete ('Directo') word
                        scale = int(scale[0]) if scale[0].isnumeric() else scale
                    current_flight = Flight(fees=fees,
                                            currency=currency,
                                            duration=duration_str,
                                            departure_datetime=departure_datetime,
                                            arrival_datetime=arrival_datetime,
                                            scale=scale,
                    )
                    scale_button = self.__get_element(flight, f'.//a[contains(@class, "{CLASS_SCALE_BUTTON}")]')
                    if scale_button and isinstance(scale, int):
                        scale_button.click()
                        
                        WebDriverWait(driver, timeout=TIMEOUT_PER_BUTTON).until(EC.visibility_of_element_located((By.XPATH, f'//div[contains(@class, "{CLASS_SUBSEGMENT_TOP_SCALES}")]/div[contains(@class, "{CLASS_DETAILS_FLIGHT_SEGMENT}")]/span[2]')))

                        flight_segments = self.__get_elements(flight, f'//section[contains(@class, "{CLASS_FLIGHT_SEGMENTS}")]')
                        scale_segments = self.__get_elements(flight, f'//section[contains(@class, "{CLASS_SCALE_SEGMENTS}")]' )
                        if flight_segments:
                            current_flight.add_details(self.__get_details_from_flight_segment(flight_segments[0]))
                            if scale_segments:
                                for i, scale_segment in enumerate(scale_segments):
                                    current_flight.add_details(self.__get_details_from_scale_segment(scale_segment))
                                    current_flight.add_details(self.__get_details_from_flight_segment(flight_segments[i+1]))
                        
                    self.flights.append(current_flight)
                    print(current_flight)
                    print(current_flight.get_dict())
                    close_button = self.__get_element(flight, f'//button[contains(@class, "{CLASS_CLOSE_SCALE_BUTTON}")]')
                    if close_button:
                        close_button.click()
                        WebDriverWait(driver, timeout=TIMEOUT_PER_BUTTON).until(EC.presence_of_element_located((By.XPATH, f'//li[contains(@class, "{CLASS_BODY_FLIGHTS}")]')))
                    
                except StaleElementReferenceException:
                    print('Error finding element, skipping flight...')
                    continue
                except ElementClickInterceptedException:
                    print('Error while clicking element, skipping flight...')
                    continue
                except TimeoutException:
                    print('Dynamic element took to long to load, skipping flight...')
                    continue
        except TimeoutException:
            print('The site can\'t be reached. ERR_CONNECTION_TIMED_OUT.')
        driver.quit()
    
    def __get_details_from_scale_segment(self, scale_segment):
        details = self.__get_element(scale_segment, f'.//div[contains(@class, "{CLASS_DETAILS_SCALE_SEGMENT}")]/div', get_text=True)
        duration = self.__get_element(scale_segment, f'.//div[contains(@class, "{CLASS_DETAILS_SCALE_SEGMENT}")]/span', get_text=True)
        if not details or not duration:
            return None
        return Scale(duration, details)

    def __get_details_from_flight_segment(self, flight_segment):
        def get_origin_hour_airportname_from_subsegment(subsegment):
            if not subsegment:
                return None, None, None
            origin = self.__get_element(subsegment, f'.//div[contains(@class, "{CLASS_DETAILS_FLIGHT_SEGMENT}")]/span[1]', get_text=True)
            hour = self.__get_element(subsegment, f'.//div[contains(@class, "{CLASS_DETAILS_FLIGHT_SEGMENT}")]/span[2]', get_text=True)
            airport_name = self.__get_element(subsegment, f'.//span[contains(@class, "{CLASS_AIRPORT_NAME}")]', get_text=True)
            return origin, hour, airport_name
    
        subsegment_top = self.__get_element(flight_segment, f'.//div[contains(@class, "{CLASS_SUBSEGMENT_TOP_SCALES}")]')
        origin, departure_hour, departure_airport_name = get_origin_hour_airportname_from_subsegment(subsegment_top)
        duration = self.__get_element(flight_segment, f'.//div[contains(@class, "{CLASS_SUBSEGMENT_MIDDLE_SCALES}")]/span[2]', get_text=True)
        subsegment_bot = self.__get_element(flight_segment, f'.//div[contains(@class, "{CLASS_SUBSEGMENT_BOT_SCALES}")]')
        destination, arrival_hour, arrival_airport_name = get_origin_hour_airportname_from_subsegment(subsegment_bot)
        flight_code = self.__get_element(flight_segment, f'.//div[contains(@class, "{CLASS_FLIGHT_CODE}")]', get_text=True)
        airplane_name = self.__get_element(flight_segment, f'.//span[contains(@class, "{CLASS_AIRPLANE_NAME}")]', get_text=True)

        return FlightDetails(origin,
                            departure_hour,
                            departure_airport_name,
                            duration,
                            destination,
                            arrival_hour,
                            arrival_airport_name,
                            flight_code,
                            airplane_name,
        )