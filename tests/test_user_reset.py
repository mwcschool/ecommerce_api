from models import User, Reset
from flask_restful import Resource, reqparse
import utils
from http.client import NOT_FOUND, OK
from datetime import datetime
from passlib.hash import pbkdf2_sha256
from models import User
from views.user import crypt_password

from .base_test import BaseTest


class TestUserReset(BaseTest):


	# class PasswordResetResource(Resource):
	#     def post(self):
	#         parser = parser = reqparse.RequestParser()
	#         parser.add_argument('code', type=utils.non_empty_str, required=True)
	#         parser.add_argument('password', type=utils.non_empty_str, required=True)
	#         args = parser.parse_args(strict=True)

	#         try:
	#             reset_code = Reset.get(Reset.uuid == args['code']
	#                                    and Reset.enable
	#                                    and Reset.expiration_date > datetime.now()
	#                                    )
	#         except (Reset.DoesNotExists):
	#             return None, NOT_FOUND

	#         user = reset_code.user

	#         reset_code.enable = False
	#         user.password = crypt_password(args['password'])

	#         reset_code.save()
	#         user.save()
	#         return None, OK



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

	def test_reset_password__failure_reset_instance_not_enabled():
		pass