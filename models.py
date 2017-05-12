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

    def json(self):
        return {
            'user_id': str(self.user_id)
        }


class Address(BaseModel):
    address_id = UUIDField(unique=True)
    user = ForeignKeyField(User, related_name="address")
    nation = CharField()
    city = CharField()
    postal_code = CharField()
    local_address = CharField()
    phone = CharField()

    def json(self):
        return {
        'address_id': self.address_id,
        'user': self.user,
        'nation': self.nation,
        'city': self.city,
        'postal_code': self.postal_code,
        'local_address': self.local_address,
        'phone': self.phone
        }


class Order(BaseModel):
    order_id = UUIDField(unique=True)
    total_price = DecimalField()
    user = ForeignKeyField(User, related_name="orders")

class OrderItem(BaseModel):
    order = ForeignKeyField(Order)
    item = ForeignKeyField(Item)
    quantity = IntegerField()
    subtotal = DecimalField()
