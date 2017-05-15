import json
from http.client import OK
from peewee import SqliteDatabase
from models import Item, User, Favorites
from app import app
import uuid


def create_an_user(id_user, first_name, last_name, email, password):
    return User.create(
        user_id=id_user,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password
    )


def create_an_item(id_item, name, price, description):
    return Item.create(
        item_id=id_item,
        name=name,
        price=price,
        description=description
    )


class TestFavorites:
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

    def test_get__favorites(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        user_db = create_an_user(
            id_user,
            'fname',
            'lname',
            'e@e.com',
            'psw')

        item_db = create_an_item(
            id_item,
            'name',
            '5',
            'desc')

        fav_db = Favorites.create(
            user=user_db,
            item=item_db
        )

        resp = self.app.get('/favorites/')
        assert resp.status_code == OK
        assert resp.data
