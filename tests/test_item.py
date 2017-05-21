import json
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
    @classmethod
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

    def test_get_items(self):
        item1 = Item.create(
            uuid=str(uuid.uuid4()),
            name='Item one',
            price=5,
            description='Description one',
            category='Category one'
        )

        item2 = Item.create(
            uuid=str(uuid.uuid4()),
            name='Item two',
            price=15,
            description='Description two',
            category='Category two'
        )

        resp = self.app.get('/items/')
        assert resp.status_code == OK
        assert json.loads(resp.data.decode()) == [item1.json(), item2.json()]

    def test_create_item__success(self):
        new_item_data = {
            'name': 'Item one',
            'price': 15,
            'description': 'Description one',
            'category': 'Category one'
        }

        resp = self.app.post('/items/', data=new_item_data)
        assert resp.status_code == CREATED

        item_from_server = json.loads(resp.data.decode())
        item_from_db = Item.get(Item.item_id == item_from_server['item_id']).json()

        assert len(Item.select()) == 1
        assert item_from_db == item_from_server

        item_from_server.pop('item_id')
        assert item_from_server == new_item_data

    def test_create_item__failure_empty_field(self):
        new_item_data = {
            'name': '',
            'price': 10,
            'description': 'Description one',
            'category': 'Category one'
        }
        resp = self.app.post('/items/', data=new_item_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Item.select()) == 0

    def test_create_item__failure_empty_field_only_spaces(self):
        new_item_data = {
            'name': '    ',
            'price': 10,
            'description': 'Description one',
            'category': 'Category one'
        }
        resp = self.app.post('/items/', data=new_item_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Item.select()) == 0

    def test_create_item__failure_missing_field(self):
        new_item_data = {
            'name': 'Item one',
            'description': 'Description one'
        }
        resp = self.app.post('/items/', data=new_item_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Item.select()) == 0

    def test_create_item__failure_field_wrong_type(self):
        new_item_data = {
            'name': 'Item one',
            'price': 'Ten',
            'description': 'Description one',
            'category': 'Category one'
        }
        resp = self.app.post('/items/', data=new_item_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Item.select()) == 0

    def test_get__item(self):
        item1 = Item.create(
            uuid=str(uuid.uuid4()),
            name='Item one',
            price=5,
            description='Description one',
            category='Category one'
        )

        resp = self.app.get('/item/{}'.format(item1.uuid))
        assert resp.status_code == OK

        item_from_server = json.loads(resp.data.decode())
        assert item_from_server == item1.json()

    def test_get_item__empty(self):
        resp = self.app.get('/item/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND

    def test_get_item__failure_non_existing_item(self):
        item1 = Item.create(
            item_id=str(uuid.uuid4()),
            name='Item one',
            price=5,
            description='Description one',
            category='Category one'
        )

        resp = self.app.get('/item/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND

    def test_delete_item__success(self):
        item1 = Item.create(
            uuid=str(uuid.uuid4()),
            name='Item one',
            price=5,
            description='Descripion one',
            category='Category one'
        )

        resp = self.app.delete('item/{}'.format(item1.uuid))
        assert resp.status_code == NO_CONTENT
        assert len(Item.select()) == 0
        resp = self.app.get('item/{}'.format(item1.uuid))
        assert resp.status_code == NOT_FOUND

    def test_delete_item__failure_not_found(self):
        Item.create(
            uuid=str(uuid.uuid4()),
            name='Item one',
            price=5,
            description='Description one',
            category='Category one'
        )

        resp = self.app.delete('item/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND
        assert len(Item.select()) == 1

    def test_delete_item__failure_non_existing_empty_items(self):
        resp = self.app.delete('item/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND

    def test_modify_item__success(self):
        static_id = str(uuid.uuid4())

        Item.create(
            uuid=static_id,
            name='Item one',
            price=5,
            description='Description one',
            category='Category one'
        )

        new_item_data = {
            'name': 'Item one',
            'price': 10,
            'description': 'Description two',
            'category': 'Category two'
        }

        resp = self.app.put('item/{}'.format(static_id), data=new_item_data)
        assert resp.status_code == OK

        item_from_server = json.loads(resp.data.decode())
        item_from_db = Item.get(Item.item_id == item_from_server['item_id']).json()

        assert item_from_db == item_from_server

        item_from_server.pop('item_id')
        assert new_item_data == item_from_server

    def test_modify_item__failure_empty_field_only_spaces(self):
        item = Item.create(
            uuid=str(uuid.uuid4()),
            name='Item one',
            price=5,
            description='Description one',
            category='Category one'
        )

        modified_content = {
            'name': '      ',
            'price': 10,
            'description': 'Description two',
            'category': 'Category two'
        }

        resp = self.app.put('/item/{}'.format(item.uuid), data=modified_content)
        item_from_db = Item.get(Item.item_id == item.uuid).json()
        assert item.json() == item_from_db
        assert resp.status_code == BAD_REQUEST

    def test_modify_item__failure_missing_argument(self):
        item = Item.create(
            uuid=str(uuid.uuid4()),
            name='Item one',
            price=5,
            description='Description one',
            category='Category one'
        )

        modified_content = {
            'name': 'Item two',
            'price': 10,
            'description': 'Description two'
        }

        resp = self.app.put('/item/{}'.format(item.uuid), data=modified_content)
        item_from_db = Item.get(Item.item_id == item.uuid).json()
        assert item.json() == item_from_db
        assert resp.status_code == BAD_REQUEST

    def test_modufy_item__failure_field_wrong_type(self):
        item = Item.create(
            uuid=str(uuid.uuid4()),
            name='Item one',
            price=5,
            description='Description one',
            category='Category one'
        )

        modified_content = {
            'name': 'Item one',
            'price': 'Ten',
            'description': 'Description two',
            'category': 'Category two'
        }
        resp = self.app.put('/item/{}'.format(item.item_id), data=modified_content)
        assert resp.status_code == BAD_REQUEST

        output_from_DB = Item.get(uuid=item.uuid).json()
        assert item.json() == output_from_DB
