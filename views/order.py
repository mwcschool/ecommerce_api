from flask_restful import reqparse, Resource
from http.client import OK, NOT_FOUND, NO_CONTENT, CREATED, BAD_REQUEST
import uuid

from models import Order, OrderItem, Item, User, database


def is_valid_uuid(user_id):
    return uuid.UUID(user_id, version=4)


class OrdersResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user', type=is_valid_uuid, required=True)
        parser.add_argument('items', type=list, required=True)
        args = parser.parse_args(strict=True)

        try:
            user = User.get(User.user_id == args['user'])
        except User.DoesNotExist:
            return None, BAD_REQUEST

        total_price = 0

        items = args['items']
        items_id = [i[0] for i in items]
        items_query = Item.select().where(Item.item_id << items_id)

        if items_query.count() != len(items):
            return None, BAD_REQUEST

        for item in items_query:
            total_price += item.price

        with database.transaction():
            order = Order.create(
                order_id=uuid.uuid4(),
                total_price=float(total_price),
                user=user.id
            )

            for item in items_query:
                item_qty = [x[1] for x in items if x[0] == item.item_id][0]
                OrderItem.create(
                    order=order.id,
                    item=item.id,
                    quantity=item_qty,
                    subtotal=float(item.price * item_qty)
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
            order = Order.get(Order.order_id == order_id)
        except Order.DoesNotExist:
            return None, NOT_FOUND

        with database.transaction():
            order_items = OrderItem.select().where(
                    OrderItem.order_id == order.id)

            for order_item in order_items:
                order_item.delete_instance()

            order.delete_instance()

        return None, NO_CONTENT
