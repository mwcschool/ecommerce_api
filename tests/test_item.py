import json
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
from http.client import BAD_REQUEST
from models import Item
import uuid

from .base_test import BaseTest


class TestItems(BaseTest):
    def test_get_items__empty(self):
        resp = self.app.get('/items/')
        assert resp.status_code == OK
        assert json.loads(resp.data.decode()) == []

    def test_get_items(self):
        item1 = self.create_item()
        item2 = self.create_item()

        resp = self.app.get('/items/')
        assert resp.status_code == OK
        assert json.loads(resp.data.decode()) == [item1.json(), item2.json()]

    def test_create_item__success(self):
        user = self.create_user()

        new_item_data = {
            'name': 'Item one',
            'price': 15,
            'description': 'desc1',
            'category': 'poligoni',
            'availability': 11
        }

        resp = self.open_with_auth(
            '/items/', 'post', user.email, 'p4ssw0rd', data=new_item_data)
        assert resp.status_code == CREATED

        item_from_server = json.loads(resp.data.decode())
        item_from_db = Item.get(Item.uuid == item_from_server['uuid']).json()

        assert len(Item.select()) == 1
        assert item_from_db == item_from_server

        item_from_server.pop('uuid')
        assert item_from_server == new_item_data

    def test_create_item__failure_invalid_field_value(self):
        user = self.create_user()
        
        new_item_data = {
            'name': 'Item one',
            'price': 15,
            'description': 'desc1',
            'category': 'poligoni',
            'availability': -8
        }

        resp = self.open_with_auth(
            '/items/', 'post', user.email, 'p4ssw0rd', data=new_item_data)
        assert resp.status_code == BAD_REQUEST

    def test_create_item__failure_empty_field(self):
        user = self.create_user()

        new_item_data = {
            'name': '',
            'price': 10,
            'description': 'Description one',
            'category': 'Category one',
            'availability': 11
        }
        resp = self.open_with_auth(
            '/items/', 'post', user.email, 'p4ssw0rd', data=new_item_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Item.select()) == 0

    def test_create_item__failure_empty_field_only_spaces(self):
        user = self.create_user()

        new_item_data = {
            'name': '    ',
            'price': 5,
            'description': 'desc1',
            'category': 'varie',
            'availability': 11
        }
        resp = self.open_with_auth(
            '/items/', 'post', user.email, 'p4ssw0rd', data=new_item_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Item.select()) == 0

    def test_create_item__failure_missing_field(self):
        user = self.create_user()

        new_item_data = {
            'name': 'Item one',
            'description': 'Description one'
        }
        resp = self.open_with_auth(
            '/items/', 'post', user.email, 'p4ssw0rd', data=new_item_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Item.select()) == 0

    def test_create_item__failure_field_wrong_type(self):
        user = self.create_user()

        new_item_data = {
            'name': 'Item one',
            'price': 'Ten',
            'description': 'Description one',
            'category': 'Category one',
            'availability': 11
        }
        resp = self.open_with_auth(
            '/items/', 'post', user.email, 'p4ssw0rd', data=new_item_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Item.select()) == 0

    def test_get__item(self):
        item1 = self.create_item()

        resp = self.app.get('/items/{}'.format(item1.uuid))
        assert resp.status_code == OK

        item_from_server = json.loads(resp.data.decode())
        assert item_from_server == item1.json()

    def test_get_item__empty(self):
        resp = self.app.get('/items/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_get_item__failure_non_existing_item(self):
        Item.create(
            uuid=uuid.uuid4(),
            name='Item one',
            price=5,
            description='Description one',
            category='Category one',
            availability=11
        )

        resp = self.app.get('/items/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_delete_item__success(self):
        user = self.create_user()
        item1 = self.create_item()

        resp = self.open_with_auth(
            'items/{}'.format(item1.uuid), 'delete', user.email, 'p4ssw0rd', data='')
        assert resp.status_code == NO_CONTENT
        assert len(Item.select()) == 0
        resp = self.app.get('/items/{}'.format(item1.uuid))
        assert resp.status_code == NOT_FOUND

    def test_delete_item__failure_not_found(self):
        user = self.create_user()
        self.create_item()

        resp = self.open_with_auth(
            'items/{}'.format(uuid.uuid4()), 'delete', user.email, 'p4ssw0rd', data='')
        assert resp.status_code == NOT_FOUND
        assert len(Item.select()) == 1

    def test_delete_item__failure_non_existing_empty_items(self):
        user = self.create_user()

        resp = self.open_with_auth(
            'items/{}'.format(uuid.uuid4()), 'delete', user.email, 'p4ssw0rd', data='')
        assert resp.status_code == NOT_FOUND

    def test_modify_item__success(self):
        user = self.create_user()
        static_id = uuid.uuid4()

        Item.create(
            uuid=static_id,
            name='Item one',
            price=5,
            description='Description one',
            category='Category one',
            availability=11
        )

        new_item_data = {
            'name': 'Item one',
            'price': 10,
            'description': 'Descrizione sensata',
            'category': 'Poligoni',
            'availability': 0
        }

        resp = self.open_with_auth(
            'items/{}'.format(static_id), 'put', user.email, 'p4ssw0rd', data=new_item_data)
        assert resp.status_code == OK

        item_from_server = json.loads(resp.data.decode())
        item_from_db = Item.get(Item.uuid == item_from_server['uuid']).json()

        assert item_from_db == item_from_server

        item_from_server.pop('uuid')
        assert new_item_data == item_from_server

    def test_modify_item__failure_invalid_field_value(self):
        static_id = uuid.uuid4()
        user = self.create_user()

        Item.create(
            uuid=static_id,
            name='Item one',
            price=5,
            description='Description one',
            category='Category one',
            availability=11
        )

        new_item_data = {
            'name': 'Item one',
            'price': 10,
            'description': 'Descrizione sensata',
            'category': 'Poligoni',
            'availability': -8
        }

        resp = self.open_with_auth(
            '/items/{}'.format(static_id), 'put', user.email, 'p4ssw0rd', data=new_item_data)
        assert resp.status_code == BAD_REQUEST

    def test_modify_item__failure_empty_field_only_spaces(self):
        user = self.create_user()

        item = Item.create(
            uuid=uuid.uuid4(),
            name='Item one',
            price=5,
            description='Description one',
            category='Category one',
            availability=11
        )

        modified_content = {
            'name': '      ',
            'price': 10,
            'description': 'Description two',
            'category': 'Category two',
            'availability': 11
        }

        resp = self.open_with_auth(
            'items/{}'.format(item.uuid), 'put', user.email, 'p4ssw0rd', data=modified_content)
        item_from_db = Item.get(Item.uuid == item.uuid).json()
        assert item.json() == item_from_db
        assert resp.status_code == BAD_REQUEST

    def test_modify_item__failure_missing_argument(self):
        user = self.create_user()

        item = Item.create(
            uuid=uuid.uuid4(),
            name='Item one',
            price=5,
            description='Description one',
            category='Category one',
            availability=11
        )

        modified_content = {
            'name': 'Item two',
            'price': 10,
            'description': 'Description two'
        }

        resp = self.open_with_auth(
            'items/{}'.format(item.uuid), 'put', user.email, 'p4ssw0rd', data=modified_content)
        item_from_db = Item.get(Item.uuid == item.uuid).json()
        assert item.json() == item_from_db
        assert resp.status_code == BAD_REQUEST

    def test_modify_item__failure_field_wrong_type(self):
        user = self.create_user()
        item = Item.create(
            uuid=uuid.uuid4(),
            name='Item one',
            price=5,
            description='Description one',
            category='Category one',
            availability=11
        )

        modified_content = {
            'name': 'Item one',
            'price': 'Ten',
            'description': 'Description two',
            'category': 'Category two',
            'availability': 6
        }
        resp = self.open_with_auth(
            'items/{}'.format(item.uuid), 'put', user.email, 'p4ssw0rd', data=modified_content)
        assert resp.status_code == BAD_REQUEST

        item_from_db = Item.get(uuid=item.uuid).json()
        assert item.json() == item_from_db
