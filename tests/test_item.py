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


def number_of_rows_in_DB():
    return len(Item.select())


class TestItems:
    def setup_class(cls):
        Item._meta.database = SqliteDatabase(':memory:')
        Item.create_table()
        cls.app = app.test_client()

    def setup_method(self):
        Item.delete().execute()

    def test_get__database_empty(self):
        resp = self.app.get('/items/')
        assert resp.status_code == OK
        assert json.loads(resp.data.decode()) == []

    def test_get__database_not_empty(self):
        obj1 = Item.create(
            uuid=uuid.uuid4(),
            name='cubo',
            price=5,
            description='dhfsdjòfgjasdògj',
            category='poligoni'
        )

        obj2 = Item.create(
            uuid=uuid.uuid4(),
            name='iphone',
            price=15,
            description='desc2',
            category='smartphone'
        )

        resp = self.app.get('/items/')
        assert resp.status_code == OK
        assert json.loads(resp.data.decode()) == [obj1.json(), obj2.json()]

    def test_post__create_item_success(self):
        source_item = {
            'name': 'cubo',
            'price': 15,
            'description': 'desc1',
            'category': 'poligoni'
        }

        resp = self.app.post('/items/', data=source_item)
        assert resp.status_code == CREATED

        select_query_db = Item.select()

        assert len(select_query_db) == 1

        item_from_db = select_query_db[0].json()
        assert item_from_db == json.loads(resp.data.decode())

    def test_post__name_with_only_spaces(self):
        source_item = {
            'name': '    ',
            'price': 123,
            'description': 'desc1',
            'category': 'varie'
        }
        resp = self.app.post('/items/', data=source_item)
        assert resp.status_code == BAD_REQUEST
        assert number_of_rows_in_DB() == 0

    def test_post__item_without_arguments_given(self):
        source_item = {
            'name': 'rombo',
            'description': 'desc2'
        }
        resp = self.app.post('/items/', data=source_item)
        assert resp.status_code == BAD_REQUEST
        assert number_of_rows_in_DB() == 0

    def test_post__price_value_as_a_string(self):
        source_item = {
            'name': 'ciao',
            'price': 'stringa',
            'description': 'desc3',
            'category': 'varie'
        }
        resp = self.app.post('/items/', data=source_item)
        assert resp.status_code == BAD_REQUEST
        assert number_of_rows_in_DB() == 0

    def test_get__item_found(self):
        obj1 = Item.create(
            item_id=uuid.uuid4(),
            name='cubo',
            price=5,
            description='dhfsdjofgjasdogj',
            category='poligoni'
        )

        resp = self.app.get('/item/{}'.format(obj1.item_id))
        assert resp.status_code == OK

        item = json.loads(resp.data.decode())
        assert item == obj1.json()

    def test_get__item_not_found(self):

        resp = self.app.get('/item/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_delete__item_removed_successfully(self):
        obj1 = Item.create(
            uuid=uuid.uuid4(),
            name='cubo',
            price=5,
            description='dhfsdjòfgjasdògj',
            category='poligoni'
        )

        resp = self.app.delete('item/{}'.format(obj1.uuid))
        assert resp.status_code == NO_CONTENT
        assert number_of_rows_in_DB() == 0
        resp = self.app.get('item/{}'.format(obj1.uuid))
        assert resp.status_code == NOT_FOUND

    def test_delete__item_not_found(self):
        Item.create(
            item_id=uuid.uuid4(),
            name='cubo',
            price=5,
            description='dhfsdjòfgjasdògj',
            category='poligoni'
        )

        resp = self.app.delete('item/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_delete__database_is_empty(self):
        resp = self.app.delete('item/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_post__item_modified_successfully(self):
        static_id = uuid.uuid4()

        Item.create(
            item_id=static_id,
            name='cubo',
            price=5,
            description='dhfsdjòfgjasdògj',
            category='poligoni'
        )

        obj2 = {
            'name': 'triangolo',
            'price': 10,
            'description': 'Descrizione sensata',
            'category': 'Poligoni'
        }

        resp = self.app.put('item/{}'.format(static_id), data=obj2)
        assert resp.status_code == OK
        resp = self.app.get('item/{}'.format(static_id))

        db_data = {
            'name': json.loads(resp.data.decode())['name'],
            'price': json.loads(resp.data.decode())['price'],
            'description': json.loads(resp.data.decode())['description'],
            'category': json.loads(resp.data.decode())['category']
        }

        assert obj2 == db_data

    def test_put__item_name_with_only_spaces(self):
        static_id = uuid.uuid4()

        obj = Item.create(
            item_id=static_id,
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
        output_from_DB = Item.get(item_id=obj.item_id).json()
        assert obj.json() == output_from_DB
        assert resp.status_code == BAD_REQUEST

    def test_put__item_without_an_argument_given(self):
        static_id = uuid.uuid4()

        obj = Item.create(
            item_id=static_id,
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
        output_from_DB = Item.get(item_id=obj.item_id).json()
        assert obj.json() == output_from_DB
        assert resp.status_code == BAD_REQUEST

    def test_put__item_price_value_as_a_string(self):
        static_id = uuid.uuid4()

        obj = Item.create(
            item_id=static_id,
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
        output_from_DB = Item.get(item_id=obj.item_id).json()
        assert obj.json() == output_from_DB
