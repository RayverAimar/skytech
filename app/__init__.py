from flask import Flask, render_template, session
import random
import os

from app.databases import db
from app.models import User

from app.routes import auth, user, search_flights

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.urandom(24)
    
    db.init_app(app)
    #with app.app_context():
    #    db.create_all()

    @app.route("/", methods=['GET'])
    def home():
        if 'user_id' in session:
            user = User.query.filter_by(id=session['user_id']).first()
            return render_template("home.html", user=user, random=random)
        return render_template("home.html", user=None, random=random)

    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(search_flights)

    return app