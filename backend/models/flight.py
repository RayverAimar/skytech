from databases.connection import db

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    departure_date = db.Column(db.String(20), nullable=False)
    departure_time = db.Column(db.String(20), nullable=False)
    arrival_date = db.Column(db.String(20), nullable=False)
    arrival_time = db.Column(db.String(20), nullable=False)
    scales = db.Column(db.Boolean, nullable=False)
