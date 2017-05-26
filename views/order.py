from flask_restful import reqparse, Resource
from http.client import OK, NOT_FOUND, NO_CONTENT, CREATED, BAD_REQUEST
import uuid
import json

from models import Order, OrderItem, Item, User, database


def is_valid_uuid(user_id):
    return uuid.UUID(user_id, version=4)


def is_valid_item_list(json_item_list):
    return json.loads(json_item_list)


class OrdersResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user', type=is_valid_uuid, required=True)
        parser.add_argument('items', type=is_valid_item_list, required=True)
        args = parser.parse_args(strict=True)

        try:
            user = User.get(User.uuid == args['user'])
        except User.DoesNotExist:
            return None, BAD_REQUEST

        total_price = 0

        items = args['items']
        items_uuid = [i[0] for i in items]
        items_query = Item.select().where(Item.uuid << items_uuid)

        if items_query.count() != len(items) or len(items) == 0:
            return None, BAD_REQUEST

        for item in items_query:
            item_quantity = [x[1] for x in items if x[0] == str(item.uuid)][0]
            total_price += float(item.price * item_quantity)

        for item in items_query:
            item_quantity = [x[1] for x in items if x[0] == str(item.item_id)][0]
            if item_quantity > item.availability:
                return None, BAD_REQUEST

        with database.transaction():
            order = Order.create(
                uuid=uuid.uuid4(),
                total_price=total_price,
                user=user.id
            )

            for item in items_query:
                item_quantity = [x[1] for x in items if x[0] == str(item.uuid)][0]
                OrderItem.create(
                    order=order,
                    item=item.id,
                    quantity=item_quantity,
                    subtotal=float(item.price * item_quantity)
                )
                item.availability = (item.availability - item_quantity)
                item.save()

        return order.json(), CREATED

    def get(self):
        return [order.json() for order in Order.select()], OK


class OrderResource(Resource):
    def get(self, uuid):
        try:
            return Order.get(uuid=uuid).json(), OK
        except Order.DoesNotExist:
            return None, NOT_FOUND

    def put(self, uuid):
        try:
            order = Order.get(uuid=uuid)
        except Order.DoesNotExist:
            return None, NOT_FOUND

        parser = reqparse.RequestParser()
        parser.add_argument('items', type=is_valid_item_list, required=True)
        args = parser.parse_args(strict=True)

        total_price = 0

        items = args['items']
        uuid = [i[0] for i in items]
        items_query = Item.select().where(Item.uuid << uuid)

        if items_query.count() != len(items) or len(items) == 0:
            return None, BAD_REQUEST

        for item in items_query:
            item_quantity = [x[1] for x in items if x[0] == str(item.uuid)][0]
            total_price += float(item.price * item_quantity)

        for item in items_query:
            item_quantity = [x[1] for x in items if x[0] == str(item.item_id)][0]
            if item_quantity > item.availability:
                return None, BAD_REQUEST

        with database.transaction():
            temp_query = OrderItem.select().where(OrderItem.order == order.id)
            for order_item in temp_query:
                item_temp_query = Item.get(Item.id == order_item.item)
                item_temp_query.availability = (item_temp_query.availability + order_item.quantity)
                item_temp_query.save()

            OrderItem.delete().where(OrderItem.order == order.id).execute()

            for item in items_query:
                item_quantity = [x[1] for x in items if x[0] == str(item.uuid)][0]
                OrderItem.create(
                    order=order,
                    item=item.id,
                    quantity=item_quantity,
                    subtotal=float(item.price * item_quantity)
                )
                item.availability = (item.availability - item_quantity)
                item.save()

            order.total_price = total_price
            order.save()

        return order.json(), OK

    def delete(self, uuid):
        try:
            order = Order.get(Order.uuid == uuid)
        except Order.DoesNotExist:
            return None, NOT_FOUND

        with database.transaction():
            order_items = OrderItem.select().where(OrderItem.order == order.id)

            for order_item in order_items:
                temp_query = Item.get(Item.id == order_item.item)
                temp_query.availability = temp_query.availability + order_item.quantity
                temp_query.save()

            for order_item in order_items:
                order_item.delete_instance()

            order.delete_instance()

        return None, NO_CONTENT
