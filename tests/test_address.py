from http.client import CREATED, NO_CONTENT, NOT_FOUND, BAD_REQUEST, OK
import json
import uuid
from peewee import SqliteDatabase
from models import User, Address
from app import app


class TestAddress:
    @classmethod
    def setup_class(cls):
        db = SqliteDatabase(':memory:')
        User._meta.database = db
        Address._meta.database = db
        User.create_table()
        Address.create_table()
        cls.app = app.test_client()

        User.create(
            uuid=uuid.uuid4(),
            first_name='Mario',
            last_name='Rossi',
            email='email@email.it',
            password='123456789',
        )

    def setup_method(self):
        Address.delete().execute()

    def test_post__success_empty_db(self):
        data_user = User.get()
        data_address = {
            'user_id': data_user.uuid,
            'nation': 'Italia',
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        resp = self.app.post('/addresses/', data=data_address)

        query = Address.select()
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
        assert len(query) == 1
        assert query.get().json() == json.loads(resp.data.decode())

    def test_post__success(self):
        data_user = User.get()
        address_id_created = uuid.uuid4()
        Address.create(
            uuid=address_id_created,
            user=data_user,
            nation='Italia',
            city='Prato',
            postal_code='59100',
            local_address='Via Roncioni 10',
            phone='0574100100',
            )

        data_address = {
            'user_id': data_user.uuid,
            'nation': 'Italia',
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        resp = self.app.post('/addresses/', data=data_address)
        query = Address.select().where(Address.uuid != address_id_created)
        assert resp.status_code == CREATED
        assert query.get().json() == json.loads(resp.data.decode())

    def test_post__empty_field(self):
        data_user = User.get()
        data_address = {
            'user_id': data_user.uuid,
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
        data_user = User.get()
        data_address = {
            'user_id': data_user.uuid,
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        resp = self.app.post('/addresses/', data=data_address)
        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 0

    def test_post__user_not_exists(self):
        data_address = {
            'user_id': uuid.uuid4(),
            'nation': 'Italia',
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        resp = self.app.post('/addresses/', data=data_address)
        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 0

    def test_get__address_found(self):
        data_user = User.get()
        address_id_created = uuid.uuid4()
        Address.create(
            uuid=address_id_created,
            user=data_user,
            nation='Italia',
            city='Prato',
            postal_code='59100',
            local_address='Via Roncioni 10',
            phone='0574100100',
            )

        resp = self.app.get('/addresses/{}'.format(address_id_created))
        query = Address.get()
        assert resp.status_code == OK
        assert query.json() == json.loads(resp.data.decode())

    def test_get__address_not_found(self):
        resp = self.app.get('/addresses/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_put__success(self):
        data_user = User.get()
        data_address = Address.create(
            uuid=uuid.uuid4(),
            user=data_user,
            nation='Italia',
            city='Prato',
            postal_code='59100',
            local_address='Via Roncioni 10',
            phone='0574100100',
            )

        new_data_address = {
            'user_id': data_user.uuid,
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
        data_user = User.get()
        data_address = Address.create(
            uuid=uuid.uuid4(),
            user=data_user,
            nation='Italia',
            city='Prato',
            postal_code='59100',
            local_address='Via Roncioni 10',
            phone='0574100100',
            )

        new_data_address = {
            'nation': 'Albania',
        }

        resp = self.app.put('/addresses/{}'.format(data_address.uuid), data=new_data_address)
        assert resp.status_code == BAD_REQUEST

    def test_put__modify_empty_fields(self):
        data_user = User.get()
        data_address = Address.create(
            uuid=uuid.uuid4(),
            user=data_user,
            nation='Italia',
            city='Prato',
            postal_code='59100',
            local_address='Via Roncioni 10',
            phone='0574100100',
            )

        new_data_address = {
            'user_id': data_user.uuid,
            'nation': '',
            'city': '',
            'postal_code': '',
            'local_address': '',
            'phone': '',
        }

        resp = self.app.put('/addresses/{}'.format(data_address.uuid), data=new_data_address)
        assert resp.status_code == BAD_REQUEST

    def test_put__address_id_not_exists(self):
        data_user = User.get()
        data = {
            'user_id': data_user.uuid,
            'nation': 'Italia',
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        resp = self.app.put('/addresses/{}'.format(uuid.uuid4()), data=data)
        assert resp.status_code == NOT_FOUND
        assert len(Address.select()) == 0

    def test_put__user_id_not_exists(self):
        data_user = User.get()
        data_address = Address.create(
            uuid=uuid.uuid4(),
            user=data_user,
            nation='Italia',
            city='Prato',
            postal_code='59100',
            local_address='Via Roncioni 10',
            phone='0574100100',
            )
        data = {
            'user_id': uuid.uuid4(),
            'nation': 'Italia',
            'city': 'Firenze',
            'postal_code': '505050',
            'local_address': 'Via Roncioni 15',
            'phone': '0558778666',
        }

        resp = self.app.put('/addresses/{}'.format(data_address.uuid), data=data)
        assert resp.status_code == BAD_REQUEST
        assert len(Address.select()) == 1
        assert data_address == Address.get()

    def test_delete__success(self):
        data_user = User.get()
        data_address1 = Address.create(
            uuid=uuid.uuid4(),
            user=data_user,
            nation='Italia',
            city='Prato',
            postal_code='59100',
            local_address='Via Roncioni 10',
            phone='0574100100',
            )
        data_address2 = Address.create(
            uuid=uuid.uuid4(),
            user=data_user,
            nation='Italia',
            city='Firenze',
            postal_code='59000',
            local_address='Via Baracca 10',
            phone='0558778666',
            )

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
        data_user = User.get()
        Address.create(
            uuid=uuid.uuid4(),
            user=data_user,
            nation='Italia',
            city='Prato',
            postal_code='59100',
            local_address='Via Roncioni 10',
            phone='0574100100',
            )
        resp = self.app.delete('/addresses/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND
        assert len(Address.select()) == 1
