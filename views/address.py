import uuid
from models import User, Address
from http.client import CREATED, NOT_FOUND, NO_CONTENT, BAD_REQUEST
from flask_restful import Resource, reqparse
import re


def non_empty_str(val, name):
    if not str(val).strip():
        raise ValueError('The argument {} is not empty'.format(name))
    return str(val)


class AddressesResource(Resource):
    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('nation', type=non_empty_str, required=True)
        parser.add_argument('city', type=non_empty_str, required=True)
        parser.add_argument('postal_code', type=non_empty_str, required=True)
        parser.add_argument('local_address', type=non_empty_str, required=True)
        parser.add_argument('phone', type=non_empty_str, required=True)
        args = parser.parse_args(strict=True)

        check_user = User.select().where(User.user_id == user_id)

        if check_user.exists():
            obj = Address.create(
                address_id=uuid.uuid4(), user=user_id, nation=args['nation'],
                city = args['city'], postal_code = args['postal_code'],
                local_address = args['local_address'], phone = args['phone'])

            return obj.json(), CREATED
        else:
            return '', BAD_REQUEST


class AddressResource(Resource):
    def get(self, address_id):
        try:
            obj = Address.get(address_id=address_id)
        except Address.DoesNotExist:
            return None, NOT_FOUND

    def put(self, address_id):
        try:
            obj = Address.get(address_id=address_id)
        except Address.DoesNotExist:
            return None, NOT_FOUND

    def delete(self, address_id):
        try:
            obj = Address.get(address_id=address_id)
        except Address.DoesNotExist:
            return None, NOT_FOUND

        obj.delete_instance()
        return None, NO_CONTENT
