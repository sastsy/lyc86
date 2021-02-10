import datetime
import flask_sqlalchemy
from main import db
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=True)
    email = db.Column(db.String, index=True, unique=True, nullable=True)
    hashed_password = db.Column(db.String, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    links = db.relationship('Link', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.created_date}')"

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)