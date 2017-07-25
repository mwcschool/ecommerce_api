from models import User
from http.client import NOT_FOUND, OK, BAD_REQUEST
import uuid
from datetime import datetime, timedelta

from .base_test import BaseTest


class TestUserReset(BaseTest):
    def test_reset_password__success(self):
        temp_user = self.create_user(email="tryresetemail@domain.com")
        temp_reset = self.create_reset(temp_user)

        data = {
            'uuid': temp_reset.uuid,
            'password': "newpassword_test",
        }

        resp = self.app.post('/resets/', data=data)

        assert resp.status_code == OK

        temp_user = temp_user.reload()
        assert temp_user.verify_password(data['password'])

    def test_reset_password__failure_reset_instance_not_enabled(self):
        temp_user = self.create_user(email="tryresetemail@domain.com")
        temp_reset = self.create_reset(user=temp_user, enable=False)

        data = {
            'uuid': temp_reset.uuid,
            'password': "newpassword_test",
        }

        resp = self.app.post('/resets/', data=data)

        assert resp.status_code == NOT_FOUND
        assert User.get() == temp_user

    def test_reset_password__failure_reset_instance_not_exist(self):
        temp_uuid = uuid.uuid4()
        data = {
            'uuid': temp_uuid,
            'password': "newpassword_test",
        }

        resp = self.app.post('/resets/', data=data)

        assert resp.status_code == NOT_FOUND

    def test_reset_password__failure_reset_instance_expired(self):
        temp_user = self.create_user(email="tryresetemail@domain.com")
        temp_reset = self.create_reset(
            user=temp_user,
            expiration_date=datetime.now() - timedelta(hours=1))

        data = {
            'uuid': temp_reset.uuid,
            'password': "newpassword_test",
        }

        resp = self.app.post('/resets/', data=data)
        assert resp.status_code == NOT_FOUND

    def test_reset_password__failure_password_length_unacceptable(self):
        temp_user = self.create_user(email="tryresetemail@domain.com")
        temp_reset = self.create_reset(temp_user)

        data = {
            'uuid': temp_reset.uuid,
            'password': "pwd_t",
        }

        resp = self.app.post('/resets/', data=data)

        assert resp.status_code == BAD_REQUEST

    def test_reset_password__failure_user_is_superuser(self):
        temp_user = self.create_user(email="tryresetemail@domain.com", superuser=True)
        temp_reset = self.create_reset(temp_user)

        data = {
            'uuid': temp_reset.uuid,
            'password': "newpassword_test",
        }

        resp = self.app.post('/resets/', data=data)

        assert resp.status_code == NOT_FOUND
        assert User.get() == temp_user

    def test_reset_password__failure_uuid_not_inserted(self):
        temp_user = self.create_user(email="tryresetemail@domain.com")
        self.create_reset(temp_user)

        data = {
            'password': "newpassword_test",
        }

        resp = self.app.post('/resets/', data=data)

        assert resp.status_code == BAD_REQUEST

    def test_reset_password__failure_password_not_inserted(self):
        temp_user = self.create_user(email="tryresetemail@domain.com")
        temp_reset = self.create_reset(temp_user)

        data = {
            'uuid': temp_reset.uuid,
        }

        resp = self.app.post('/resets/', data=data)

        assert resp.status_code == BAD_REQUEST
