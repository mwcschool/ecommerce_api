import pytest
import uuid
import json
from peewee import SqliteDatabase
from http.client import OK, NOT_FOUND, NO_CONTENT, CREATED

from app import app
from models import Order 

class TestOrders:
	@classmethod
	def setup_class(cls):
		Order._meta.database = SqliteDatabase(':memory:')
		Order.create_table()
		app.config['TESTING'] = True
		cls.app = app.test_client()

	def setup_method(self):
		Order.delete().execute()

	def test_get_orders__empty(self):
		resp = self.app.get('/orders/')
		assert resp.status_code == 	OK
		assert json.loads(resp.data.decode()) == []
