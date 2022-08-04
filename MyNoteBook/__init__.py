from genericpath import exists
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from os import path


db = SQLAlchemy()
DB_NAME = "Database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "sdfjhsdklfjolkjfwelkfj"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    from routes import routes
    app.register_blueprint(routes)
    from models import User, Note, Trash
    create_database(app)
    return app

def create_database(app):
    if not path.exists('Note_app/' + DB_NAME):
        db.create_all(app=app)
        
