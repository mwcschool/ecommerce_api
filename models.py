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


class Order(BaseModel):
    order_id = UUIDField(unique=True)
    total_price = DecimalField()
    user = ForeignKeyField(User, related_name="orders")


class OrderItem(BaseModel):
    order = ForeignKeyField(Order)
    item = ForeignKeyField(Item)
    quantity = IntegerField()
    subtotal = DecimalField()


User.create_table(fail_silently=True)
Item.create_table(fail_silently=True)
Order.create_table(fail_silently=True)
OrderItem.create_table(fail_silently=True)
