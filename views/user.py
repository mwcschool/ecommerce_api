import uuid
from models import User
from http.client import CREATED, NOT_FOUND, NO_CONTENT, BAD_REQUEST
from flask_restful import Resource, reqparse
import re


def non_empty_str(val, name):
    if not str(val).strip():
        raise ValueError('The argument {} is not empty'.format(name))
    return str(val)


class UsersResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=non_empty_str, required=True)
        parser.add_argument('last_name', type=non_empty_str, required=True)
        parser.add_argument('email', type=non_empty_str, required=True)
        parser.add_argument('password', type=non_empty_str, required=True)
        args = parser.parse_args(strict=True)

        regex = re.compile('[a-z]{3,}(?P<chiocciola>@)[a-z]{3,}\.[a-z]{2,}')

        if regex.match(args['email']) is not None and len(args['password']) > 6:
            obj = User.create(
                user_id=uuid.uuid4(),
                first_name=args['first_name'],
                last_name=args['last_name'],
                email=args['email'],
                password=args['password']
            )

            return obj.json(), CREATED
        else:
            return '', BAD_REQUEST


class UserResource(Resource):
    def put(self, user_id):
        try:
            obj = User.get(user_id=user_id)
        except User.DoesNotExist:
            return None, NOT_FOUND

        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=non_empty_str, required=True)
        parser.add_argument('last_name', type=non_empty_str, required=True)
        parser.add_argument('email', type=non_empty_str, required=True)
        parser.add_argument('password', type=non_empty_str, required=True)
        args = parser.parse_args(strict=True)

        regex = re.compile('[a-z]{3,}(?P<chiocciola>@)[a-z]{3,}\.[a-z]{2,}')

        if regex.match(args['email']) is not None and len(args['password']) > 6:
            obj.first_name = args['first_name']
            obj.last_name = args['last_name']
            obj.email = args['email']
            obj.password = args['password']
            obj.save()

            return obj.json(), CREATED
        else:
            return '', BAD_REQUEST

    def delete(self, user_id):
        try:
            obj = User.get(user_id=user_id)
        except User.DoesNotExist:
            return None, NOT_FOUND

        obj.delete_instance()
        return None, NO_CONTENT
