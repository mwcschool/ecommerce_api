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

    def test_post__price_value_as_a_string(self):
        new_item_data = {
            'name': 'ciao',
            'price': 'stringa',
            'description': 'desc3',
            'category': 'varie'
        }
        resp = self.app.post('/items/', data=new_item_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Item.select()) == 0

    def test_get__item_found(self):
        item1 = Item.create(
            uuid=str(uuid.uuid4()),
            name='cubo',
            price=5,
            description='dhfsdjofgjasdogj',
            category='poligoni'
        )

        resp = self.app.get('/item/{}'.format(item1.uuid))
        assert resp.status_code == OK

        item = json.loads(resp.data.decode())
        assert item == item1.json()

    def test_get__item_not_found(self):

        resp = self.app.get('/item/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND

    def test_delete__item_removed_successfully(self):
        item1 = Item.create(
            uuid=str(uuid.uuid4()),
            name='cubo',
            price=5,
            description='dhfsdjòfgjasdògj',
            category='poligoni'
        )

        resp = self.app.delete('item/{}'.format(item1.uuid))
        assert resp.status_code == NO_CONTENT
        assert len(Item.select()) == 0
        resp = self.app.get('item/{}'.format(item1.uuid))
        assert resp.status_code == NOT_FOUND

    def test_delete__item_not_found(self):
        Item.create(
            uuid=str(uuid.uuid4()),
            name='cubo',
            price=5,
            description='dhfsdjòfgjasdògj',
            category='poligoni'
        )

        resp = self.app.delete('item/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND

    def test_delete__database_is_empty(self):
        resp = self.app.delete('item/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND

    def test_post__item_modified_successfully(self):
        static_id = str(uuid.uuid4())

        Item.create(
            uuid=static_id,
            name='cubo',
            price=5,
            description='dhfsdjòfgjasdògj',
            category='poligoni'
        )

        item2 = {
            'name': 'triangolo',
            'price': 10,
            'description': 'Descrizione sensata',
            'category': 'Poligoni'
        }

        resp = self.app.put('item/{}'.format(static_id), data=item2)
        assert resp.status_code == OK
        resp = self.app.get('item/{}'.format(static_id))

        db_data = {
            'name': json.loads(resp.data.decode())['name'],
            'price': json.loads(resp.data.decode())['price'],
            'description': json.loads(resp.data.decode())['description'],
            'category': json.loads(resp.data.decode())['category']
        }

        assert item2 == db_data

    def test_put__item_name_with_only_spaces(self):
        static_id = str(uuid.uuid4())

        item = Item.create(
            uuid=uuid.uuid4(),
            name='cubo',
            price=5,
            description='dhfsdjòfgjasdògj',
            category='poligoni'
        )

        modified_content = {
            'name': '      ',
            'price': '123',
            'description': 'desc2',
            'category': '    '
        }

        resp = self.app.put('/item/{}'.format(static_id), data=modified_content)
        output_from_DB = Item.get(uuid=item.uuid).json()
        assert item.json() == output_from_DB
        assert resp.status_code == BAD_REQUEST

    def test_put__item_without_an_argument_given(self):
        static_id = str(uuid.uuid4())

        item = Item.create(
            uuid=uuid.uuid4(),
            name='cubo',
            price=5,
            description='dhfsdjòfgjasdògj',
            category='poligoni'
        )

        modified_content = {
            'name': 'rombo',
            'description': 'desc2'
        }

        resp = self.app.put('/item/{}'.format(static_id), data=modified_content)

        output_from_DB = Item.get(uuid=item.uuid).json()
        assert item.json() == output_from_DB
        assert resp.status_code == BAD_REQUEST

    def test_put__item_price_value_as_a_string(self):
        static_id = str(uuid.uuid4())

        item = Item.create(
            uuid=uuid.uuid4(),
            name='cubo',
            price=5,
            description='dhfsdjòfgjasdògj',
            category='poligoni'
        )

        modified_content = {
            'name': 'rombo',
            'price': 'asdasd',
            'description': 'Ciaociao',
            'category': 'asdfdafdf'
        }
        resp = self.app.put('/item/{}'.format(static_id), data=modified_content)
        assert resp.status_code == BAD_REQUEST

        output_from_DB = Item.get(uuid=item.uuid).json()
        assert item.json() == output_from_DB
