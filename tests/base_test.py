from models import Item, User, Address, Order, OrderItem
from peewee import SqliteDatabase
from app import app


class BaseTest:
    @classmethod
    def setup_class(cls):
        database = SqliteDatabase(':memory:')

        cls.tables = [Item, User, Address, Order, OrderItem]
        for table in cls.tables:
            table._meta.database = database
            table.create_table()

        app.config['TESTING'] = True
        cls.app = app.test_client()

    def setup_method(self):
        for table in self.tables:
            table.delete().execute()
