import uuid
import json
from http.client import OK, NOT_FOUND, NO_CONTENT, CREATED, BAD_REQUEST

from models import Order, OrderItem

from .base_test import BaseTest


class TestOrders(BaseTest):
    def setup_method(self):
        super(TestOrders, self).setup_method()
        self.user1 = self.create_user()
        self.item1 = self.create_item()
        self.item2 = self.create_item()

        self.order_items = [
            [self.item1, 1], [self.item2, 2]
        ]

    def test_get_orders__empty(self):
        resp = self.app.get('/orders/')
        assert resp.status_code == OK
        assert json.loads(resp.data.decode()) == []

    def test_get_orders(self):
        order1 = self.create_order(self.user1)
        order2 = self.create_order(self.user1)

        resp = self.app.get('/orders/')
        assert resp.status_code == OK
        assert json.loads(resp.data.decode()) == [order1.json(), order2.json()]

    def test_get_order__empty(self):
        resp= self.app.get('/orders/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_get_order__failure_non_existing_order(self):
        order1 = Order.create(
            uuid=uuid.uuid4(),
            total_price=10,
            user=self.user1,
        )
        OrderItem.create(
            order=order1,
            item=self.item1,
            quantity=1,
            subtotal=self.item1.price,
        )

        resp= self.app.get('/orders/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_get_order__success(self):
        order1 = Order.create(
            uuid=uuid.uuid4(),
            total_price=10,
            user=self.user1,
        )
        OrderItem.create(
            order=order1,
            item=self.item1,
            quantity=1,
            subtotal=self.item1.price,
        )

        order2 = Order.create(
            uuid=uuid.uuid4(),
            total_price=10,
            user=self.user1,
        )
        OrderItem.create(
            order=order2,
            item=self.item1,
            quantity=1,
            subtotal=self.item1.price,
        )

        resp = self.app.get('/orders/{}'.format(order1.uuid))
        assert resp.status_code == OK

        order_from_server = json.loads(resp.data.decode())

        assert order_from_server == order1.json()

    def test_create_order__success(self):
        new_order_data = {
            'user': self.user1.uuid,
            'items': json.dumps([
                [str(self.item1.uuid), 2], [str(self.item2.uuid), 1]
            ])
        }

        resp = self.app.post('/orders/', data=new_order_data)
        assert resp.status_code == CREATED

        order_from_server = json.loads(resp.data.decode())
        order_from_db = Order.get(Order.uuid == order_from_server['uuid']).json()

        assert len(Order.select()) == 1
        assert order_from_db == order_from_server

        order_from_server.pop('uuid')
        assert order_from_server['user'] == str(new_order_data['user'])
        assert len(order_from_server['items']) == 2

        order_items_ids = [str(self.item1.uuid), str(self.item2.uuid)]
        assert order_from_server['items'][0]['uuid'] in order_items_ids
        assert order_from_server['items'][1]['uuid'] in order_items_ids

        order_total = (self.item1.price * 2) + self.item2.price
        assert order_from_server['total_price'] == order_total

    def test_create_order__failure_missing_field(self):
        new_order_data = {
            'user': self.user1.uuid
        }

        resp = self.app.post('/orders/', data=new_order_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order__failure_empty_items(self):
        new_order_data = {
            'user': self.user1.uuid,
            'items': json.dumps('')
        }

        resp = self.app.post('/orders/', data=new_order_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order__failure_non_existing_items(self):
        new_order_data = {
            'user': self.user1.uuid,
            'items': json.dumps([
                [str(uuid.uuid4()), 1], [str(uuid.uuid4()), 1]
            ])
        }

        resp = self.app.post('/orders/', data=new_order_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order__failure_non_existing_user(self):
        new_order_data = {
            'user': str(uuid.uuid4()),
            'items': json.dumps([
                [str(self.item1.uuid), 1]
            ])
        }

        resp = self.app.post('/orders/', data=new_order_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_modify_order__success(self):
        order1 = self.create_order(self.user1)
        order2 = self.create_order(self.user1)

        updates = {
            'items': json.dumps([
                [str(self.item2.uuid), 2]
            ])
        }

        resp = self.app.put(
            '/orders/{}'.format(order1.uuid),
            data=updates
        )
        assert resp.status_code == OK

        order1_upd = Order.get(Order.uuid == order1.uuid).json()
        total_price = self.item2.price * 2
        assert order1_upd['total_price'] == total_price

        order2_db = Order.get(Order.uuid == order2.uuid).json()
        assert order2_db == order2.json()

        order1_items = OrderItem.select().where(OrderItem.order == order1)
        assert len(order1_items) == 1
        assert str(order1_items[0].item.uuid) == str(self.item2.uuid)

    def test_modify_order__failure_non_existing(self):
        self.create_order(self.user1)

        updates = {
            'items': json.dumps([
                [str(self.item1.uuid), 1]
            ])
        }

        resp = self.app.put(
            '/orders/{}'.format(str(uuid.uuid4())),
            data=updates
        )
        assert resp.status_code == NOT_FOUND

    def test_modify_order__failure_non_existing_empty_orders(self):
        updates = {
            'items': json.dumps([
                [str(self.item1.uuid), 1]
            ])
        }

        resp = self.app.put(
            '/orders/{}'.format(str(uuid.uuid4())),
            data=updates
        )
        assert resp.status_code == NOT_FOUND

    def test_modify_order__failure_changed_order_id(self):
        order1 = self.create_order(self.user1)

        updates = {
            'uuid': str(uuid.uuid4())
        }

        resp = self.app.put(
            '/orders/{}'.format(order1.uuid),
            data=updates
        )
        assert resp.status_code == BAD_REQUEST

    def test_modify_order__failure_changed_user(self):
        order1 = self.create_order(self.user1)

        updates = {
            'user': str(uuid.uuid4())
        }

        resp = self.app.put(
            '/orders/{}'.format(order1.uuid),
            data=updates
        )
        assert resp.status_code == BAD_REQUEST

    def test_modify_order__failure_empty_field(self):
        order1 = self.create_order(self.user1)

        updates = {
            'items': json.dumps('')
        }

        resp = self.app.put(
            '/orders/{}'.format(order1.uuid),
            data=updates
        )
        assert resp.status_code == BAD_REQUEST

    def test_delete_order__success(self):
        order1 = self.create_order(self.user1)
        order2 = self.create_order(self.user1)

        resp = self.app.delete('/orders/{}'.format(order1.uuid))
        assert resp.status_code == NO_CONTENT

        orders = Order.select()
        assert len(orders) == 1
        assert Order.get(Order.uuid == order2.uuid)

        order_items = OrderItem.select().where(OrderItem.order == order1)
        assert len(order_items) == 0

    def test_delete_order__failure_non_existing(self):
        self.create_order(self.user1)
        self.create_order(self.user1)

        resp = self.app.delete('/orders/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND
        assert len(Order.select()) == 2

    def test_delete_order__failure_non_existing_empty_orders(self):
        resp = self.app.delete('/orders/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND
