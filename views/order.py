from flask_restful import reqparse, Resource
from http.client import OK
import uuid

from models import Order


class OrdersResource(Resource):
    def get(self):
        return [order.json() for order in Order.select()], OK


class OrderResource(Resource):
    def get(self, order_id):
        try:
            return Order.get(order_id=order_id).json(), OK
        except Order.DoesNotExist:
            return None, NOT_FOUND
