from flask_restful import Resource, reqparse
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
from http.client import BAD_REQUEST
import uuid
from models import Item
import utils


class ItemsResource(Resource):
    def get(self):
        return [obj.json() for obj in Item.select()], OK

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('price', type=int, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('category', type=str, required=True)
        args = parser.parse_args(strict=True)
        try:
            utils.non_empty_str(args['name'], 'name')
        except ValueError:
            return None, BAD_REQUEST

        obj = Item.create(
            item_id=uuid.uuid4(),
            name=args["name"],
            price=args["price"],
            description=args["description"],
            category=args["category"]
        )

        return obj.json(), CREATED


class ItemResource(Resource):

    def get(self, item_id):
        try:
            return Item.get(Item.item_id == item_id).json(), OK
        except Item.DoesNotExist:
            return None, NOT_FOUND

    def delete(self, item_id):
        try:
            item = Item.get(Item.item_id == item_id)
        except Item.DoesNotExist:
            return None, NOT_FOUND

        item.delete_instance()
        return None, NO_CONTENT

    def put(self, item_id):
        try:
            obj = Item.get(item_id=item_id)
        except Item.DoesNotExist:
            return None, NOT_FOUND

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('price', type=int, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('category', type=str, required=True)
        args = parser.parse_args(strict=True)
        try:
            utils.non_empty_str(args['name'], 'name')
        except ValueError:
            return None, BAD_REQUEST

        obj.name = args["name"]
        obj.price = args["price"]
        obj.description = args["description"]
        obj.category = args["category"]
        obj.save()

        return obj.json(), OK
