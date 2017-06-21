from http.client import CREATED, NO_CONTENT, NOT_FOUND, BAD_REQUEST, UNAUTHORIZED
import json
import uuid
from models import User, Reset
import pytest

from .base_test import BaseTest


class Testuser(BaseTest):
    def test_post__success_empty_db(self):
        data = {
            'first_name': 'Alessandro',
            'last_name': 'Cappellini',
            'email': 'emailprova@pippo.it',
            'password': '1234567'
        }
        resp = self.app.post('/users/', data=data)
        query = User.select()
        user_from_db = User.get()
        expected_data = {
            'first_name': user_from_db.first_name,
            'last_name': user_from_db.last_name,
            'email': user_from_db.email,
            'password': data['password']
        }
        assert expected_data == data
        assert resp.status_code == CREATED
        assert len(query) == 1
        assert query.get().json() == json.loads(resp.data.decode())
        assert not user_from_db.superuser
        assert user_from_db.status == 'enable'

    def test_post__success(self):
        data = {
            'first_name': 'Anna',
            'last_name': 'Markis',
            'email': 'anna@markis.com',
            'password': '1234567'
        }

        user1 = self.create_user()

        resp = self.app.post('/users/', data=data)
        query = User.select().where(User.uuid != user1.uuid)
        assert resp.status_code == CREATED
        assert query.get().json() == json.loads(resp.data.decode())
        user_from_db = query.get()
        assert not user_from_db.superuser
        assert user_from_db.status == 'enable'

    def test_post__empty_field(self):
        data = {
            'first_name': '',
            'last_name': 'Alessandro',
            'email': 'alessandro@hotmail.com',
            'password': '1234'
        }

        resp = self.app.post('/users/', data=data)
        assert resp.status_code == BAD_REQUEST
        assert len(User.select()) == 0

    def test_post__field_not_exists(self):
        data = {
            'last_name': 'Pippo',
            'email': 'mark@pippo.it',
            'password': '123456'
        }

        resp = self.app.post('/users/', data=data)
        assert resp.status_code == BAD_REQUEST
        assert len(User.select()) == 0

    def test_put__success(self):
        user = self.create_user()

        data = {
            'first_name': 'anna',
            'last_name': 'Marini',
            'email': 'giovanni@mariani.com',
            'password': '1234567'
        }

        resp = self.open_with_auth(
            '/users/{}'.format(user.uuid), 'put', user.email, 'p4ssw0rd', data=data)
        query = User.select()
        user_from_db = query.get()
        expected_data = {
            'first_name': user_from_db.first_name,
            'last_name': user_from_db.last_name,
            'email': user_from_db.email,
            'password': data['password']
        }

        assert expected_data == data
        assert resp.status_code == CREATED
        assert query.get().json() == json.loads(resp.data.decode())
        assert not user_from_db.superuser

    def test_put__modify_one_field(self):
        user = self.create_user()

        data = {
            'first_name': 'Anna',
        }

        resp = self.open_with_auth(
            '/users/{}'.format(user.uuid), 'put', user.email, 'p4ssw0rd', data=data)
        assert resp.status_code == BAD_REQUEST

    def test_put__empty_fields(self):
        user = self.create_user()

        data = {
            'first_name': '',
            'last_name': '',
            'email': '',
            'password': ''
        }

        resp = self.open_with_auth(
            '/users/{}'.format(user.uuid), 'put', user.email, 'p4ssw0rd', data=data)
        assert resp.status_code == BAD_REQUEST

    def test_put__user_unauthorized(self):
        user = self.create_user()

        data = {
            'first_name': 'Giovanni',
            'last_name': 'Pippo',
            'email': 'giovanni@mariani.com',
            'password': '1234567'
        }

        resp = self.open_with_auth(
            '/users/{}'.format(user.uuid), 'put', user.email, 'wr0ng_p4ssw0rd', data=data)
        query = User.select().where(User.last_name == user.last_name)
        assert len(query) == 1
        assert resp.status_code == UNAUTHORIZED

    def test_put__user_unauthorized_for_modify_another_user(self):
        user = self.create_user()
        user2 = self.create_user("email2@domain.com")

        data = {
            'first_name': 'Anna',
            'last_name': 'Rossi',
            'email': 'maria@rossi.com',
            'password': '1234567'
        }

        resp = self.open_with_auth(
            '/users/{}'.format(user.uuid), 'put', user2.email, 'p4ssw0rd', data=data)
        assert resp.status_code == UNAUTHORIZED

    def test_delete_user__success(self):
        user = self.create_user()
        self.create_user("email2@domain.com")

        resp = self.open_with_auth(
            '/users/{}'.format(user.uuid), 'delete', user.email, 'p4ssw0rd', data='')

        assert resp.status_code == NO_CONTENT
        assert len(User.select()) == 2
        assert User.get(uuid=user.uuid).status == 'deleted'

    def test_delete__userid_not_exist(self):
        self.create_user()

        resp = self.open_with_auth(
            '/users/{}'.format(uuid.uuid4), 'delete', 'ciao@libero.it', 'p4ssw0rd', data='')
        assert resp.status_code == NOT_FOUND
        assert len(User.select()) == 1
        assert User.get().status == 'enable'

    def test_delete_user__unauthorized_for_delete_another_user(self):
        user = self.create_user()
        user2 = self.create_user("email2@doamin.com")

        resp = self.open_with_auth(
            '/users/{}'.format(user.uuid), 'delete', user2.email, 'p4ssw0rd', data='')
        assert resp.status_code == UNAUTHORIZED

    def test_reset_password_request__success(self):
        temp_user = self.create_user(email="tryresetemail@domain.com")

        data = {
            'email': temp_user.email,
        }

        resp = self.app.post('/users/reset/', data=data)

        assert Reset.get(Reset.user == temp_user)
        assert resp.status_code == NO_CONTENT

    def test_reset_password_request__failure_badformatted_email(self):
        data = {
            'email': 'tryresetemaildomain.com',
        }

        resp = self.app.post('/users/reset/', data=data)

        assert resp.status_code == BAD_REQUEST

    def test_reset_password_request__failure_user_not_exist(self):
        temp_email = 'tryresetemail@domain.com'
        data = {
            'email': temp_email,
        }

        resp = self.app.post('/users/reset/', data=data)
        assert resp.status_code == NO_CONTENT
        with pytest.raises(User.DoesNotExist):
            User.get(User.email == temp_email)

    def test_reset_password_request__success_only_one_request_enabled(self):
        temp_email = 'tryresetemail@domain.com'
        self.create_user(email=temp_email)
        data = {
            'email': temp_email,
        }

        self.app.post('/users/reset/', data=data)
        self.app.post('/users/reset/', data=data)

        Reset.update(enable=True)

        resp = self.app.post('/users/reset/', data=data)

        assert len(Reset.select().where(Reset.enable)) == 1
        assert resp.status_code == NO_CONTENT
