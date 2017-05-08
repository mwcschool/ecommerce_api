from flask import Flask
from flask_restful import Resource, reqparse
import json
import peewee
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
from http.client import BAD_REQUEST
import uuid

import models


def json(self):
    return {
        'item_id': str(self.item_id),
        'name': self.name,
        'price': int(self.price),
        'description': self.description
    }


class Items(Resource):
    def get(self):
        return [obj.json() for obj in models.Item.select()], OK

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('price', type=int, required=True)
        parser.add_argument('description', type=str, required=True)
        try:
            args = parser.parse_args()
        except ValueError:
            return None, BAD_REQUEST

        obj = models.Item.create(
            item_id=uuid.uuid4(),
            name=args["name"],
            price=args["price"],
            description=args["description"]
        )

        return obj.json(), CREATED


class Item(Resource):

    def get(self, item_id):
        try:
            return models.Item.get(models.Item.item_id == item_id).json(), OK
        except models.Item.DoesNotExist:
            return None, NOT_FOUND

    def delete(self, item_id):
        try:
            item = models.Item.get(models.Item.item_id == item_id)
        except models.Item.DoesNotExist:
            return None, NOT_FOUND

        item.delete_instance()
        return None, NO_CONTENT

    def put(self, item_id):
        try:
            obj = models.Item.get(item_id=item_id)
        except models.Item.DoesNotExist:
            return None, NOT_FOUND

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('price', type=int, required=True)
        parser.add_argument('description', type=str, required=True)

        try:
            args = parser.parse_args()
        except ValueError:
            return None, BAD_REQUEST

        obj.name = args["name"]
        obj.price = args["price"]
        obj.description = args["description"]
        obj.save()

        return obj.json(), OK
