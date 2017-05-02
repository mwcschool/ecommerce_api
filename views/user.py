import uuid
from models import User
import json
from http.client import OK, CREATED, NOT_FOUND, NO_CONTENT
from flask_restful import Api, Resource, reqparse

def non_empty_str(val, name):
	if not str(val).strip():
		raise ValueError('The argument {} is not empty'.format(name))
	return str(val)

class UserResource(Resource):
	def post(self):
		parser = reqparse.RequestParser()
		parser.add_argument('first_name', type=non_empty_str, required=True)
		parser.add_argument('last_name', type=non_empty_str, required=True)
		parser.add_argument('email', type=non_empty_str, required=True)
		parser.add_argument('password', type=non_empty_str, required=True)
		args = parser.parse_args(strict=True)
		obj = User.create(
			user_id=uuid.uuid4(),
			first_name=args['first_name'],
			last_name=args['last_name'],
			email=args['email'],
			password=args['password']
		)

		return {'user_id': obj.user_id}, CREATED


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

		obj.first_name=args['first_name']
		obj.last_name=args['last_name']
		obj.email=args['email']
		obj.password=['password']
		obj.save()

		return obj.json(), CREATED


	def delete(self, user_id):
		try:
			obj = User.get(user_id=user_id)
		except User.DoesNotExist:
			return None, NOT_FOUND

		obj.delete_instance()
		return None, NO_CONTENT







