from models import Reset
from flask_restful import Resource, reqparse
import utils
from http.client import NOT_FOUND, OK, BAD_REQUEST
from datetime import datetime
from passlib.hash import pbkdf2_sha256


def crypt_password(password):
    crypt = pbkdf2_sha256.hash(password)

    return crypt


class PasswordResetResource(Resource):
    def post(self):
        parser = parser = reqparse.RequestParser()
        parser.add_argument('code', type=utils.non_empty_str, required=True)
        parser.add_argument('password', type=utils.non_empty_str, required=True)
        args = parser.parse_args(strict=True)

        try:
            user = Reset.get(Reset.uuid == args['code']).user
            reset_code = Reset.select()\
                .where(Reset.uuid == args['code'])\
                .where(Reset.enable)\
                .where(Reset.expiration_date > datetime.now()).get()

        except Reset.DoesNotExist:
            return None, NOT_FOUND

        if user.superuser:
            return None, NOT_FOUND

        if not len(args['password']) > 6:
            return None, BAD_REQUEST

        reset_code.enable = False
        user.password = crypt_password(args['password'])

        reset_code.save()
        user.save()
        return None, OK
