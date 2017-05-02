from flask_restful import reqparse, Resource
from http.client import OK
import uuid

from models import Order


class OrdersResource(Resource):
    def get(self):
        return [order.json() for order in Order.select()], OK
