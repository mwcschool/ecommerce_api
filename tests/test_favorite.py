import json
from http.client import OK
from http.client import NOT_FOUND
from http.client import CREATED
from http.client import BAD_REQUEST
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
            1)

        item_db = create_an_item(
            id_item,
            1)

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

        user = create_an_user(id_user, 1)

        item = create_an_item(id_item, 1)

        sample_favorite = {
            'id_user': id_user,
            'id_item': id_item
        }

        resp = self.app.post('/favorites/', data=sample_favorite)
        assert resp.status_code == CREATED
        assert Favorites.row_count() == 1

    def test_post__failed_item_do_not_exist(self):
        id_user = uuid.uuid4()

        user = create_an_user(id_user, 1)

        item = create_an_item(uuid.uuid4(), 1)

        sample_favorite = {
            'id_user': id_user,
            'id_item': uuid.uuid4()
        }

        resp = self.app.post('/favorites/', data=sample_favorite)

        assert resp.status_code == NOT_FOUND
        assert Favorites.row_count() == 0

    def test_post__failed_uuid_not_valid(self):
        sample_favorite = {
            'id_user':  "Stringa di prova",
            'id_item': 123123
        }
        resp = self.app.post('/favorites/', data=sample_favorite)
        assert resp.status_code == BAD_REQUEST
        assert Favorites.row_count() == 0

    def test_post__failed_item_uuid_does_not_exists(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        user = create_an_user(id_user, 1)

        item = create_an_item(id_item, 1)

        sample_favorite = {
            'id_user': id_user,
            'id_item': uuid.uuid4()
        }

        resp = self.app.post('/favorites/', data=sample_favorite)
        assert resp.status_code == NOT_FOUND
        assert json.loads(resp.data.decode()) == None
        assert Favorites.row_count() == 0

    def test_post__failed_user_uuid_does_not_exists(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        user = create_an_user(id_user, 1)

        item = create_an_item(id_item, 1)

        sample_favorite = {
            'id_user': uuid.uuid4(),
            'id_item': id_item
        }

        resp = self.app.post('/favorites/', data=sample_favorite)
        assert resp.status_code == NOT_FOUND
        assert json.loads(resp.data.decode()) == None
        assert Favorites.row_count() == 0
