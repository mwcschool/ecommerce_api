import json
from http.client import OK
from http.client import NOT_FOUND
from http.client import CREATED
from http.client import BAD_REQUEST
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
        assert len(json.loads(resp.data.decode())) == 1
        assert user_db.get_favorite_items() == json.loads(resp.data.decode())

    def test_get__favorites_empty(self):
        resp = self.app.get('/favorites/')
        assert json.loads(resp.data.decode()) == None
        assert resp.status_code == NOT_FOUND

    def test_post__create_favorite_success(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        user = create_an_user(
            id_user,
            'first_name',
            'last_name',
            'email@email.com',
            'password'
        )

        item = create_an_item(
            id_item,
            'item_name',
            100,
            'description'
        )

        sample_favorite = {
            'id_user': id_user,
            'id_item': id_item
        }

        resp = self.app.post('/favorites/', data=sample_favorite)
        assert resp.status_code == CREATED
        assert Favorites.row_count() == 1

    def test_post__failed_uuid_not_valid(self):
        sample_favorite = {
            'id_user':  "Stringa di prova",
            'id_item': 123123
        }
        resp = self.app.post('/favorites/', data=sample_favorite)
        assert resp.status_code == BAD_REQUEST
        assert Favorites.row_count() == 0

    def test_post__failed_uuids_does_not_exists(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        user = create_an_user(
            id_user,
            'first_name',
            'last_name',
            'email@email.com',
            'password'
        )

        item = create_an_item(
            id_item,
            'item_name',
            100,
            'description'
        )

        sample_favorite = {
            'id_user': uuid.uuid4(),
            'id_item': uuid.uuid4()
        }

        resp = self.app.post('/favorites/', data=sample_favorite)
        assert resp.status_code == NOT_FOUND
        assert json.loads(resp.data.decode()) == None
        assert Favorites.row_count() == 0
