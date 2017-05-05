import flask as f
import flask_restful as rest
import json
import peewee as p
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK	
from models import Item
from app import app
import uuid

class TestItems:
	def setup_class(cls):
		Item._meta.database = p.SqliteDatabase(':memory:')
		Item.create_table()
		cls.app = app.test_client()

	def setup_method(self):
		Item.delete().execute()

	def test_get_items_empty(self):
		resp = self.app.get('/items/')
		assert resp.status_code == OK
		assert json.loads(resp.data.decode()) == []

	def test_get_items_not_empty(self):
		obj1 = Item.create(
			item_id = uuid.uuid4(),
			name = 'cubo',
			price = 10,
			description = 'dhfsdjòfgjasdògj'
			)

		obj2 = Item.create(
			item_id = uuid.uuid4(),
			name = 'cubo',
			price = 15,
			description = 'desc2'
			)

		resp = self.app.get('/items/')
		assert resp.status_code == OK
		assert json.loads(resp.data.decode()) == [obj1.json(), obj2.json()]






