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

    def create_user(self, email="email@domain.com", first_name="First Name",
                    last_name="Last name", password="p4ssw0rd"):
        return User.create(
            uuid=uuid.uuid4(),
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )

    def create_item(self, name="Item name", price=7,
                    description="Item description", category="Category"):
        return Item.create(
            uuid=uuid.uuid4(),
            name=name,
            price=price,
            description=description,
            category=category,
        )

    def create_order(self, user=None, items=None):
        '''Parameter format:

        items = [
            [Instance of Item, quantity],
            ...
            [instance of item, quantity]
        ]

        user = Instance of User
        '''
        if not user:
            user = self.create_user()

        if not items:
            items = []
            for i in range(2):
                item = self.create_item()
                items.append([item, i + 1])

        total_price = 0

        for item in items:
            total_price = float(item[0].price * item[1])

        order = Order.create(
            uuid=uuid.uuid4(),
            total_price=total_price,
            user=user.id
        )

        for item in items:
            item_quantity = item[1]
            item = item[0]

            OrderItem.create(
                order=order.id,
                item=item.id,
                quantity=item_quantity,
                subtotal=float(item.price * item_quantity)
            )

        return order
