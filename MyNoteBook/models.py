from __init__ import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.String(150), primary_key=True)
    password = db.Column(db.String(150), nullable=False)
    notes = db.relationship('Note')
    trashes = db.relationship('Trash')

class Note(db.Model):
    id = db.Column(db.String(150), primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.String(150), db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.String(10000))

class Trash(db.Model):
    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.String(150), db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.String(10000))
