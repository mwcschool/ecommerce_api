import uuid
from models import User
import auth
from flask import g, request
from http.client import CREATED, NOT_FOUND, NO_CONTENT, BAD_REQUEST, UNAUTHORIZED
from flask_restful import Resource, reqparse
import re
from passlib.hash import pbkdf2_sha256
from marshmallow import ValidationError


def valid_email(email):
    return re.match('[a-z]{3,}(?P<at>@)[a-z]{3,}(?P<point>\.)[a-z]{2,}', email)


def crypt_password(password):
    crypt = pbkdf2_sha256.hash(password)

    return crypt


class UsersResource(Resource):
    def post(self):
        json_data = request.get_json()
        try:
            User.verify_json(json_data)
        except ValidationError as err:
            return {'message': err.message}, NOT_FOUND

        if valid_email(json_data['email']) and len(json_data['password']) > 6:
            obj = User.create(
                uuid=uuid.uuid4(),
                first_name=json_data['first_name'],
                last_name=json_data['last_name'],
                email=json_data['email'],
                password=crypt_password(json_data['password'])
            )

            return obj.json(), CREATED
        else:
            return '', BAD_REQUEST


class UserResource(Resource):
    @auth.login_required
    def put(self, uuid):
        json_data = request.get_json()
        try:
            obj = User.verify_json(json_data)
        except ValidationError as err:
            return None, NOT_FOUND

        if obj != g.current_user:
            return '', UNAUTHORIZED

        if valid_email(json_data['email']) is not None and len(json_data['password']) > 6:
            obj.first_name = json_data['first_name']
            obj.last_name = json_data['last_name']
            obj.email = json_data['email']
            obj.password = crypt_password(json_data['password'])
            obj.save()

            return obj.json(), CREATED
        else:
            return '', BAD_REQUEST

    @auth.login_required
    def delete(self, uuid):
        json_data = request.get_json()
        try:
            obj = User.verify_json(json_data)
        except ValidationError:
            return None, NOT_FOUND

        if obj != g.current_user:
            return '', UNAUTHORIZED

        obj.status = 'deleted'
        obj.save()

        return None, NO_CONTENT
