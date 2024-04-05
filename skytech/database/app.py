from flask import Flask, request, render_template, redirect, url_for
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import date

import sqlite3


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class FlightModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    departure_date = db.Column(db.String(20), nullable=False)
    departure_time = db.Column(db.String(20), nullable=False)
    arrival_date = db.Column(db.String(20), nullable=False)
    arrival_time = db.Column(db.String(20), nullable=False)
    scales = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Flight(id={self.id}, price={self.price}, duration={self.duration}, departure_date={self.departure_date}, departure_time={self.departure_time}, arrival_date={self.arrival_date}, arrival_time={self.arrival_time}, scales={self.scales})"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)

class SearchFlights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(50), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

flight_put_args = reqparse.RequestParser()
flight_put_args.add_argument("price", type=float, help="Price of the flight", required=True)
flight_put_args.add_argument("duration", type=str, help="Duration of the flight", required=True)
flight_put_args.add_argument("departure_date", type=str, help="Departure date of the flight", required=True)
flight_put_args.add_argument("departure_time", type=str, help="Departure time of the flight", required=True)
flight_put_args.add_argument("arrival_date", type=str, help="Arrival date of the flight", required=True)
flight_put_args.add_argument("arrival_time", type=str, help="Arrival time of the flight", required=True)
flight_put_args.add_argument("scales", type=bool, help="Scales of the flight", required=True)

flight_update_args = reqparse.RequestParser()
flight_update_args.add_argument("price", type=float, help="Price of the flight")
flight_update_args.add_argument("duration", type=str, help="Duration of the flight")
flight_update_args.add_argument("departure_date", type=str, help="Departure date of the flight")
flight_update_args.add_argument("departure_time", type=str, help="Departure time of the flight")
flight_update_args.add_argument("arrival_date", type=str, help="Arrival date of the flight")
flight_update_args.add_argument("arrival_time", type=str, help="Arrival time of the flight")
flight_update_args.add_argument("scales", type=bool, help="Scales of the flight")

resource_fields = {
    'id': fields.Integer,
    'price': fields.Float,
    'duration': fields.String,
    'departure_date': fields.String,
    'departure_time': fields.String,
    'arrival_date': fields.String,
    'arrival_time': fields.String,
    'scales': fields.Boolean,
}

class Flight(Resource):

    @marshal_with(resource_fields)
    def get(self, flight_id):
        result = FlightModel.query.get(flight_id)
        if not result:
            abort(404, message="Could not find flight with that ID")
        return result

    @marshal_with(resource_fields)
    def put(self, flight_id):
        args = flight_put_args.parse_args()
        flight = FlightModel.query.get(flight_id)
        if not flight:
            abort(404, message="Flight does not exist, cannot update")

        if args['price']:
            flight.price = args['price']
        if args['duration']:
            flight.duration = args['duration']
        if args['departure_date']:
            flight.departure_date = args['departure_date']
        if args['departure_time']:
            flight.departure_time = args['departure_time']
        if args['arrival_date']:
            flight.arrival_date = args['arrival_date']
        if args['arrival_time']:
            flight.arrival_time = args['arrival_time']
        if args['scales']:
            flight.scales = args['scales']

        db.session.commit()

        return flight, 200

    @marshal_with(resource_fields)
    def post(self, flight_id):
        args = flight_put_args.parse_args()
        flight = FlightModel(
            #id=flight_id,
            price=args['price'],
            duration=args['duration'],
            departure_date=args['departure_date'],
            departure_time=args['departure_time'],
            arrival_date=args['arrival_date'],
            arrival_time=args['arrival_time'],
            scales=args['scales']
        )
        db.session.add(flight)
        db.session.commit()
        return flight, 201


    @marshal_with(resource_fields)
    def patch(self, flight_id):
        args = flight_update_args.parse_args()
        result = FlightModel.query.filter_by(id=flight_id).first()
        if not result:
            abort(404, message="Flight does not exist, cannot update")

        if args['price']:
            result.price = args['price']
        if args['duration']:
            result.duration = args['duration']
        if args['departure_date']:
            result.departure_date = args['departure_date']
        if args['departure_time']:
            result.departure_time = args['departure_time']
        if args['arrival_date']:
            result.arrival_date = args['arrival_date']
        if args['arrival_time']:
            result.arrival_time = args['arrival_time']
        if args['scales']:
            result.scales = args['scales']

        db.session.commit()

        return result

    #def delete(self, flight_id):
        #abort_if_flight_doesnt_exist(flight_id)
        #del flights[flight_id]
        #return '', 204

api.add_resource(Flight, "/flight/<int:flight_id>")
@app.route('/user/<int:id>', methods=['GET'])
def index(id):
    # find in database user
    # if user exists, return render_template('index.html')
    # if user does not exist, return render_template('login.html')
    data = User.query.filter_by(id=id).first()
    if data:
        busquedas = SearchFlights.query.filter_by(usuario_id=id).all()
        dataDic = {
            'id': data.id,
            'username': data.username,
            'password': data.password,
            'email': data.email,
            'firstname': data.first_name,
            'lastname': data.last_name,
            'phone': data.phone
        }
        busquedasDic = []
        if len(busquedas) > 0:
            for busqueda in busquedas:
                busquedasDic.append({
                    'id': busqueda.id,
                    'origin': busqueda.origin,
                    'destination': busqueda.destination,
                    'departure_date': busqueda.departure_date,
                    'return_date': busqueda.return_date
                })
            return render_template('infoUser.html', data=dataDic, skies=busquedasDic)
        else:
            return render_template('infoUser.html', data=dataDic)
    else:
        return render_template('login.html')
    
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        last_name = request.form['surname']
        email = request.form['email']
        phone = request.form['phone']
        user = User(username=username, password=password, email=email, first_name=name, last_name=last_name, phone=phone)
        db.session.add(user)
        db.session.commit()
        # execute route /user/id
        return index(user.id)
    else:
        return render_template('login.html')
    

@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        query = request.form["search"]
        
        if query != "":
            return redirect(url_for("search_results", query=query))
    
    
    return render_template("index.html")

@app.route("/search_results/<query>")
def search_results(query):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM flight_model")
    
    flights = cursor.fetchall()
    
    keys = ["id", "price", "duration", "departure_date", "departure_time", "arrival_date", "arrival_time", "scales"]
    documents = [dict(zip(keys, flight)) for flight in flights]

    connection.close()

    return render_template("search_results.html", query=query, documents=documents)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
