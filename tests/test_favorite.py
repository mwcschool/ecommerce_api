import json
from http.client import OK
from http.client import NOT_FOUND
from http.client import CREATED
from http.client import BAD_REQUEST
from http.client import NO_CONTENT
from models import Item, User, Favorites
import uuid

from .base_test import BaseTest


class TestFavorites(BaseTest):
    def test_get__favorites(self):
        user_db = self.create_user()
        item_db = self.create_item()

        Favorites.create(
            uuid=uuid.uuid4(),
            user=user_db,
            item=item_db
        )

        resp = self.open_with_auth(
            '/favorites/', 'get', user_db.email, "p4ssw0rd", data=None)

        assert resp.status_code == OK
        data = json.loads(resp.data.decode())
        assert len(data) == 1
        assert user_db.favorite_items() == data

    def test_get__favorites_is_empty(self):
        user_db = self.create_user()
        self.create_item()

        resp = self.open_with_auth(
            '/favorites/', 'get', user_db.email, "p4ssw0rd", data=None)

        assert resp.status_code == OK
        data = json.loads(resp.data.decode())
        assert len(data) == 0
        assert user_db.favorite_items() == []

    def test_post__create_favorite_success(self):
        user_db = self.create_user()
        item_db = self.create_item()

        sample_favorite = {
            'id_item': item_db.uuid
        }

        resp = self.open_with_auth(
            '/favorites/', 'post', user_db.email, "p4ssw0rd", data=sample_favorite)
        assert resp.status_code == CREATED
        assert Favorites.count() == 1

    def test_post__failed_item_uuid_not_valid(self):
        user_db = self.create_user()

        sample_favorite = {
            'id_item': 123123
        }

        resp = self.open_with_auth(
            '/favorites/', 'post', user_db.email, "p4ssw0rd", data=sample_favorite)
        assert resp.status_code == BAD_REQUEST
        assert Favorites.count() == 0

    def test_post__failed_item_does_not_exists(self):
        user_db = self.create_user()
        self.create_item()

        sample_favorite = {
            'id_item': uuid.uuid4()
        }

        resp = self.open_with_auth(
            '/favorites/', 'post', user_db.email, "p4ssw0rd", data=sample_favorite)
        assert resp.status_code == BAD_REQUEST
        data = json.loads(resp.data.decode())
        assert not data
        assert Favorites.count() == 0

    def test_delete__favorite_success(self):
        user_db = self.create_user()
        item_db_1 = self.create_item()
        item_db_2 = self.create_item()

        Favorites.create(
            uuid=uuid.uuid4(),
            user=User.get(User.uuid == user_db.uuid),
            item=Item.get(Item.uuid == item_db_1.uuid),
        )

        Favorites.create(
            uuid=uuid.uuid4(),
            user=User.get(User.uuid == user_db.uuid),
            item=Item.get(Item.uuid == item_db_2.uuid),
        )

        resp = self.open_with_auth(
            '/favorites/{}'.format(item_db_1.uuid), 'delete', user_db.email, "p4ssw0rd", data=None)
        assert Favorites.count() == 1
        assert Favorites.item == item_db_2
        assert resp.status_code == NO_CONTENT

    def test_delete__failed_item_not_found(self):
        user_db = self.create_user()
        item_db = self.create_item()

        Favorites.create(
            uuid=uuid.uuid4(),
            user=User.get(User.uuid == user_db.uuid),
            item=Item.get(Item.uuid == item_db.uuid),
        )

        resp = self.open_with_auth(
            '/favorites/{}'.format(uuid.uuid4()), 'delete', user_db.email, "p4ssw0rd", data=None)

        assert Favorites.count() == 1
        assert Favorites.item == item_db.uuid
        assert resp.status_code == NOT_FOUND
        data = json.loads(resp.data.decode())
        assert not data

    def test_delete__failed_user_has_no_favorite_items(self):
        user_db_1 = self.create_user(email="tizio@tizio.it")
        user_db_2 = self.create_user(email="caio@caio.it")
        item_db = self.create_item()

        Favorites.create(
            uuid=uuid.uuid4(),
            user=User.get(User.uuid == user_db_2.uuid),
            item=Item.get(Item.uuid == item_db.uuid),
        )

        resp = self.open_with_auth(
            '/favorites/{}'.format(item_db.uuid), 'delete', user_db_1.email, "p4ssw0rd", data=None)

        assert Favorites.count() == 1
        assert Favorites.item == item_db
        assert resp.status_code == NOT_FOUND
        data = json.loads(resp.data.decode())
        assert not data

    def test_delete__database_has_no_favorites(self):
        user_db = self.create_user()
        item_db = self.create_item()

        resp = self.open_with_auth(
            '/favorites/{}'.format(item_db.uuid), 'delete', user_db.email, "p4ssw0rd", data=None)

        assert Favorites.count() == 0
        assert resp.status_code == NOT_FOUND
        data = json.loads(resp.data.decode())
        assert not data
