import uuid
from models import User
import auth
from flask import g, request
from http.client import CREATED, NOT_FOUND, NO_CONTENT, BAD_REQUEST, UNAUTHORIZED
from flask_restful import Resource, reqparse
import re
from passlib.hash import pbkdf2_sha256
from jsonschema.exceptions import ValidationError


def valid_email(email):
    return re.match('[a-z]{3,}(?P<at>@)[a-z]{3,}(?P<point>\.)[a-z]{2,}', email)


def crypt_password(password):
    crypt = pbkdf2_sha256.hash(password)

    return crypt


class UsersResource(Resource):
    def post(self):
        json = request.get_json()
        try:
            User.verify_json(json)
        except ValidationError as err:
            return {'message': err.message}, BAD_REQUEST

        if valid_email(json['email']) and len(json['password']) > 6:
            user = User.create(
                uuid=uuid.uuid4(),
                first_name=json['first_name'],
                last_name=json['last_name'],
                email=json['email'],
                password=crypt_password(json['password'])
            )

            return user.json(), CREATED
        else:
            return '', BAD_REQUEST


class UserResource(Resource):
    @auth.login_required
    def put(self, uuid):
        json = request.get_json()
        try:
            User.verify_json(json)
        except ValidationError as err:
            return None, BAD_REQUEST

        user = User.get(uuid=uuid)
        if user != g.current_user:
            return '', UNAUTHORIZED

        if valid_email(json['email']) is not None and len(json['password']) > 6:
            user.first_name = json['first_name']
            user.last_name = json['last_name']
            user.email = json['email']
            user.password = crypt_password(json['password'])
            user.save()

            return user.json(), CREATED
        else:
            return '', BAD_REQUEST

    @auth.login_required
    def delete(self, uuid):
        json = request.get_json()
        try:
            user = User.get(uuid=uuid)
        except User.DoesNotExist:
            return None, NOT_FOUND

        if user != g.current_user:
            return '', UNAUTHORIZED

        user.status = 'deleted'
        user.save()

        return None, NO_CONTENT
