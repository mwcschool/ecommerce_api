import uuid
import json
from peewee import SqliteDatabase
from http.client import OK, NOT_FOUND, NO_CONTENT, CREATED, BAD_REQUEST

from app import app
from models import Order, OrderItem, Item, User


class TestOrders:
    @classmethod
    def setup_class(cls):
        database = SqliteDatabase(':memory:')

        OrderItem._meta.database = database
        Order._meta.database = database
        Item._meta.database = database
        User._meta.database = database

        OrderItem.create_table()
        Order.create_table()
        Item.create_table()
        User.create_table()

        cls.user1 = User.create(
            user_id=str(uuid.uuid4()),
            first_name='Name',
            last_name='Surname',
            email='email@domain.com',
            password='password'
        )
        cls.item1 = Item.create(
            item_id=str(uuid.uuid4()),
            name='Item one',
            price=10,
            description='Item one description'
        )
        cls.item2 = Item.create(
            item_id=str(uuid.uuid4()),
            name='Item two',
            price=10,
            description='Item two description'
        )

        app.config['TESTING'] = True
        cls.app = app.test_client()

    def setup_method(self):
        OrderItem.delete().execute()
        Order.delete().execute()

    def test_get_orders__empty(self):
        resp = self.app.get('/orders/')
        assert resp.status_code == OK
        assert json.loads(resp.data.decode()) == []

    def test_get_orders(self):
        order1 = Order.create(
            order_id=str(uuid.uuid4()),
            total_price=10,
            user=self.user1.id
        )
        OrderItem.create(
            order=order1.id,
            item=self.item1.id,
            quantity=1,
            subtotal=self.item1.price
        )

        order2 = Order.create(
            order_id=str(uuid.uuid4()),
            total_price=7,
            user=self.user1.id
        )
        OrderItem.create(
            order=order2.id,
            item=self.item1.id,
            quantity=1,
            subtotal=self.item1.price
        )

        resp = self.app.get('/orders/')
        assert resp.status_code == OK
        assert json.loads(resp.data.decode()) == [order1.json(), order2.json()]

    def test_create_order__success(self):
        new_order_data = {
            'user': self.user1.user_id,
            'items': json.dumps([
                [self.item1.item_id, 2], [self.item2.item_id, 1]
            ])
        }

        resp = self.app.post('/orders/', data=new_order_data)
        assert resp.status_code == CREATED

        order_from_server = json.loads(resp.data.decode())
        order_from_db = Order.get(Order.order_id == order_from_server['order_id']).json()

        assert len(Order.select()) == 1
        assert order_from_db == order_from_server

        order_from_server.pop('order_id')
        assert order_from_server['user'] == new_order_data['user']
        assert len(order_from_server['items']) == 2

        order_items_ids = [self.item1.item_id, self.item2.item_id]
        assert order_from_server['items'][0]['item_id'] in order_items_ids
        assert order_from_server['items'][1]['item_id'] in order_items_ids

        order_total = (self.item1.price * 2) + self.item2.price
        assert order_from_server['total_price'] == order_total

    def test_create_order__failure_missing_field(self):
        new_order_data = {
            'user': self.user1.user_id
        }

        resp = self.app.post('/orders/', data=new_order_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order__failure_empty_items(self):
        new_order_data = {
            'user': self.user1.user_id,
            'items': json.dumps('')
        }

        resp = self.app.post('/orders/', data=new_order_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order__failure_non_existing_items(self):
        new_order_data = {
            'user': self.user1.user_id,
            'items': json.dumps([
                [str(uuid.uuid4()), 1], [str(uuid.uuid4()), 1]
            ])
        }

        resp = self.app.post('/orders/', data=new_order_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order__failure_non_existing_user(self):
        new_order_data = {
            'total_price': 10,
            'user': str(uuid.uuid4())
        }

        resp = self.app.post('/orders/', data=new_order_data)
        assert resp.status_code == BAD_REQUEST
        assert len(Order.select()) == 0

    def test_create_order__failure_empty_field(self):
        new_order_data = {
            'total_price': None,
            'user': self.user1.user_id
        }

        resp = self.app.post('/orders/', data=new_order_data)
        assert resp.status_code == BAD_REQUEST

    def test_modify_order__success(self):
        order1 = Order.create(
            order_id=str(uuid.uuid4()),
            total_price=10,
            user=self.user1.id
        )
        OrderItem.create(
            order=order1.id,
            item=self.item1.id,
            quantity=1,
            subtotal=self.item1.price
        )

        order2 = Order.create(
            order_id=str(uuid.uuid4()),
            total_price=12,
            user=self.user1.id
        )
        OrderItem.create(
            order=order2.id,
            item=self.item1.id,
            quantity=1,
            subtotal=self.item1.price
        )

        updates = {
            'items':json.dumps([
                    [self.item2.item_id, 2]
                ])
        }

        resp = self.app.put(
            '/orders/{}'.format(order1.order_id),
            data=updates
        )
        assert resp.status_code == OK

        order1_upd = Order.get(Order.order_id == order1.order_id).json()
        total_price = self.item2.price*2
        assert order1_upd['total_price'] == total_price

        order2_db = Order.get(Order.order_id == order2.order_id).json()
        assert order2_db == order2.json()

        order1_items = OrderItem.select().where(OrderItem.order_id==order1.id)
        assert len(order1_items) == 1
        assert order1_items[0].item_id == self.item2.id

    def test_modify_order__failure_non_existing(self):
        Order.create(
            order_id=str(uuid.uuid4()),
            total_price=10,
            user=self.user1.id
        )

        updates = {
            'items':json.dumps([
                    [self.item1.item_id, 1]
                ])
        }

        resp = self.app.put(
            '/orders/{}'.format(str(uuid.uuid4())),
            data=updates
        )
        assert resp.status_code == NOT_FOUND

    def test_modify_order__failure_non_existing_empty_orders(self):
        updates = {
            'items':json.dumps([
                    [self.item1.item_id, 1]
                ])
        }

        resp = self.app.put(
            '/orders/{}'.format(str(uuid.uuid4())),
            data=updates
        )
        assert resp.status_code == NOT_FOUND

    def test_modify_order__failure_changed_order_id(self):
        order1 = Order.create(
            order_id=str(uuid.uuid4()),
            total_price=10,
            user=self.user1.id
        )

        updates = {
            'order_id': str(uuid.uuid4())
        }

        resp = self.app.put(
            '/orders/{}'.format(order1.order_id),
            data=updates
        )
        assert resp.status_code == BAD_REQUEST

    def test_modify_order__failure_changed_user(self):
        order1 = Order.create(
            order_id=str(uuid.uuid4()),
            total_price=10,
            user=self.user1.id
        )

        updates = {
            'user': str(uuid.uuid4())
        }

        resp = self.app.put(
            '/orders/{}'.format(order1.order_id),
            data=updates
        )
        assert resp.status_code == BAD_REQUEST

    def test_modify_order__failure_empty_field(self):
        order1 = Order.create(
            order_id=str(uuid.uuid4()),
            total_price=10,
            user=self.user1.id
        )

        updates = {
            'items':json.dumps('')
        }

        resp = self.app.put(
            '/orders/{}'.format(order1.order_id),
            data=updates
        )
        assert resp.status_code == BAD_REQUEST

    def test_delete_order__success(self):
        order1 = Order.create(
            order_id=str(uuid.uuid4()),
            total_price=10,
            user=self.user1.id
        )
        item1 = Item.create(
            item_id=str(uuid.uuid4()),
            name='Item one',
            price=10,
            description='Item one description'
        )
        OrderItem.create(
            order=order1.id,
            item=self.item1.id,
            quantity=1,
            subtotal=self.item1.price
        )
        order2 = Order.create(
            order_id=str(uuid.uuid4()),
            total_price=12,
            user=self.user1.id
        )
        OrderItem.create(
            order=order2.id,
            item=self.item1.id,
            quantity=1,
            subtotal=self.item1.price
        )

        resp = self.app.delete('/orders/{}'.format(order1.order_id))
        assert resp.status_code == NO_CONTENT

        orders = Order.select()
        assert len(orders) == 1
        assert Order.get(Order.order_id == order2.order_id)

        order_items = OrderItem.select().where(OrderItem.order_id == order1.id)
        assert len(order_items) == 0

    def test_delete_order__failure_non_existing(self):
        Order.create(
            order_id=str(uuid.uuid4()),
            total_price=10,
            user=self.user1.id
        )
        Order.create(
            order_id=str(uuid.uuid4()),
            total_price=12,
            user=self.user1.id
        )

        resp = self.app.delete('/orders/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND
        assert len(Order.select()) == 2

    def test_delete_order__failure_non_existing_empty_orders(self):
        resp = self.app.delete('/orders/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND
