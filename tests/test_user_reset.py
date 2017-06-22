from models import User, Reset
from http.client import NOT_FOUND, OK, BAD_REQUEST
import uuid
import pytest
from datetime import datetime, timedelta

from .base_test import BaseTest


class TestUserReset(BaseTest):
    def test_reset_password__success(self):
        temp_user = self.create_user(email="tryresetemail@domain.com")
        temp_reset = self.create_reset(temp_user)

        data = {
            'code': temp_reset.uuid,
            'password': "newpassword_test",
        }

        resp = self.app.post('/resets/', data=data)

        assert resp.status_code == OK

        new_temp_user = User.get(User.id == temp_reset.user)
        assert new_temp_user.verify_password(data['password'])

    def test_reset_password__failure_reset_instance_not_enabled(self):
        temp_user = self.create_user(email="tryresetemail@domain.com")
        temp_reset = self.create_reset(temp_user)
        temp_reset.enable = False
        temp_reset.save()

        data = {
            'code': temp_reset.uuid,
            'password': "newpassword_test",
        }

        resp = self.app.post('/resets/', data=data)

        assert resp.status_code == NOT_FOUND
        assert User.get() == temp_user
        assert not temp_reset.enable

    def test_reset_password__failure_reset_instance_not_exist(self):
        temp_uuid = uuid.uuid4()
        data = {
            'code': temp_uuid,
            'password': "newpassword_test",
        }

        self.app.post('/resets/', data=data)

        with pytest.raises(Reset.DoesNotExist):
            Reset.get(Reset.uuid == temp_uuid)

    def test_reset_password__failure_reset_instance_expired(self):
        temp_user = self.create_user(email="tryresetemail@domain.com")
        temp_reset = self.create_reset(temp_user)

        temp_reset.expiration_date = (datetime.now() - timedelta(hours=1))
        temp_reset.save()

        data = {
            'code': temp_reset.uuid,
            'password': "newpassword_test",
        }

        resp = self.app.post('/resets/', data=data)

        print(temp_reset.expiration_date)

        assert resp.status_code == NOT_FOUND

    def test_reset_password__failure_password_length_unacceptable(self):
        temp_user = self.create_user(email="tryresetemail@domain.com")
        temp_reset = self.create_reset(temp_user)

        data = {
            'code': temp_reset.uuid,
            'password': "pwd_t",
        }

        resp = self.app.post('/resets/', data=data)

        assert resp.status_code == BAD_REQUEST

    def test_reset_password__failure_user_is_superuser(self):
        temp_user = self.create_user(email="tryresetemail@domain.com")
        temp_reset = self.create_reset(temp_user)
        temp_user.superuser = True
        temp_user.save()

        data = {
            'code': temp_reset.uuid,
            'password': "newpassword_test",
        }

        resp = self.app.post('/resets/', data=data)

        assert resp.status_code == NOT_FOUND
        assert User.get() == temp_user
