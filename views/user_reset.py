from models import Reset
from flask_restful import Resource, reqparse
import utils
from http.client import NOT_FOUND


class PasswordResetResource(Resource):
    def post(self):
        parser = parser = reqparse.RequestParser()
        parser.add_argument('code', type=utils.non_empty_str, required=True)
        parser.add_argument('password', type=utils.non_empty_str, required=True)
        args = parser.parse_args(strict=True)

        try:
            Reset.get(Reset.uuid == args['code'])
        except (Reset.DoesNotExists):
            return None, NOT_FOUND
