from http.client import CREATED, NO_CONTENT, NOT_FOUND, BAD_REQUEST, OK
import json
import uuid
from peewee import SqliteDatabase
from models import User, Address
from app import app

from .base_test import BaseTest


class TestAddress(BaseTest):
    def setup_method(self):
        super(TestAddress, self).setup_method()
        self.user = self.create_user()

    def test_post__success_empty_db(self):
        data_address = {
            'user_id': self.user.uuid,
            'nation': 'Italia',
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        resp = self.app.post('/addresses/', data=data_address)

        address_from_db = Address.get()
        expected_data = {
            'user_id': address_from_db.user.uuid,
            'nation': address_from_db.nation,
            'city': address_from_db.city,
            'postal_code': address_from_db.postal_code,
            'local_address': address_from_db.local_address,
            'phone': address_from_db.phone,
        }
        assert expected_data == data_address
        assert resp.status_code == CREATED
        assert len(Address.select()) == 1
        assert address_from_db.json() == json.loads(resp.data.decode())

    def test_post__success(self):
        data_address = {
            'user_id': self.user.uuid,
            'nation': 'Italia',
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        resp = self.app.post('/addresses/', data=data_address)

        address_from_server = json.loads(resp.data.decode())

        address_from_db = Address.get(Address.uuid == address_from_server['uuid'])
        assert resp.status_code == CREATED

        data_address['user'] = str(data_address['user_id'])
        data_address.pop('user_id')

        address_from_server.pop('uuid')

        assert address_from_server == data_address

    def test_post__empty_field(self):
        data_address = {
            'user_id': self.user.uuid,
            'nation': '',
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        resp = self.app.post('/addresses/', data=data_address)
        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 0

    def test_post__field_not_exists(self):
        data_address = {
            'user_id': self.user.uuid,
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        resp = self.app.post('/addresses/', data=data_address)
        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 0

    def test_get__address_found(self):
        address = self.create_address(self.user)

        resp = self.app.get('/addresses/{}'.format(address.uuid))
        query = Address.get()
        assert resp.status_code == OK
        assert query.json() == json.loads(resp.data.decode())

    def test_get__address_not_found(self):
        resp = self.app.get('/addresses/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_put__success(self):
        data_address = self.create_address(self.user)

        new_data_address = {
            'user_id': self.user.uuid,
            'nation': 'Italia',
            'city': 'Firenze',
            'postal_code': '505050',
            'local_address': 'Via Baracca 15',
            'phone': '0550550550',
        }

        resp = self.app.put('/addresses/{}'.format(data_address.uuid), data=new_data_address)
        address_from_db = Address.get()
        expected_data = {
            'user_id': address_from_db.user.uuid,
            'nation': address_from_db.nation,
            'city': address_from_db.city,
            'postal_code': address_from_db.postal_code,
            'local_address': address_from_db.local_address,
            'phone': address_from_db.phone,
        }
        assert expected_data == new_data_address
        assert resp.status_code == CREATED
        assert address_from_db.json() == json.loads(resp.data.decode())

    def test_put__modify_one_field(self):
        data_address = self.create_address(self.user)

        new_data_address = {
            'nation': 'Albania',
        }

        resp = self.app.put('/addresses/{}'.format(data_address.uuid), data=new_data_address)
        assert resp.status_code == BAD_REQUEST

    def test_put__modify_empty_fields(self):
        data_address = self.create_address(self.user)

        new_data_address = {
            'user_id': self.user.uuid,
            'nation': '',
            'city': '',
            'postal_code': '',
            'local_address': '',
            'phone': '',
        }

        resp = self.app.put('/addresses/{}'.format(data_address.uuid), data=new_data_address)
        assert resp.status_code == BAD_REQUEST

    def test_put__address_id_not_exists(self):
        data = {
            'user_id': self.user.uuid,
            'nation': 'Italia',
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        resp = self.app.put('/addresses/{}'.format(uuid.uuid4()), data=data)
        assert resp.status_code == NOT_FOUND
        assert len(Address.select()) == 0

    def test_delete__success(self):
        data_address1 = self.create_address(self.user)

        # TODO: Is ok to have a duplicated address for a single user?
        data_address2 = self.create_address(self.user)

        resp = self.app.delete('/addresses/{}'.format(data_address1.uuid))
        all_addresses = Address.select()
        address_from_db = all_addresses.get()
        assert resp.status_code == NO_CONTENT
        assert len(all_addresses) == 1
        assert address_from_db.uuid == data_address2.uuid

    def test_delete__empty_db_address_id_not_exists(self):
        resp = self.app.delete('/addresses/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND
        assert len(Address.select()) == 0

    def test_delete__address_id_not_exists(self):
        self.create_address(self.user)

        resp = self.app.delete('/addresses/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND
        assert len(Address.select()) == 1
