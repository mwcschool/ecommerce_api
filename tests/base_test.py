from models import Item, User, Address, Order, OrderItem
from peewee import SqliteDatabase
from app import app
import uuid


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

    def create_user(first_name="First Name", last_name="Last name",
                    email="email@domain.com", password="p4ssw0rd"):
        return User.create(
            user_id=str(uuid.uuid4()),
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )

    def create_item(name="Item name", price=7, description="Item description", category="Category"):
        return Item.create(
            item_id=str(uuid.uuid4()),
            name=name,
            price=price,
            description=description,
            category=category,
        )
