from peewee import Model, SqliteDatabase
from peewee import DecimalField, TextField, CharField
from peewee import UUIDField, ForeignKeyField, IntegerField
from passlib.hash import pbkdf2_sha256

database = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = database


class Item(BaseModel):
    item_id = UUIDField(unique=True)
    name = CharField()
    price = DecimalField()
    description = TextField()
    category = CharField()

    def json(self):
        return {
            'item_id': str(self.item_id),
            'name': self.name,
            'price': int(self.price),
            'description': self.description,
            'category': self.category
        }


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

    def verify_password(self, origin_password):
        return pbkdf2_sha256.verify(origin_password, self.password)


class Address(BaseModel):
    user = ForeignKeyField(User, related_name="address")
    nation = CharField()
    city = CharField()
    postal_code = CharField()
    local_address = CharField()
    phone = CharField()


class Order(BaseModel):
    order_id = UUIDField(unique=True)
    total_price = DecimalField()
    user = ForeignKeyField(User, related_name="orders")

    def json(self):
        return {
            'order_id': str(self.order_id),
            'total_price': self.total_price,
            'user': self.user
        }


class OrderItem(BaseModel):
    order = ForeignKeyField(Order)
    item = ForeignKeyField(Item)
    quantity = IntegerField()
    subtotal = DecimalField()
