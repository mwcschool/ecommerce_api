import flask as f
import flask_restful as rest
import json
import peewee as p
from peewee import SqliteDatabase
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
from http.client import BAD_REQUEST
from models import Item
from app import app
import uuid


class TestItems:
    def setup_class(cls):
        Item._meta.database = SqliteDatabase(':memory:')
        Item.create_table()
        cls.app = app.test_client()

    def setup_method(self):
        Item.delete().execute()

    def test_get_items__empty(self):
        resp = self.app.get('/items/')
        assert resp.status_code == OK
        assert json.loads(resp.data.decode()) == []

    def test_get_items__not_empty(self):
        obj1 = Item.create(
            item_id=uuid.uuid4(),
            name='cubo',
            price=5,
            description='dhfsdjòfgjasdògj'
        )

        obj2 = Item.create(
            item_id=uuid.uuid4(),
            name='cubo',
            price=15,
            description='desc2'
        )

        resp = self.app.get('/items/')
        assert resp.status_code == OK
        assert json.loads(resp.data.decode()) == [obj1.json(), obj2.json()]

    def test_post_create_item__success(self):
        source_item = {
            'name': 'cubo',
            'price': 15,
            'description': 'desc1'
        }

        resp = self.app.post('/items/', data=source_item)
        assert resp.status_code == CREATED
        resp2 = self.app.get('/items/')

        db_data = {
            'name': json.loads(resp2.data.decode())[0]['name'],
            'price': json.loads(resp2.data.decode())[0]['price'],
            'description': json.loads(resp2.data.decode())[0]['description']
        }

        assert source_item == db_data

    def test_post__malformed_input_type(self):
        source_item = {
            'name': 'cubo',
            'price': 'banana',
            'description': 'desc1'
        }

        source_item_2 = {
            'name': 'rombo',
            'description': 'desc2'
        }
        resp = self.app.post('/items/', data=source_item)
        assert resp.status_code == BAD_REQUEST
        resp = self.app.post('/items/', data=source_item_2)
        assert resp.status_code == BAD_REQUEST

    def test_get_item__find(self):
        obj1 = Item.create(
            item_id=uuid.uuid4(),
            name='cubo',
            price=5,
            description='dhfsdjòfgjasdògj'
        )

        resp = self.app.get('/item/{}'.format(obj1.json()['item_id']))
        assert resp.status_code == OK

    def test_get_item__not_found(self):

        resp = self.app.get('/item/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND
