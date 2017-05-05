from http.client import CREATED, NO_CONTENT, NOT_FOUND, BAD_REQUEST
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
            'email': 'emailprova@pippo.it',
            'password': '1234567'
        }
        resp = self.app.post('/users/', data=data)
        query = User.select()
        assert resp.status_code == CREATED
        assert query == json.loads(resp.data.decode())

    def test_post__success(self):
        data = {
            'first_name': 'Anna',
            'last_name': 'Markis',
            'email': 'anna@markis.com',
            'password': '1234567'
        }

        User.create(
            user_id=uuid.uuid4(),
            first_name='Giovanni',
            last_name='Mariani',
            email='giovanni@mariani.com',
            password='1234'
            )
        resp = self.app.post('/users/', data=data)
        query = User.select()
        assert resp.status_code == CREATED
        assert query == json.loads(resp.data.decode())

    def test_post__empty_field(self):
        data = {
            'first_name': '',
            'last_name': 'Alessandro',
            'email': 'alessandro@hotmail.com',
            'password': '1234'
        }

        resp = self.app.post('/users/', data=data)
        assert resp.status_code == BAD_REQUEST

    def test_post__field_not_exist(self):
        data = {
            'last_name': 'Pippo',
            'email': 'mark@pippo.it',
            'password': '123456'
        }

        resp = self.app.post('/users/', data=data)
        assert resp.status_code == BAD_REQUEST

    def test_put__success(self):
        obj1 = User.create(
            user_id=uuid.uuid4(),
            first_name='Giovanni',
            last_name='Mariani',
            email='giovanni@mariani.com',
            password='1234567'
        )

        data = {
            'first_name': 'Anna',
            'last_name': 'Markis',
            'email': 'anna@markis.com',
            'password': '1234567'
        }

        resp = self.app.put('/user/{}'.format(obj1.user_id), data=data)
        query = User.select()
        assert resp.status_code == CREATED
        assert query == json.loads(resp.data.decode())

    def test_put__one_field(self):
        obj1 = User.create(
            user_id=uuid.uuid4(),
            first_name='Giovanni',
            last_name='Mariani',
            email='giovanni@mariani.com',
            password='1234'
        )

        data = {
            'first_name': 'Anna',
        }

        resp = self.app.put('/user/{}'.format(obj1.user_id), data=data)
        assert resp.status_code == BAD_REQUEST

    def test_put__empty_fields(self):
        obj1 = User.create(
            user_id=uuid.uuid4(),
            first_name='Giovanni',
            last_name='Mariani',
            email='giovanni@mariani.com',
            password='1234'
        )

        data = {
            'first_name': '',
            'last_name': '',
            'email': '',
            'password': ''
        }

        resp = self.app.put('/user/{}'.format(obj1.user_id), data=data)
        assert resp.status_code == BAD_REQUEST

    def test_put__userid_not_exist(self):
        data = {
            'first_name': 'Anna',
            'last_name': 'Markis',
            'email': 'anna@markis.com',
            'password': '12345'
        }

        resp = self.app.put('/user/{}'.format(uuid.uuid4()), data=data)
        assert resp.status_code == NOT_FOUND

    def test_delete_user__success(self):
        data_1 = {
            'first_name': 'Alessandro',
            'last_name': 'Cappellinni',
            'email': 'prova@pippo.com',
            'password': '1234'
        }
        data_2 = {
            'first_name': 'Jonh',
            'last_name': 'Smith',
            'email': "jonh@smith.com",
            'password': "1234"
        }
        obj1 = User.create(
            user_id=uuid.uuid4(),
            first_name=data_1['first_name'],
            last_name=data_1['last_name'],
            email=data_1['email'],
            password=data_1['password']
            )
        obj2 = User.create(
            user_id=uuid.uuid4(),
            first_name=data_2['first_name'],
            last_name=data_2['last_name'],
            email=data_2['email'],
            password=data_2['password']
            )
        resp = self.app.delete('/user/{}'.format(obj1.user_id))
        assert resp.status_code == NO_CONTENT
        assert len(User.select()) == 1
        assert len(User.select().where(User.user_id == obj2.user_id)) == 1

    def test_delete__emptydb_userid_not_exist(self):
        resp = self.app.delete('/user/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_delete__userid_not_exist(self):
        User.create(
            user_id=uuid.uuid4(),
            first_name='Alessandro',
            last_name='Rossi',
            email='a@b.it',
            password='ciaociao'
        )
        resp = self.app.delete('/user/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND
        assert len(User.select()) == 1
