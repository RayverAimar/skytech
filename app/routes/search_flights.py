
from flask import Blueprint, session, redirect, render_template, url_for, request

import re
from datetime import datetime, date

from app.databases import db

from app.models import User, Flight, SearchHistory

from app.scrapers import LatamScraper

search_flights = Blueprint('search_flights', __name__)

@search_flights.route('/search', methods=['POST'])
def search():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    query = request.form['search']
    
    if query == '':
        return redirect(url_for('home'))
    
    ### Parsed Query ### 
    date_matches = re.findall(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})', query, re.IGNORECASE)
    parsed_dates = []
    for match in date_matches:
        try:
            month, day = match
            date_str = f'{day} {month} {datetime.now().year}'
            parsed_date = datetime.strptime(date_str, '%d %b %Y').date()
            parsed_dates.append(date(parsed_date.year, parsed_date.month, parsed_date.day))
        except ValueError as e:
            print(f"Error al parsear la fecha: {e}")
            continue

    origin, destination = query.split(' to ', 1) # Format of query shall be 'origin to destination'
    destination =  destination.split(' ', 1)[0]
    departure_date, return_date = parsed_dates
    
    print(origin, destination, departure_date, return_date)
    #departure_date = (datetime.now() + timedelta(days=1)).strftime('%d %m %Y')
    #return_date = (datetime.now() + timedelta(days=2)).strftime('%d %m %Y')

    ### Save Query in History ###
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        if user:
            new_search = SearchHistory(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                usuario_id=user.id,
            )
            db.session.add(new_search)
            db.session.commit()
        
        return redirect(url_for('search_flights.search_results',
                        origin=origin,
                        destination=destination,
                        departure_date=departure_date,
                        return_date=return_date))

    
    return redirect(url_for('auth.signup')) 

@search_flights.route('/search_results', methods=['GET'])
def search_results():

    origin = request.args.get('origin')
    destination = request.args.get('destination')
    departure_date = datetime.strptime(request.args.get('departure_date'), '%Y-%m-%d').date()
    return_date =  datetime.strptime(request.args.get('return_date'), '%Y-%m-%d').date()

    print("OK:" , origin, destination, departure_date, return_date)

    query = Flight.query

    dict_of_acronyms = {
    'Arequipa':'AQP',
    'Cuzco':'CUZ',
    'Lima':'LIM',
    'Piura':'PIU',
    'Tumbes':'TBP'
    }

    if origin:
        query = query.filter(Flight.origin == dict_of_acronyms[origin])
    
    if destination:
        query = query.filter(Flight.destination == dict_of_acronyms[destination])

    if departure_date:
        query = query.filter(Flight.departure_date == departure_date)

    flights = query.order_by(Flight.departure_date).all()

    if not flights:
        # Scraper
        scraper = LatamScraper(origin=origin,
                       destination=destination,
                       departure_date=departure_date,
                       return_date=return_date,
        )

        scraper.scrape()
        flights_data = scraper.save()

        for flight_info in flights_data:
            flight = Flight(
                origin=flight_info['details'][0]['origin'],
                destination=flight_info['details'][0]['destination'],
                price=flight_info['price'],
                duration=flight_info['duration'],
                departure_date=datetime.strptime(flight_info['departure_date'], '%Y-%m-%d').date(),
                departure_time=datetime.strptime(flight_info['departure_time'], '%H:%M').time(),
                arrival_date=datetime.strptime(flight_info['arrival_date'], '%Y-%m-%d').date(),
                arrival_time=datetime.strptime(flight_info['arrival_time'], '%H:%M').time(),
                scales=flight_info['scales']
            )
            db.session.add(flight)

        db.session.commit()

        query = Flight.query

        if origin:
            query = query.filter(Flight.origin == dict_of_acronyms[origin])
    
        if destination:
            query = query.filter(Flight.destination == dict_of_acronyms[destination])

        if departure_date:
            query = query.filter(Flight.departure_date == departure_date)

        flights = query.order_by(Flight.departure_date).all()
    
    keys = ["id", "price", "duration", "departure_date", "departure_time", "arrival_date", "arrival_time", "scales"]
    documents = [dict(zip(keys, [getattr(flight, key) for key in keys])) for flight in flights]

    return render_template("search_results.html", query="Flights Results", documents=documents)  
