from http.client import CREATED, NO_CONTENT, NOT_FOUND, BAD_REQUEST
import json
import uuid
from peewee import SqliteDatabase
from models import User, Address
from app import app


class TestAddress:
    @classmethod
    def setup_class(cls):
        User._meta.database = SqliteDatabase(':memory:')
        User.create_table()
        Address.create_table()
        cls.app = app.test_client()

    def setup_method(self):
        User.delete().execute()
        Address.delete().execute()
