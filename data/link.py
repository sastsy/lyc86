from datetime import datetime
import string
from random import choices

import flask_sqlalchemy
from app import db


"""def generate_short_link():
    characters = string.digits + string.ascii_letters
    short_url = ''.join(choices(characters, k=3))

    session = db_session.create_session()

    link = session.query(self).filter_by(short_url=short_url).first()

    if link:
        return self.generate_short_link()

    return short_url"""


class Link(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    original_url = db.Column(db.String(512))
    short_url = db.Column(db.String(3))
    visits = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return f"Link('{self.original_url}', '{self.short_url}', '{self.visits}', '{self.date_created}')"
