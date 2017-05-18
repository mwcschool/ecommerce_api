from http.client import CREATED, NO_CONTENT, NOT_FOUND, BAD_REQUEST
import json
import uuid
from peewee import SqliteDatabase
from models import User, Address
from app import app


class Testaddress:
    @classmethod
    def setup_class(cls):
        db = SqliteDatabase(':memory:')
        Address._meta.database = db
        Address.create_table()
        User._meta.database = db
        User.create_table()
        cls.app = app.test_client()
        User.create(
            user_id=uuid.uuid4(),
            first_name='Giovanni',
            last_name='Mariani',
            email='giovanni@mariani.com',
            password='1234'
        )

    def setup_method(self):
        Address.delete().execute()

    def test_post__success_empty_db(self):
        user = User.get()
        data = {
            'user_id': user.user_id,
            'nation': 'TestNation',
            'city': 'TestCity',
            'postal_code': 'TestPostalCode',
            'local_address': 'TestLocalAddress',
            'phone': 'TestPhone'
        }
        resp = self.app.post('/addresses/', data=data)


        checked_address = user.address.get()
        
        checked_address_dict = {
            'user_id': user.user_id,
            'nation': checked_address.nation,
            'city': checked_address.city,
            'postal_code': checked_address.postal_code,
            'local_address': checked_address.local_address,
            'phone': checked_address.phone
        }

        assert data == checked_address_dict

        assert resp.status_code == CREATED

    def test_post__success(self):
        u_query = User.get()
        data = {
            'user_id': u_query.user_id,
            'nation': 'TestNation',
            'city': 'TestCity',
            'postal_code': 'TestPostalCode',
            'local_address': 'TestLocalAddress',
            'phone': 'TestPhone'
        }

        resp = self.app.post('/addresses/', data=data)
        assert resp.status_code == CREATED

    def test_post__empty_field(self):
        u_query = User.get()
        data = {
            'user_id': u_query.user_id,
            'nation': 'TestNation',
            'city': '',
            'postal_code': 'TestPostalCode',
            'local_address': 'TestLocalAddress',
            'phone': 'TestPhone'
        }

        resp = self.app.post('/addresses/', data=data)
        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 0

    def test_post__field_not_exists(self):
        u_query = User.get()
        data = {
            'user_id': u_query.user_id,
            'city': 'TestCity',
            'postal_code': 'TestPostalCode',
            'local_address': 'TestLocalAddress',
            'phone': 'TestPhone'
        }

        resp = self.app.post('/addresses/', data=data)
        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 0

    def test_put__success(self):
        u_query = User.get()
        address = Address.create(
            address_id=uuid.uuid4(),
            user=u_query,
            nation='TestNation',
            city='TestCity',
            postal_code='TestPostalCode',
            local_address='TestLocalAddress',
            phone='TestPhone')

        data = {
            'user_id': u_query.user_id,
            'nation': 'TestNewNation',
            'city': 'TestNewCity',
            'postal_code': 'TestNewPostalCode',
            'local_address': 'TestNewLocalAddress',
            'phone': 'TestNewPhone'
        }

        resp = self.app.put('/addresses/{}'.format(address.address_id), data=data)

        assert resp.status_code == CREATED

    def test_put__modify_one_field(self):
        u_query = User.get()
        address = Address.create(
            address_id=uuid.uuid4(),
            user=u_query,
            nation='TestNation',
            city='TestCity',
            postal_code='TestPostalCode',
            local_address='TestLocalAddress',
            phone='TestPhone')

        data = {
            'city': 'TestDifferentCity',
        }

        resp = self.app.put('/addresses/{}'.format(address.address_id), data=data)
        assert resp.status_code == BAD_REQUEST

    def test_put__empty_fields(self):
        u_query = User.get()
        address = Address.create(
            address_id=uuid.uuid4(),
            user=u_query,
            nation='TestNation',
            city='TestCity',
            postal_code='TestPostalCode',
            local_address='TestLocalAddress',
            phone='TestPhone')

        data = {
            'nation': '',
            'city': '',
            'postal_code': '',
            'local_address': '',
            'phone': ''
        }

        resp = self.app.put('/addresses/{}'.format(address.address_id), data=data)
        assert resp.status_code == BAD_REQUEST

    def test_put__addressid_not_exist(self):
        data = {
            'nation': 'TestNewNation',
            'city': 'TestNewCity',
            'postal_code': 'TestNewPostalCode',
            'local_address': 'TestNewLocalAddress',
            'phone': 'TestNewPhone'
        }

        resp = self.app.put('/adresses/{}'.format(uuid.uuid4()), data=data)
        assert resp.status_code == NOT_FOUND
        assert len(Address.select()) == 0

    def test_delete_address__success(self):
        u_query = User.get()
        address = Address.create(
            address_id=uuid.uuid4(),
            user=u_query,
            nation='TestNation',
            city='TestCity',
            postal_code='TestPostalCode',
            local_address='TestLocalAddress',
            phone='TestPhone')
        u_query = User.get()
        address2 = Address.create(
            address_id=uuid.uuid4(),
            user=u_query,
            nation='TestNation',
            city='TestCity',
            postal_code='TestPostalCode',
            local_address='TestLocalAddress',
            phone='TestPhone')

        resp = self.app.delete('/addresses/{}'.format(address.address_id))
        all_addresses = Address.select()
        address_from_db = all_addresses.get()
        assert resp.status_code == NO_CONTENT
        assert address_from_db.address_id == address2.address_id

    def test_delete__emptydb_addressid_not_exist(self):
        resp = self.app.delete('/addresses/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND
        assert len(Address.select()) == 0

    def test_delete__addressid_not_exist(self):
        u_query = User.get()
        Address.create(
            address_id=uuid.uuid4(),
            user=u_query,
            nation='TestNation',
            city='TestCity',
            postal_code='TestPostalCode',
            local_address='TestLocalAddress',
            phone='TestPhone')

        resp = self.app.delete('/addresses/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND
        assert len(Address.select()) == 1
