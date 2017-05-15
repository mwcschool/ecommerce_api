from peewee import Model, SqliteDatabase
from peewee import DecimalField, TextField, CharField
from peewee import UUIDField, ForeignKeyField, IntegerField
from passlib.hash import pbkdf2_sha256

database = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = database


class Item(BaseModel):
    uuid = UUIDField(unique=True)
    name = CharField()
    price = DecimalField()
    description = TextField()
    category = CharField()

    def json(self):
        return {
            'item_id': str(self.uuid),
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
            'uuid': str(self.order_id),
            'total_price': float(self.total_price),
            'user': str(self.user.user_id),
            'items': self._get_order_items()
        }

    def _get_order_items(self):
        data = []
        for order_item in self.order_items:
            item = order_item.item
            data.append({
                'item_id': str(item.item_id),
                'name': item.name,
                'quantity': order_item.quantity,
                'subtotal': float(order_item.subtotal)
            })
        return data


class OrderItem(BaseModel):
    order = ForeignKeyField(Order, related_name="order_items")
    item = ForeignKeyField(Item)
    quantity = IntegerField()
    subtotal = DecimalField()
