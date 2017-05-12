import uuid
from models import Address
from http.client import CREATED, NOT_FOUND, NO_CONTENT, BAD_REQUEST
from flask_restful import Resource, reqparse
import re


def non_empty_str(val, name):
    if not str(val).strip():
        raise ValueError('The argument {} is not empty'.format(name))
    return str(val)


class AddressesResource(Resource):
    def post(self):
        pass


class AddressResource(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass
