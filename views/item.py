import flask as f
import flask_restful as rest
import json
import peewee as p
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
import uuid

import models as m


def json(self):
    return {
        'item_id': str(self.item_id),
        'name': self.name,
        'price': self.price,
        'description': self.description
    }


class Items(rest.Resource):
    def get(self):
        return [obj.json() for obj in m.Item.select()], OK

    def post(self):
        parser = rest.reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('price', type=int, required=True)
        parser.add_argument('description', type=str, required=True)

        obj = m.Item.create(
            item_id=uuid.uuid4(),
            name=args["name"],
            price=args["price"],
            description=args["description"]
        )

        return obj.json(), OK


class Item(rest.Resource):

    def get(self, item_id):
        try:
            return m.Item.get(m.Item.item_id == item_id)
        except m.Item.DoesNotExist:
            return None, NOT_FOUND

    def delete(self, item_id):
        try:
            item = m.Item.get(m.Item.item_id == item_id)
        except m.Item.DoesNotExist:
            return None, NOT_FOUND

        item.delete_instance()
        return None, NO_CONTENT

    def put(self, item_id):
        try:
            obj = m.Item.get(item_id=item_id)
        except m.Item.DoesNotExist:
            return None, NOT_FOUND

        parser = rest.reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('price', type=str, required=True)
        parser.add_argument('description', type=str, required=True)

        obj.name = args["name"]
        obj.price = args["price"]
        obj.description = args["description"]
        obj.save()

        return ogj.json(), OK
