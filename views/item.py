from flask_restful import Resource, reqparse
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
from http.client import BAD_REQUEST
import uuid
from models import Item
import utils
import auth


class ItemsResource(Resource):
    def get(self):
        return [obj.json() for obj in Item.select()], OK

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('price', type=int, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('category', type=str, required=True)
        parser.add_argument('availability', type=int, required=True)
        args = parser.parse_args(strict=True)
        try:
            utils.non_empty_str(args['name'], 'name')
        except ValueError:
            return None, BAD_REQUEST

        if args["availability"] < 0:
            return None, BAD_REQUEST

        obj = Item.create(
            uuid=uuid.uuid4(),
            name=args["name"],
            price=args["price"],
            description=args["description"],
            category=args["category"],
            availability=args["availability"]
        )

        return obj.json(), CREATED


class ItemResource(Resource):

    def get(self, uuid):
        try:
            return Item.get(Item.uuid == uuid).json(), OK
        except Item.DoesNotExist:
            return None, NOT_FOUND

    @auth.login_required
    def delete(self, uuid):
        try:
            item = Item.get(Item.uuid == uuid)
        except Item.DoesNotExist:
            return None, NOT_FOUND

        item.delete_instance()
        return None, NO_CONTENT

    @auth.login_required
    def put(self, uuid):
        try:
            obj = Item.get(uuid=uuid)
        except Item.DoesNotExist:
            return None, NOT_FOUND

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('price', type=int, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('category', type=str, required=True)
        parser.add_argument('availability', type=int, required=True)
        args = parser.parse_args(strict=True)
        try:
            utils.non_empty_str(args['name'], 'name')
        except ValueError:
            return None, BAD_REQUEST

        if args["availability"] < 0:
            return None, BAD_REQUEST

        obj.name = args["name"]
        obj.price = args["price"]
        obj.description = args["description"]
        obj.category = args["category"]
        obj.availability = args["availability"]
        obj.save()

        return obj.json(), OK
