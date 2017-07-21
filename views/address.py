import uuid
from models import Address
from http.client import CREATED, NOT_FOUND, NO_CONTENT, BAD_REQUEST, OK
from flask_restful import Resource
from flask import g, request
import auth
from jsonschema import ValidationError

# import utils


class AddressesResource(Resource):
    @auth.login_required
    def post(self):
        json = request.get_json()
        try:
            Address.verify_json(json)
        except ValidationError as err:
            return {"message": err.message}, BAD_REQUEST

        address = Address.create(
            uuid=uuid.uuid4(),
            user=g.current_user,
            nation=json['nation'],
            city=json['city'],
            postal_code=json['postal_code'],
            local_address=json['local_address'],
            phone=json['phone'],
        )

        return address.json(), CREATED


class AddressResource(Resource):
    @auth.login_required
    def get(self, address_id):
        try:
            address = (
                Address.select()
                .where(Address.uuid == address_id)
                .where(Address.user == g.current_user)
                .get())
        except Address.DoesNotExist:
            return None, NOT_FOUND

        return address.json(), OK

    @auth.login_required
    def put(self, address_id):
        json = request.get_json()
        try:
            address = (
                Address.select()
                .where(Address.uuid == address_id)
                .where(Address.user == g.current_user)
                .get())
        except Address.DoesNotExist:
            return None, NOT_FOUND

        try:
            Address.verify_json(json)
        except ValidationError as err:
            return {"message": err.message}, BAD_REQUEST

        if address.user.uuid == g.current_user.uuid:
            address.nation = json['nation']
            address.city = json['city']
            address.postal_code = json['postal_code']
            address.local_address = json['local_address']
            address.phone = json['phone']
            address.save()

            return address.json(), CREATED
        else:
            return '', BAD_REQUEST

    @auth.login_required
    def patch(self, address_id):
        try:
            address = (
                Address.select()
                .where(Address.uuid == address_id)
                .where(Address.user == g.current_user)
                .get())
        except Address.DoesNotExist:
            return None, NOT_FOUND

        parser = reqparse.RequestParser()
        parser.add_argument('nation', type=utils.non_empty_str)
        parser.add_argument('city', type=utils.non_empty_str)
        parser.add_argument('postal_code', type=utils.non_empty_str)
        parser.add_argument('local_address', type=utils.non_empty_str)
        parser.add_argument('phone', type=utils.non_empty_str)
        args = parser.parse_args(strict=True)

        for param in ['nation', 'city', 'postal_code', 'local_address', 'phone']:
            if args.get(param) and args.get(param) != getattr(address, param):
                if len(args[param]) < 3:
                    return '', BAD_REQUEST
                else:
                    setattr(address, param, args[param])
        address.save()

        return address.json(), OK

    @auth.login_required
    def delete(self, address_id):
        try:
            address = (
                Address.select()
                .where(Address.uuid == address_id)
                .where(Address.user == g.current_user)
                .get())
        except Address.DoesNotExist:
            return None, NOT_FOUND

        address.delete_instance()
        return None, NO_CONTENT
