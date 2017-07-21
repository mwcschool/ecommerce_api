from http.client import CREATED, NO_CONTENT, NOT_FOUND, BAD_REQUEST, OK
import json
import uuid
from models import Address, User

from .base_test import BaseTest


class TestAddress(BaseTest):
    def setup_method(self):
        super(TestAddress, self).setup_method()
        self.user = self.create_user()

    def test_post__success_empty_db(self):
        data_address = {
            'nation': 'Italia',
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        resp = self.open_with_auth(
            '/addresses/', 'post', self.user.email, 'p4ssw0rd', data=data_address)

        address_from_db = Address.get()
        expected_data = {
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
            'nation': 'Italia',
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        current_user = User.get(User.email == self.user.email)

        resp = self.open_with_auth(
            '/addresses/', 'post', self.user.email, 'p4ssw0rd', data=data_address)

        address_from_server = json.loads(resp.data.decode())

        assert resp.status_code == CREATED

        data_address['user'] = str(current_user.uuid)
        address_from_server.pop('uuid')

        assert address_from_server == data_address

    def test_post__empty_field(self):
        data_address = {
            'nation': '',
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        resp = self.open_with_auth(
            '/addresses/', 'post', self.user.email, 'p4ssw0rd', data=data_address)
        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 0

    def test_post__field_not_exists(self):
        data_address = {
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        resp = self.open_with_auth(
            '/addresses/', 'post', self.user.email, 'p4ssw0rd', data=data_address)
        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 0

    def test_get__address_found(self):
        address = self.create_address(self.user)

        resp = self.open_with_auth(
            '/addresses/{}'.format(address.uuid), 'get', self.user.email, 'p4ssw0rd', data='')
        query = Address.get()
        assert resp.status_code == OK
        assert query.json() == json.loads(resp.data.decode())

    def test_get__address_not_found(self):
        resp = self.open_with_auth(
            '/addresses/{}'.format(uuid.uuid4()), 'get', self.user.email, 'p4ssw0rd', data='')
        assert resp.status_code == NOT_FOUND

    def test_put__success(self):
        data_address = self.create_address(self.user)

        new_data_address = {
            'nation': 'Italia',
            'city': 'Firenze',
            'postal_code': '505050',
            'local_address': 'Via Baracca 15',
            'phone': '0550550550',
        }

        current_user = User.get(User.email == self.user.email)

        resp = self.open_with_auth(
            '/addresses/{}'.format(data_address.uuid), 'put', self.user.email, 'p4ssw0rd',
            data=new_data_address)
        new_data_address['user'] = str(current_user.uuid)
        address_from_db = Address.get()
        expected_data = {
            'user': str(address_from_db.user.uuid),
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

        resp = self.open_with_auth(
            '/addresses/{}'.format(data_address.uuid), 'put', self.user.email, 'p4ssw0rd',
            data=new_data_address)
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

        resp = self.open_with_auth(
            '/addresses/{}'.format(data_address.uuid), 'put', self.user.email, 'p4ssw0rd',
            data=new_data_address)
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

        resp = self.open_with_auth(
            '/addresses/{}'.format(uuid.uuid4()), 'put', self.user.email, 'p4ssw0rd',
            data=data)
        assert resp.status_code == NOT_FOUND
        assert len(Address.select()) == 0

    def test_delete__success(self):
        data_address1 = self.create_address(self.user)

        # TODO: Is ok to have a duplicated address for a single user?
        data_address2 = self.create_address(self.user)

        resp = self.open_with_auth(
            '/addresses/{}'.format(data_address1.uuid), 'delete', self.user.email, 'p4ssw0rd',
            data='')
        all_addresses = Address.select()
        address_from_db = all_addresses.get()
        assert resp.status_code == NO_CONTENT
        assert len(all_addresses) == 1
        assert address_from_db.uuid == data_address2.uuid

    def test_delete__empty_db_address_id_not_exists(self):
        resp = self.open_with_auth(
            '/addresses/{}'.format(uuid.uuid4()), 'delete', self.user.email, 'p4ssw0rd',
            data='')
        assert resp.status_code == NOT_FOUND
        assert len(Address.select()) == 0

    def test_delete__address_id_not_exists(self):
        self.create_address(self.user)

        resp = self.open_with_auth(
            '/addresses/{}'.format(uuid.uuid4()), 'delete', self.user.email, 'p4ssw0rd',
            data='')
        assert resp.status_code == NOT_FOUND
        assert len(Address.select()) == 1

    def test_get__address_found_different_user(self):
        user2 = self.create_user("acaca@bababa.it")
        address = self.create_address(self.user)

        resp = self.open_with_auth(
            '/addresses/{}'.format(address.uuid), 'get', user2.email, 'p4ssw0rd', data='')
        assert resp.status_code == NOT_FOUND

    def test_delete__address_different_user(self):
        user2 = self.create_user('user2@email.com')
        address = self.create_address(self.user)
        resp = self.open_with_auth(
            '/addresses/{}'.format(address.uuid), 'delete', user2.email, 'p4ssw0rd', data='')
        assert resp.status_code == NOT_FOUND

    def test_patch__all_fields_succeed(self):
        data_address = self.create_address(self.user)

        new_data_address = {
            'nation': 'Germania',
            'city': 'Berlino',
            'postal_code': '05100',
            'local_address': 'Via Roma 15',
            'phone': '33333333333',
        }

        current_user = User.get(User.email == self.user.email)

        resp = self.open_with_auth(
            '/addresses/{}'.format(data_address.uuid),
            'patch', self.user.email, 'p4ssw0rd',
            data=new_data_address)

        new_data_address['user'] = str(current_user.uuid)
        address_from_db = Address.get()

        expected_data = {
            'user': str(address_from_db.user.uuid),
            'nation': address_from_db.nation,
            'city': address_from_db.city,
            'postal_code': address_from_db.postal_code,
            'local_address': address_from_db.local_address,
            'phone': address_from_db.phone,
        }

        assert resp.status_code == OK
        assert expected_data == new_data_address
        assert address_from_db.json() == json.loads(resp.data.decode())

    def test_patch_modify_single_field_succeed(self):
        data_address = self.create_address(self.user)

        new_data_address = {
            'nation': 'Germania',
            'city': 'Reykjavik',
            'postal_code': '05100',
            'local_address': 'Via Roma 15',
            'phone': '33333333333',
        }

        current_user = User.get(User.email == self.user.email)

        resp = self.open_with_auth(
            '/addresses/{}'.format(data_address.uuid),
            'patch', self.user.email, 'p4ssw0rd',
            data=new_data_address)

        new_data_address['user'] = str(current_user.uuid)
        address_from_db = Address.get()

        expected_data = {
            'user': str(address_from_db.user.uuid),
            'nation': address_from_db.nation,
            'city': address_from_db.city,
            'postal_code': address_from_db.postal_code,
            'local_address': address_from_db.local_address,
            'phone': address_from_db.phone,
            }

        assert resp.status_code == OK
        assert expected_data == new_data_address
        assert address_from_db.json() == json.loads(resp.data.decode())

    def test_patch_modify_empty_field(self):
        data_address = self.create_address(self.user)

        new_data_address = {
            'nation': '',
        }

        resp = self.open_with_auth(
            '/addresses/{}'.format(data_address.uuid),
            'patch', self.user.email, 'p4ssw0rd',
            data=new_data_address)

        assert resp.status_code == BAD_REQUEST
