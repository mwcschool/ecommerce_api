from models import Reset
from flask_restful import Resource, reqparse
import utils
from http.client import NOT_FOUND, OK
from datetime import datetime


class PasswordResetResource(Resource):
    def post(self):
        parser = parser = reqparse.RequestParser()
        parser.add_argument('code', type=utils.non_empty_str, required=True)
        parser.add_argument('password', type=utils.non_empty_str, required=True)
        args = parser.parse_args(strict=True)

        try:
            reset_code = Reset.get(Reset.uuid == args['code']
                                   and Reset.enable
                                   and Reset.expiration_date > datetime.now()
                                   )
        except (Reset.DoesNotExists):
            return None, NOT_FOUND

        user = reset_code.user

        reset_code.enable = False
        user.password = args['password']

        reset_code.save()
        user.save()
        return None, OK
