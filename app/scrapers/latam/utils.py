HOUR = 'hour'
MINUTES = 'min'

def get_minutes_from_str(datetime_str):
        '''
        Function to return minutes of an str. 
        If datetime lenght is more than 4 characters then it has minutes in it.
        Sample: 1 hr 25 min -> 25
        '''
        if not datetime_str:
            return None
        index_to_trim = -1
        for i, e in enumerate(datetime_str):
            if e == MINUTES[0]:
                index_to_trim = i
                break
        return int(datetime_str[index_to_trim-3:index_to_trim-1])

def get_hours_from_str(datetime_str):
    '''
        Function to return hours of a formatted str. 
        Sample: 10 hr 25 min -> 1
                2 hr 35 min -> 2
                5 hr -> 5
    '''
    if not datetime_str:
        return None
    index_to_trim = -1
    for i, e in enumerate(datetime_str):
        if e == HOUR[0]:
            index_to_trim = i
            break
    return int(datetime_str[:index_to_trim-1])

def get_hours_and_minutes_from_time(datetime_):
    '''
        Function to return hours and minutes of a formatted time.
        Sample: 10:00 -> 10 0
                14:25 -> 14 25 
    '''
    separator_index = -1
    for i, e in enumerate(datetime_):
        if e == ':':
            separator_index = i
            break
    return int(datetime_[:separator_index]), int(datetime_[separator_index+1:])

class Flight:
    def __init__(self, fees, currency, duration, departure_datetime, arrival_datetime, scale):
        self.fees = fees
        self.currency = currency
        self.duration = duration
        self.departure_datetime = departure_datetime
        self.arrival_datetime = arrival_datetime
        self.scale = scale
        self.details = []

    def add_details(self, detail):
        self.details.append(detail)
    
    def get_dict(self):
        flight_dict = {}
        fees_dict = {}
        if self.fees:
            for fee in self.fees:
                fees_dict[fee.name] = fee.price
        flight_dict['price'] = fees_dict['basic']
        flight_dict['currency'] = self.currency
        flight_dict['duration'] = self.duration
        if self.departure_datetime:
            flight_dict['departure_date'] = '-'.join((str(self.departure_datetime.year), str(self.departure_datetime.month), str(self.departure_datetime.day)))
            flight_dict['departure_time'] = ':'.join((str(self.departure_datetime.hour), str(self.departure_datetime.minute)))
        else:
            flight_dict['departure_date'] = None
            flight_dict['departure_time'] = None
        
        if self.arrival_datetime:
            flight_dict['arrival_date'] = '-'.join((str(self.arrival_datetime.year), str(self.arrival_datetime.month), str(self.arrival_datetime.day)))
            flight_dict['arrival_time'] = ':'.join((str(self.arrival_datetime.hour), str(self.arrival_datetime.minute)))
        else:
            flight_dict['arrival_date'] = None
            flight_dict['arrival_time'] = None
        flight_dict['scales'] = False if self.scale == 'Directo' else True
        details_list = []
        for detail in self.details:
            if detail:
                details_list.append(detail.get_dict())
        flight_dict['details'] = details_list if self.details else None
        return flight_dict
    
    def __str__(self):
        return (f"Flight Information:\n"
                f"Fees: {self.currency}\n"
                f"Duration: {self.duration}\n"
                f"Departure: {self.departure_datetime}\n"
                f"Arrival: {self.arrival_datetime}\n"
                f"Scale: {'Yes' if self.scale else 'No'}")

class FlightDetails:
    def __init__(self, origin, departure_time, departure_airport, duration, destination, arrival_time, arrival_airport, flight_code, airplane_code):
        self.origin = origin
        self.departure_time = departure_time
        self.departure_airport = departure_airport
        self.duration = duration
        self.destination = destination
        self.arrival_time = arrival_time
        self.arrival_airport = arrival_airport
        self.flight_code = flight_code
        self.airplane_code = airplane_code

    def __str__(self) -> str:
        out_str = f'\tFlight: {self.flight_code} ({self.airplane_code})\n'
        out_str += f'\t- Origin: {self.origin} {self.departure_time} ({self.departure_airport})\n'
        out_str += f'\t- Duration: {self.duration}\n'
        out_str += f'\t- Destination: {self.destination} {self.arrival_time} ({self.arrival_airport})'
        return out_str
    
    def get_dict(self):
        flightdetails_dict = {}
        flightdetails_dict['flight_code'] = self.flight_code
        flightdetails_dict['airplane_code'] = self.airplane_code
        flightdetails_dict['origin'] = self.origin
        flightdetails_dict['origin_airport'] = self.departure_airport
        flightdetails_dict['departure_time'] = self.departure_time
        flightdetails_dict['destination'] = self.destination
        flightdetails_dict['destination_airport'] = self.arrival_airport
        flightdetails_dict['arrival_time'] = self.arrival_time
        flightdetails_dict['duration'] = self.duration
        return flightdetails_dict

class Scale:
    def __init__(self, scale_duration, details):
        self.scale_duration = scale_duration
        self.details = details
    
    def __str__(self) -> str:
        return f'\t\t{self.details}\n\t\t{self.scale_duration}'
    
    def get_dict(self):
        scale_dict = {}
        scale_dict['scale_details'] = self.details
        scale_dict['scale_duration'] = self.scale_duration
        return scale_dict

class Fee:
    def __init__(self, name, price):
        self.name = name
        self.price = price

dict_of_acronyms = {
    'Arequipa':'AQP',
    'Cuzco':'CUZ',
    'Lima':'LIM',
    'Piura':'PIU',
    'Tumbes':'TBP'
}

