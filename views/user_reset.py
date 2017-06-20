import uuid
from models import User, Reset
import auth
from flask import g
from http.client import CREATED, NOT_FOUND, NO_CONTENT, BAD_REQUEST, UNAUTHORIZED
from flask_restful import Resource, reqparse
import re
from passlib.hash import pbkdf2_sha256
import utils
from views.user import valid_email, crypt_password


class PasswordResetResource(Resource):
    def post(self):
        parser = parser = reqparse.RequestParser()
        parser.add_argument('code', type=utils.non_empty_str, required=True)
        parser.add_argument('password', type=utils.non_empty_str, required=True)
        args = parser.parse_args(strict=True)

        try:
            reset_code = Reset.get(Reset.uuid == args['code'])
        except (Reset.DoesNotExists):
            return None, NOT_FOUND
