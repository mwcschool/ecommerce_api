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
            'uuid': str(self.uuid),
            'name': self.name,
            'price': int(self.price),
            'description': self.description,
            'category': self.category
        }


class User(BaseModel):
    uuid = UUIDField(unique=True)
    first_name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField()

    def json(self):
        return {
            'user_id': str(self.uuid)
        }

    def verify_password(self, origin_password):
        return pbkdf2_sha256.verify(origin_password, self.password)


class Address(BaseModel):
    uuid = UUIDField(unique=True)
    user = ForeignKeyField(User, related_name="address")
    nation = CharField()
    city = CharField()
    postal_code = CharField()
    local_address = CharField()
    phone = CharField()

    def json(self):
        return {
            'uuid': str(self.uuid),
            'user': str(self.user.uuid),
            'nation': self.nation,
            'city': self.city,
            'postal_code': self.postal_code,
            'local_address': self.local_address,
            'phone': self.phone
        }


class Order(BaseModel):
    uuid = UUIDField(unique=True)
    total_price = DecimalField()
    user = ForeignKeyField(User, related_name="orders")

    def json(self):
        return {
            'uuid': str(self.uuid),
            'total_price': float(self.total_price),
            'user': str(self.user.uuid),
            'items': self._get_order_items()
        }

    def _get_order_items(self):
        data = []
        for order_item in self.order_items:
            item = order_item.item
            data.append({
                'uuid': str(item.uuid),
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
