from flask_restful import reqparse, Resource
from http.client import OK, NOT_FOUND, NO_CONTENT, CREATED, BAD_REQUEST
import uuid

from models import Order, User


def is_valid_uuid(user_id):
    return uuid.UUID(user_id, version=4)


class OrdersResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('total_price', type=float, required=True)
        parser.add_argument('user', type=is_valid_uuid, required=True)
        args = parser.parse_args(strict=True)

        try:
            user = User.get(User.user_id == args['user'])
        except User.DoesNotExist:
            return None, BAD_REQUEST

        order = Order.create(
            order_id=uuid.uuid4(),
            total_price=float(args['total_price']),
            user=user.id
        )
        return order.json(), CREATED

    def get(self):
        return [order.json() for order in Order.select()], OK


class OrderResource(Resource):
    def get(self, order_id):
        try:
            return Order.get(order_id=order_id).json(), OK
        except Order.DoesNotExist:
            return None, NOT_FOUND

    def put(self, order_id):
        try:
            order = Order.get(order_id=order_id)
        except Order.DoesNotExist:
            return None, NOT_FOUND

        parser = reqparse.RequestParser()
        parser.add_argument('total_price', type=float, required=True)
        args = parser.parse_args(strict=True)

        order.total_price = args['total_price']
        order.save()

        return order.json(), OK

    def delete(self, order_id):
        try:
            order = Order.get(order_id=order_id)
        except Order.DoesNotExist:
            return None, NOT_FOUND

        order.delete_instance()
        return None, NO_CONTENT
