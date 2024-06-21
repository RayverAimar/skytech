
from flask import Blueprint, session, redirect, render_template, url_for, request

import re
from datetime import datetime, date

from app.databases import db

from app.models import User, Flight, SearchHistory

from app.scrapers import LatamScraper

from openai import OpenAI

client = OpenAI(api_key='.')

search_flights = Blueprint('search_flights', __name__)

@search_flights.route('/search', methods=['POST'])
def search():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    query = request.form['search']
    
    if query == '':
        return redirect(url_for('home'))
    
    flight_info = obtener_datos_vuelo(query)

    if isinstance(flight_info, str):  # In case of error or missing information
        print(flight_info)
        return redirect(url_for('home'))

    origin = flight_info['origen']
    destination = flight_info['destino']
    departure_date = datetime.strptime(flight_info['fecha_ida'], '%d/%m').replace(year=datetime.now().year).date()
    return_date = datetime.strptime(flight_info['fecha_vuelta'], '%d/%m').replace(year=datetime.now().year).date() if 'fecha_vuelta' in flight_info else None


    '''
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
    '''
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
    return_date = datetime.strptime(request.args.get('return_date'), '%Y-%m-%d').date()

    print("OK:", origin, destination, departure_date, return_date)

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

    # Obtener el vuelo más barato
    cheapest_flight = query.order_by(Flight.price).first()

    if not cheapest_flight:
        # Scraper
        scraper = LatamScraper(
            origin=origin,
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

        cheapest_flight = query.order_by(Flight.price).first()
    
    if cheapest_flight:
        keys = ["id", "price", "duration", "departure_date", "departure_time", "arrival_date", "arrival_time", "scales", "origin", "destination"]
        documents = [dict(zip(keys, [getattr(cheapest_flight, key) for key in keys]))]
    else:
        documents = []

    return render_template("search_results.html", query="Flight Results", documents=documents)

  
    '''
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


        cheapest_flight = query.order_by(Flight.price).first()

    if not cheapest_flight:
        # Scraper
        scraper = LatamScraper(
            origin=origin,
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

        cheapest_flight = query.order_by(Flight.price).first()
    
    if cheapest_flight:
        keys = ["id", "price", "duration", "departure_date", "departure_time", "arrival_date", "arrival_time", "scales"]
        documents = [dict(zip(keys, [getattr(cheapest_flight, key) for key in keys]))]
    else:
        documents = []

    return render_template("search_results.html", query="Flight Results", documents=documents)


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
'''

def obtener_datos_vuelo(consulta):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {"role": "system", "content": "You are a travel agent that receives a message from a customer asking for flight details. You need to extract the following information from the message: origin, destination and dates of departure and return. The text for departure is the following Departure date and for return is Return date. The format of the dates is dd/mm."},
                {"role": "user", "content": consulta}
            ]
        )

        respuesta = response.choices[0].message
        stringRespuesta = respuesta.content
        datos_vuelo = stringRespuesta.split("\n")

        info_vuelo = {}
        for dato in datos_vuelo:
            if "Origin" in dato:
                info_vuelo['origen'] = dato.split(":")[1].strip()
            elif "Destination" in dato:
                info_vuelo['destino'] = dato.split(":")[1].strip()
            elif "Departure date" in dato:
                info_vuelo['fecha_ida'] = dato.split(":")[1].strip()
            elif "Return date" in dato:
                info_vuelo['fecha_vuelta'] = dato.split(":")[1].strip()

        faltantes = [campo for campo in ['origen', 'destino', 'fecha_ida'] if campo not in info_vuelo]

        if faltantes:
            return f"Faltan los siguientes datos: {', '.join(faltantes)}"
        else:
            return info_vuelo

    except Exception as e:
        return str(e)