from http.client import CREATED, NO_CONTENT, NOT_FOUND, BAD_REQUEST
import json
import uuid
from peewee import SqliteDatabase
from models import User, Address
from app import app


class Testaddress:
    @classmethod
    def setup_class(cls):
        Address._meta.database = SqliteDatabase(':memory:')
        Address.create_table()
        cls.app = app.test_client()

    def setup_method(self):
        Address.delete().execute()

    def test_post__success_empty_db(self):
        u_query = User.get()
        data = {
            'user': u_query[0],
            'nation': 'TestNation',
            'city': 'TestCity',
            'postal_code': 'TestPostalCode',
            'local_address': 'TestLocalAddress',
            'phone': 'TestPhone'
        }
        resp = self.app.post('/addresses/', data=data)
        query = Address.select()
        address_from_db = Address.get()
        expected_data = {
            'user': address_from_db.user,
            'nation': address_from_db.nation,
            'city': address_from_db.city,
            'postal_code': address_from_db.postal_code,
            'local_address': address_from_db.local_address,
            'phone': address_from_db.phone
        }
        assert expected_data == data
        assert resp.status_code == CREATED
        assert len(query) == 1
        assert query.get().json() == json.loads(resp.data.decode())

    def test_post__success(self):
        u_query = User.get()
        data = {
            'user': u_query[0],
            'nation': 'TestNation',
            'city': 'TestCity',
            'postal_code': 'TestPostalCode',
            'local_address': 'TestLocalAddress',
            'phone': 'TestPhone'
        }

        id_address_created = uuid.uuid4()

        Address.create(
            address_id=id_address_created,
            user=u_query[0],
            nation='TestNation',
            city='TestCity',
            postal_code='TestPostalCode',
            local_address='TestLocalAddress',
            phone='TestPhone'
        )
        resp = self.app.post('/addresses/', data=data)
        query = Address.select().where(Address.address_id != id_address_created)
        assert resp.status_code == CREATED
        assert query.get().json() == json.loads(resp.data.decode())

    def test_post__empty_field(self):
        u_query = User.get()
        data = {
            'user': u_query[0],
            'nation': 'TestNation',
            'city': 'TestCity',
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
            'user': u_query[0],
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
            user=u_query[0],
            nation='TestNation',
            city='TestCity',
            postal_code='TestPostalCode',
            local_address='TestLocalAddress',
            phone='TestPhone')

        data = {
            'nation': 'TestNewNation',
            'city': 'TestNewCity',
            'postal_code': 'TestNewPostalCode',
            'local_address': 'TestNewLocalAddress',
            'phone': 'TestNewPhone'
        }

        resp = self.app.put('/addresses/{}'.format(address.address_id), data=data)
        query = Address.select()
        address_from_db = query.get()
        expected_data = {
            'user': address_from_db.user,
            'nation': address_from_db.nation,
            'city': address_from_db.city,
            'postal_code': address_from_db.postal_code,
            'local_address': address_from_db.local_address,
            'phone': address_from_db.phone
        }
        assert expected_data == data
        assert resp.status_code == CREATED
        assert query.get().json() == json.loads(resp.data.decode())

    def test_put__modify_one_field(self):
        u_query = User.get()
        address = Address.create(
            address_id=uuid.uuid4(),
            user=u_query[0],
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
            user=u_query[0],
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
            'phone':''
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
            user=u_query[0],
            nation='TestNation',
            city='TestCity',
            postal_code='TestPostalCode',
            local_address='TestLocalAddress',
            phone='TestPhone')
        u_query = User.get()
        address2 = Address.create(
            address_id=uuid.uuid4(),
            user=u_query[0],
            nation='TestNation',
            city='TestCity',
            postal_code='TestPostalCode',
            local_address='TestLocalAddress',
            phone='TestPhone')

        resp = self.app.delete('/addresses/{}'.format(address.address_id))
        all_addresses = Address.select()
        address_from_db = all_addresses.get()
        assert resp.status_code == NO_CONTENT
        assert len(all_addresses) == 1
        assert address_from_db.address_id == address2.address_id

    def test_delete__emptydb_addressid_not_exist(self):
        resp = self.app.delete('/addresses/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND
        assert len(Address.select()) == 0

    def test_delete__addressid_not_exist(self):
        u_query = User.get()
        Address.create(
            address_id=uuid.uuid4(),
            user=u_query[0],
            nation='TestNation',
            city='TestCity',
            postal_code='TestPostalCode',
            local_address='TestLocalAddress',
            phone='TestPhone')

        resp = self.app.delete('/addresses/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND
        assert len(Address.select()) == 1
