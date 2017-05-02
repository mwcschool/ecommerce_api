from views.user import UserResource
from http.client import OK, CREATED, NO_CONTENT, NOT_FOUND
import json
import uuid
from peewee import SqliteDatabase
from models import User
from app import app

class Testuser:
	@classmethod
	def setup_class(cls):
		User._meta.database = SqliteDatabase(':memory:')
		User.create_table()
		cls.app = app.test_client()

	def setup_method(self):
		User.delete().execute()

	def test_post__empty(self):
		data = {
			'first_name': 'Alessandro',
			'last_name': 'Cappellini',
			'email': 'email_prova@pippo.it',
			'password': '1234'
		}
		resp = self.app.post('/user/', data=data)
		'''query = User.select()
		assert resp.status_code == CREATED
		assert query == json.loads(resp.data.decode())'''
