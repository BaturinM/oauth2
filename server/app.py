from flask import Flask
from .models import db, Client, User
from .oauth2 import create_server
from sqlalchemy_utils import database_exists, create_database, drop_database
from .settings import SQLALCHEMY_DATABASE_URI


def init_db():
    db.create_all()

    client = Client(name='dev',
                    client_id='dev',
                    client_secret='dev',
                    _redirect_uris='http://localhost:5000/authorized')
    user = User(username='user',
                password='password',
                email='user@gmail.com',
                phone='1234567890')
    admin = User(username='admin',
                password='password',
                email='admin@gmail.com',
                phone='1234567890')
    db.session.add(client)
    db.session.add(user)
    db.session.add(admin)
    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    setup_app(app)
    return app


def setup_app(app):
    db.init_app(app)
    with app.app_context():
        drop_database(SQLALCHEMY_DATABASE_URI)
        if not database_exists(SQLALCHEMY_DATABASE_URI):
            create_database(SQLALCHEMY_DATABASE_URI)
        init_db()
    create_server(app)

