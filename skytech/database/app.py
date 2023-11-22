from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

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
            id=flight_id,
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

if __name__ == "__main__":
    #db.create_all()
    app.run(debug=True)
