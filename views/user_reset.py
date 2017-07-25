from models import Reset
from flask_restful import Resource, request
from http.client import NOT_FOUND, OK, BAD_REQUEST
from datetime import datetime
import auth
from jsonschema import ValidationError


class PasswordResetResource(Resource):
    def post(self):
        args = request.form

        try:
            Reset.verify_json(args)
        except ValidationError:
            return None, BAD_REQUEST

        try:
            user = Reset.get(Reset.uuid == args['uuid']).user
            reset_code = Reset.select()\
                .where(Reset.uuid == args['uuid'])\
                .where(Reset.enable)\
                .where(Reset.expiration_date > datetime.now()).get()

        except Reset.DoesNotExist:
            return None, NOT_FOUND

        if user.superuser:
            return None, NOT_FOUND

        reset_code.enable = False
        user.password = auth.crypt_password(args['password'])

        reset_code.save()
        user.save()
        return None, OK
