from peewee import Model, SqliteDatabase, PostgresqlDatabase, Check
from peewee import DecimalField, TextField, CharField
from peewee import UUIDField, ForeignKeyField, IntegerField, BooleanField
from schemas import ItemSchema, UserSchema, AddressSchema
from schemas import OrderSchema, OrderItemSchema, FavoritesSchema
from passlib.hash import pbkdf2_sha256
from jsonschema import validate
from marshmallow_jsonschema import JSONSchema
from urllib.parse import urlparse
import uuid
import os

ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')

database = ''

if ENVIRONMENT == 'dev':
    database = SqliteDatabase('database.db')
else:
    url_db = urlparse(os.getenv('DATABASE_URL'))

    database = PostgresqlDatabase(
        url_db.path[1:],
        user=url_db.username,
        password=url_db.password,
        host=url_db.hostname,
    )


class BaseModel(Model):
    class Meta:
        database = database

    def reload(self):
        cls = type(self)
        return cls.get(cls.id == self.id)

    @classmethod
    def get_schema(cls):
        raise NotImplementedError

    @classmethod
    def verify_json(cls, json):
        schema = cls.get_schema()
        json_schema = JSONSchema().dump(schema).data
        validate(json, json_schema)

    def json(self):
        schema = self.get_schema()
        return schema.dump(self).data

    @classmethod
    def count(cls):
        return cls.select().count()


class Item(BaseModel):
    uuid = UUIDField(unique=True)
    name = CharField()
    price = DecimalField(max_digits=20)
    description = TextField()
    category = CharField()
    availability = IntegerField(constraints=[Check('availability >= 0')])

    @classmethod
    def get_schema(cls):
        return ItemSchema()


class User(BaseModel):
    uuid = UUIDField(unique=True)
    first_name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField()
    superuser = BooleanField(default=False)

    @classmethod
    def get_schema(cls):
        return UserSchema()

    def verify_password(self, origin_password):
        return pbkdf2_sha256.verify(origin_password, self.password)

    def favorite_items(self):
        return [favorite.item.json() for favorite in self.favorites]

    def add_favorite(self, item):
        favorite = Favorites.create(
            uuid=uuid.uuid4(),
            user=self,
            item=item,
        )
        return favorite

    def remove_favorite(self, item):
        Favorites.delete().where(Favorites.item == item, Favorites.user == self).execute()
        return None


class Address(BaseModel):
    uuid = UUIDField(unique=True)
    user = ForeignKeyField(User, related_name="address")
    nation = CharField()
    city = CharField()
    postal_code = CharField()
    local_address = CharField()
    phone = CharField()

    @classmethod
    def get_schema(cls):
        return AddressSchema()


class Order(BaseModel):
    uuid = UUIDField(unique=True)
    total_price = DecimalField(max_digits=20)
    user = ForeignKeyField(User, related_name="orders")

    @classmethod
    def get_schema(cls):
        return OrderSchema()


class OrderItem(BaseModel):
    order = ForeignKeyField(Order, related_name="order_items")
    item = ForeignKeyField(Item)
    quantity = IntegerField()
    subtotal = DecimalField(max_digits=20)

    @classmethod
    def get_schema(cls):
        return OrderItemSchema()


class Picture(BaseModel):
    uuid = UUIDField(unique=True)
    title = CharField()
    extension = CharField()
    item = ForeignKeyField(Item, related_name="pictures")

    def json(self):
        return {
            'uuid': str(self.uuid),
            'title': self.title,
            'extension': self.extension,
        }


class Favorites(BaseModel):
    uuid = UUIDField(unique=True)
    user = ForeignKeyField(User, related_name="favorites")
    item = ForeignKeyField(Item, related_name="favorites")

    @classmethod
    def get_schema(cls):
        return FavoritesSchema()

    def json(self):
        return {
            'uuid': str(self.uuid),
            'user': str(self.user.uuid),
            'item': str(self.item.uuid)
        }
