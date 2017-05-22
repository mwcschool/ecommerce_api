import uuid
from models import User, Address
from http.client import CREATED, NOT_FOUND, NO_CONTENT, BAD_REQUEST, OK
from flask_restful import Resource, reqparse
import utils


class AddressesResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        # TODO Security issue, grab user_id from user authentication
        parser.add_argument('user_id', type=utils.non_empty_str, required=True)
        parser.add_argument('nation', type=utils.non_empty_str, required=True)
        parser.add_argument('city', type=utils.non_empty_str, required=True)
        parser.add_argument('postal_code', type=utils.non_empty_str, required=True)
        parser.add_argument('local_address', type=utils.non_empty_str, required=True)
        parser.add_argument('phone', type=utils.non_empty_str, required=True)
        args = parser.parse_args(strict=True)

        for parm in ['nation', 'city', 'postal_code', 'local_address', 'phone']:
            if len(args[parm]) < 3:
                return '', BAD_REQUEST

        try:
            user = User.get(User.user_id == args['user_id'])
        except User.DoesNotExist:
            return '', BAD_REQUEST

        address = Address.create(
            address_id=uuid.uuid4(),
            user=user,
            nation=args['nation'],
            city=args['city'],
            postal_code=args['postal_code'],
            local_address=args['local_address'],
            phone=args['phone'],
        )

        return address.json(), CREATED


class AddressResource(Resource):
    def get(self, address_id):
        try:
            address = Address.get(Address.address_id == address_id)
        except Address.DoesNotExist:
            return None, NOT_FOUND

        return address.json(), OK

    def put(self, address_id):
        try:
            address = Address.get(Address.address_id == address_id)
        except Address.DoesNotExist:
            return None, NOT_FOUND

        parser = reqparse.RequestParser()
        # TODO Security issue, grab user_id from user authentication
        parser.add_argument('user_id', type=utils.non_empty_str, required=True)
        parser.add_argument('nation', type=utils.non_empty_str, required=True)
        parser.add_argument('city', type=utils.non_empty_str, required=True)
        parser.add_argument('postal_code', type=utils.non_empty_str, required=True)
        parser.add_argument('local_address', type=utils.non_empty_str, required=True)
        parser.add_argument('phone', type=utils.non_empty_str, required=True)
        args = parser.parse_args(strict=True)

        for parm in ['nation', 'city', 'postal_code', 'local_address', 'phone']:
            if len(args[parm]) < 3:
                return '', BAD_REQUEST

        if str(address.user.user_id) == args['user_id']:
            address.nation = args['nation']
            address.city = args['city']
            address.postal_code = args['postal_code']
            address.local_address = args['local_address']
            address.phone = args['phone']
            address.save()

            return address.json(), CREATED
        else:
            return '', BAD_REQUEST

    def delete(self, address_id):
        try:
            address = Address.get(Address.address_id == address_id)
        except Address.DoesNotExist:
            return None, NOT_FOUND

        address.delete_instance()
        return None, NO_CONTENT
