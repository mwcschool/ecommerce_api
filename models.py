from peewee import Model, SqliteDatabase, Check
from peewee import DecimalField, TextField, CharField
from peewee import UUIDField, ForeignKeyField, IntegerField, BooleanField
from schemas import ItemSchema, UserSchema, AddressSchema
from passlib.hash import pbkdf2_sha256
import uuid

database = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = database

    def reload(self):
        cls = type(self)
        return cls.get(cls.id == self.id)

    @classmethod
    def get_schema(cls):
        raise NotImplementedError

    def json(self):
        schema = self.get_schema()
        return schema.dump(self).data

    @classmethod
    def count(cls):
        return cls.select().count()


class Item(BaseModel):
    uuid = UUIDField(unique=True)
    name = CharField()
    price = DecimalField()
    description = TextField()
    category = CharField()
    availability = IntegerField(constraints=[Check('availability >= 0')])

    @classmethod
    def get_schema(cls):
        return ItemSchema()

    @classmethod
    def exists_uuid(cls, check_uuid):
        if Item.select().where(Item.uuid == check_uuid).exists():
            return True
        else:
            return False


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
        Favorites.delete().where(Favorites.item == item).where(Favorites.user == self).execute()
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
    total_price = DecimalField()
    user = ForeignKeyField(User, related_name="orders")

    def json(self):
        return {
            'uuid': str(self.uuid),
            'total_price': float(self.total_price),
            'user': str(self.user.uuid),
            'items': self._get_order_items(),
        }

    def _get_order_items(self):
        data = []
        for order_item in self.order_items:
            item = order_item.item
            data.append({
                'uuid': str(item.uuid),
                'name': item.name,
                'quantity': order_item.quantity,
                'subtotal': float(order_item.subtotal),
            })
        return data


class OrderItem(BaseModel):
    order = ForeignKeyField(Order, related_name="order_items")
    item = ForeignKeyField(Item)
    quantity = IntegerField()
    subtotal = DecimalField()


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

    def json(self):
        return {
            'uuid': str(self.uuid),
            'user': str(self.user.uuid),
            'item': str(self.item.uuid)
        }
