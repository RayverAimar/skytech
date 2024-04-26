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
    # Modelo de usuario
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    searches = db.relationship('SearchHistory', backref='user')
    friend_requests_sent = db.relationship('FriendRequest', foreign_keys='FriendRequest.sender_id', backref='sender')
    friend_requests_received = db.relationship('FriendRequest', foreign_keys='FriendRequest.receiver_id', backref='receiver')

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(50), nullable=False)
    departure_date = db.Column(db.String(50), nullable=False)
    return_date = db.Column(db.String(50), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class FriendRequest(db.Model):
    # Solicitud de amistad
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'accepted', 'rejected'

#db.create_all()

@app.route('/send_friend_request/<int:receiver_id>', methods=['POST'])
def send_friend_request(receiver_id):
    if 'user_id' in session:
        sender_id = session['user_id']
        friend_request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id)
        db.session.add(friend_request)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/accept_friend_request/<int:request_id>', methods=['POST'])
def accept_friend_request(request_id):
    if 'user_id' in session:
        user_id = session['user_id']
        friend_request = FriendRequest.query.get(request_id)
        if friend_request and friend_request.receiver_id == user_id:
            friend_request.status = 'accepted'
            db.session.commit()
    return redirect(url_for('index'))

@app.route('/reject_friend_request/<int:request_id>', methods=['POST'])
def reject_friend_request(request_id):
    if 'user_id' in session:
        user_id = session['user_id']
        friend_request = FriendRequest.query.get(request_id)
        if friend_request and friend_request.receiver_id == user_id:
            friend_request.status = 'rejected'
            db.session.commit()
    return redirect(url_for('index'))


#def profile(user_id):
#    if 'user_id' in session:
#        user = User.query.get(user_id)
#        if user:
#            return render_template('profile.html', user=user)
#    return redirect(url_for('index'))

#@app.route('/profile', methods=['GET', 'POST'])
@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    print('profile')
    if 'user_id' in session:
        user = User.query.get(user_id)
        friend_requests_received = FriendRequest.query.filter_by(receiver_id=user_id, status='pending').all()
        # find friends
        friendsAccepted = FriendRequest.query.filter_by(sender_id=user_id, status='accepted').all()
        friends = User.query.filter(User.id.in_([friend.receiver_id for friend in friendsAccepted])).all()
        if request.method == 'POST':
            sender_id = user.id
            receiver_username = request.form['receiver_username']
            receiver = User.query.filter_by(username=receiver_username).first()
            if receiver:
                # Verificar si ya existe una solicitud pendiente entre los usuarios
                existing_request = FriendRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver.id).first()
                if not existing_request:
                    new_request = FriendRequest(sender_id=sender_id, receiver_id=receiver.id)
                    db.session.add(new_request)
                    db.session.commit()
        return render_template('profile.html', user=user, friend_requests_received=friend_requests_received, friends=friends)
    else:
        return redirect(url_for('login'))



@app.route('/profile/search_users', methods=['GET', 'POST'])
def search_users():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            users = User.query.filter(User.username.ilike(f'%{search_query}%')).all()
            return render_template('search_results.html', users=users)
    return redirect(url_for('profile'))

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
