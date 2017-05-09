from peewee import Model, SqliteDatabase
from peewee import DecimalField, TextField, CharField
from peewee import UUIDField, ForeignKeyField, IntegerField

database = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = database


class Item(BaseModel):
    item_id = UUIDField(unique=True)
    name = CharField()
    price = DecimalField()
    description = TextField()


class User(BaseModel):
    user_id = UUIDField(unique=True)
    first_name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField()


class Order(BaseModel):
    order_id = UUIDField(unique=True)
    total_price = DecimalField()
    user = ForeignKeyField(User, related_name="orders")

    def json(self):
        return {
            'order_id': str(self.order_id),
            'total_price': float(self.total_price),
            'user': str(self.user.user_id)
        }


class OrderItem(BaseModel):
    order = ForeignKeyField(Order)
    item = ForeignKeyField(Item)
    quantity = IntegerField()
    subtotal = DecimalField()
