from flask import Flask, request, render_template, redirect, url_for, session
import random
import os
from dateutil import parser
import re

from datetime import datetime, timedelta

from databases import db
from models import Flight, User, SearchHistory

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

db.init_app(app)
#db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'user_id' not in session:
            redirect(url_for('login'))
        query = request.form["search"]
        if query != "":
            return redirect(url_for('search', query=query))
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        return render_template("index.html", user=user, random=random)
    return render_template("index.html", user=None, random=random)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        last_name = request.form['surname']
        email = request.form['email']
        phone = request.form['phone']
        user = User(username=username,
                    password=password,
                    email=email,
                    first_name=name,
                    last_name=last_name,
                    phone=phone)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('index'))
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
        return redirect(url_for('index'))
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    origin, destination = query.split(' to ', 1) # Format of query shall be 'origin to destination'
    departure_date = (datetime.now() + timedelta(days=1)).strftime('%d %m %Y')
    return_date = (datetime.now() + timedelta(days=2)).strftime('%d %m %Y')
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
            return redirect(url_for('search_results'))
    return redirect(url_for('index'))

@app.route('/search_history', methods=['GET'])
def search_history():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        if user:
            searches = SearchHistory.query.filter_by(usuario_id=user_id).all()
            return render_template('search_history.html', user=user, searches=searches, random=random)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route("/search_results")
def search_results():
    #connection = sqlite3.connect('database.db')
    #cursor = db.c.cursor()
   # paser = parse_travel_query(query)
    #departure_date_str = paser['depart_date'].strftime("%Y-%m-%d")
    #cursor.execute("SELECT * FROM flight_model WHERE departure_date = ?", (departure_date_str))
   # db.execute("SELECT * FROM flight_model")
    
    user_info = None

   
    flights = Flight.query.all()
    #flights = db.fetchall()

    #print(parse_travel_query(query))
    print(flights)
    
    keys = ["id", "price", "duration", "departure_date", "departure_time", "arrival_date", "arrival_time", "scales"]
    documents = [dict(zip(keys, [getattr(flight, key) for key in keys])) for flight in flights]


   # connection.close()
    return render_template("search_results.html", query="Flights Results", documents=documents )

def parse_travel_query(query):
    # Patrones de expresiones regulares para extraer la información
    pattern = (r"(?P<origin>from\s+\w+)|"
               r"(?P<destination>to\s+\w+)|"
               r"(?P<depart_date>on\s+\w+\s+\d{1,2}(st|nd|rd|th)?\s+\w+)|"
               r"(?P<return_date>returning\s+on\s+\w+\s+\d{1,2}(st|nd|rd|th)?\s+\w+)")

    matches = re.finditer(pattern, query, re.IGNORECASE)

    # Diccionario para guardar la información encontrada
    travel_info = {
        'origin': None,
        'destination': None,
        'depart_date': None,
        'return_date': None,
    }

    # Extraer la información
    for match in matches:
        if match.group('origin'):
            travel_info['origin'] = match.group('origin').split(' ')[1]
        if match.group('destination'):
            travel_info['destination'] = match.group('destination').split(' ')[1]
        if match.group('depart_date'):
            travel_info['depart_date'] = parser.parse(match.group('depart_date').replace('on ', ''), fuzzy=True)
        if match.group('return_date'):
            travel_info['return_date'] = parser.parse(match.group('return_date').replace('returning on ', ''), fuzzy=True)
    return travel_info


if __name__ == "__main__":
    app.run(debug=True)
