from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key'
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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    searches = relationship('SearchHistory', backref='user')

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(50), nullable=False)
    departure_date = db.Column(db.String(50), nullable=False)
    return_date = db.Column(db.String(50), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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

if __name__ == "__main__":
    app.run(debug=True)
