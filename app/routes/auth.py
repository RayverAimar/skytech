from flask import Blueprint, session, redirect, render_template, url_for, request

from app.databases import db

from app.models import User

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET','POST'])
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
    
@auth.route('/login', methods=['GET', 'POST'])
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

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))