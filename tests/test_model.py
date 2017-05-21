import json
from http.client import OK
from http.client import NOT_FOUND
from http.client import CREATED
from http.client import BAD_REQUEST
from http.client import NO_CONTENT
from peewee import SqliteDatabase
from models import Item, User, Favorites
from app import app
import uuid

def create_an_user(id_user, number):
    return User.create(
        user_id=id_user,
        first_name='{}{}'.format('first_name_', number),
        last_name='{}{}'.format('last_name_', number),
        email='{}{}'.format('email_', number),
        password='{}{}'.format('password_', number),
    )


def create_an_item(id_item, number):
    return Item.create(
        item_id=id_item,
        name='{}{}'.format('name_', number),
        price=number,
        description='{}{}'.format('description_', number),
    )

class TestModel:
    @classmethod
    def setup_class(cls):
        db = SqliteDatabase(':memory:')
        tables = [Favorites, Item, User]
        for table in tables:
            table._meta.database = db
            table.create_table()

        cls.app = app.test_client()

    def setup_method(self):
        Item.delete().execute()
        Favorites.delete().execute()
        User.delete().execute()

    def user_add_favorite__success(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        user = create_an_user(id_user, 1)
        item = create_an_item(id_item, 1)

        User.add_favorite(Item.get())

        assert Favorites.row_count() == 1
        assert Favorites.item == item
        assert Favorites.user == user
