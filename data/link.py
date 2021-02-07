from datetime import datetime
import string
from random import choices
import sqlalchemy
from sqlalchemy import orm

from data import db_session
from data.db_session import SqlAlchemyBase


def generate_short_link():
    characters = string.digits + string.ascii_letters
    short_url = ''.join(choices(characters, k=3))

    session = db_session.create_session()

    """link = session.query(self).filter_by(short_url=short_url).first()

    if link:
        return self.generate_short_link()"""

    return short_url


class Link(SqlAlchemyBase):
    __tablename__ = 'link'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    original_url = sqlalchemy.Column(sqlalchemy.String(512))
    short_url = sqlalchemy.Column(sqlalchemy.String(3))
    visits = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    date_created = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.short_url = generate_short_link()
