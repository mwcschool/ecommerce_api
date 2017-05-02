import pytest
import uuid
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


