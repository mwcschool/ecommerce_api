import uuid
from models import User, Reset
import auth
from flask import g
from http.client import CREATED, NOT_FOUND, NO_CONTENT, BAD_REQUEST, UNAUTHORIZED
from flask_restful import Resource, reqparse, request
import re
import utils
from datetime import datetime, timedelta
from schemas import ResetRequestSchema
from marshmallow_jsonschema import JSONSchema
from jsonschema import validate


def valid_email(email):
    return re.match('[a-z]{3,}(?P<at>@)[a-z]{3,}(?P<point>\.)[a-z]{2,}', email)


class UsersResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=utils.non_empty_str, required=True)
        parser.add_argument('last_name', type=utils.non_empty_str, required=True)
        parser.add_argument('email', type=utils.non_empty_str, required=True)
        parser.add_argument('password', type=utils.non_empty_str, required=True)
        args = parser.parse_args(strict=True)

        if valid_email(args['email']) and len(args['password']) > 6:
            obj = User.create(
                uuid=uuid.uuid4(),
                first_name=args['first_name'],
                last_name=args['last_name'],
                email=args['email'],
                password=auth.crypt_password(args['password'])
            )

            return obj.json(), CREATED
        else:
            return '', BAD_REQUEST


class UserResource(Resource):
    @auth.login_required
    def put(self, uuid):
        try:
            obj = User.get(uuid=uuid)
        except User.DoesNotExist:
            return None, NOT_FOUND

        if obj != g.current_user:
            return '', UNAUTHORIZED

        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=utils.non_empty_str, required=True)
        parser.add_argument('last_name', type=utils.non_empty_str, required=True)
        parser.add_argument('email', type=utils.non_empty_str, required=True)
        parser.add_argument('password', type=utils.non_empty_str, required=True)
        args = parser.parse_args(strict=True)

        if valid_email(args['email']) is not None and len(args['password']) > 6:
            obj.first_name = args['first_name']
            obj.last_name = args['last_name']
            obj.email = args['email']
            obj.password = auth.crypt_password(args['password'])
            obj.save()

            return obj.json(), CREATED
        else:
            return '', BAD_REQUEST

    @auth.login_required
    def delete(self, uuid):
        try:
            obj = User.get(uuid=uuid)
        except User.DoesNotExist:
            return None, NOT_FOUND

        if obj != g.current_user:
            return '', UNAUTHORIZED

        obj.status = 'deleted'
        obj.save()

        return None, NO_CONTENT


class ResetResource(Resource):
    def post(self):
        args = request.form
        validate(args, JSONSchema().dump(ResetRequestSchema()).data)

        if not valid_email(args['email']):
            return None, BAD_REQUEST

        try:
            user = User.get(User.email == args['email'])
        except User.DoesNotExist:
            return None, NO_CONTENT

        Reset.update(enable=False).where(Reset.user == user).execute()

        Reset.create(
            uuid=uuid.uuid4(),
            user=user,
            expiration_date=datetime.now() + timedelta(hours=1)
        )

        return None, NO_CONTENT
