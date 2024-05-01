from flask import Blueprint, session, redirect, render_template, url_for, request
import random

from app.databases import db

from app.models import User, SearchHistory, FriendRequest

user = Blueprint('user', __name__, url_prefix='/user')

@user.route('/search_history', methods=['GET'])
def search_history():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        if user:
            searches = SearchHistory.query.filter_by(usuario_id=user_id).all()
            return render_template('search_history.html', user=user, searches=searches, random=random)
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))
    
@user.route('/profile/search_users', methods=['GET', 'POST'])
def search_users():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            users = User.query.filter(User.username.ilike(f'%{search_query}%')).all()
            return render_template('search_users.html', users=users)
    return redirect(url_for('home'))
    
@user.route('/profile/<int:user_id>', methods=['GET', 'POST'])
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
        return render_template('profile.html', user=user, friend_requests_received=friend_requests_received, friends=friends, random=random)
    else:
        return redirect(url_for('auth.login'))
    
@user.route('/send_friend_request/<int:receiver_id>', methods=['POST'])
def send_friend_request(receiver_id):
    if 'user_id' in session:
        sender_id = session['user_id']
        friend_request = FriendRequest(sender_id=sender_id, receiver_id=receiver_id)
        db.session.add(friend_request)
        db.session.commit()
    return redirect(url_for('home'))

@user.route('/accept_friend_request/<int:request_id>', methods=['POST'])
def accept_friend_request(request_id):
    if 'user_id' in session:
        user_id = session['user_id']
        friend_request = FriendRequest.query.get(request_id)
        if friend_request and friend_request.receiver_id == user_id:
            friend_request.status = 'accepted'
            db.session.commit()
    return redirect(url_for('home'))

@user.route('/reject_friend_request/<int:request_id>', methods=['POST'])
def reject_friend_request(request_id):
    if 'user_id' in session:
        user_id = session['user_id']
        friend_request = FriendRequest.query.get(request_id)
        if friend_request and friend_request.receiver_id == user_id:
            friend_request.status = 'rejected'
            db.session.commit()
    return redirect(url_for('home'))