from models import Item, User, Address, Order, OrderItem
from peewee import SqliteDatabase
from app import app


class BaseTest:
    @classmethod
    def setup_class(cls):
        database = SqliteDatabase(':memory:')

        tables = [Item, User, Address, Order, OrderItem]
        for table in tables:
            table._meta.database = database
            table.create_table()

        app.config['TESTING'] = True
        cls.app = app.test_client()
