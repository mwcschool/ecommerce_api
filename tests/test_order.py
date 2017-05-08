import pytest
import uuid
import json
from peewee import SqliteDatabase
from http.client import OK, NOT_FOUND, NO_CONTENT, CREATED, BAD_REQUEST

from app import app
from models import Order, User

class TestOrders:
    @classmethod
    def setup_class(cls):
        Order._meta.database = SqliteDatabase(':memory:')
        Order.create_table()
        User._meta.database = SqliteDatabase(':memory:')
        User.create_table()
        app.config['TESTING'] = True
        cls.app = app.test_client()

    def setup_method(self):
        Order.delete().execute()
        User.delete().execute()

    def test_get_orders__empty(self):
        resp = self.app.get('/orders/')
        assert resp.status_code == OK
        assert json.loads(resp.data.decode()) == []

    def test_get_orders(self):
        usr1 = User.create(
                user_id=str(uuid.uuid4()),
                first_name='Name',
                last_name='Surname',
                email='email@domain.com',
                password='password'
            )
        ord1 = Order.create(
                order_id=str(uuid.uuid4()),
                total_price=10,
                user=usr1.id
            )
        ord2 = Order.create(
                order_id=str(uuid.uuid4()),
                total_price=7,
                user=usr1.id
            )

        resp = self.app.get('/orders/')
        assert resp.status_code == OK
        assert json.loads(resp.data.decode()) == [ord1.json(), ord2.json()]


    def test_create_order__success(self):
        usr1 = User.create(
                user_id=str(uuid.uuid4()),
                first_name='Name',
                last_name='Surname',
                email='email@domain.com',
                password='password'
            )

        source_order = {
            'total_price': 10,
            'user': usr1.user_id
        }

        resp = self.app.post('/orders/', data=source_order)
        assert resp.status_code == CREATED
        order = json.loads(resp.data.decode())

        assert len(Order.select()) == 1
        assert Order.get(order_id=order['order_id']).json() == order
        order.pop('order_id')
        assert order == source_order

    def test_create_order__failure_missing_field(self):
        usr1 = User.create(
                user_id=str(uuid.uuid4()),
                first_name='Name',
                last_name='Surname',
                email='email@domain.com',
                password='password'
            )
        source_order = {
            'user': usr1.user_id
        }

        resp = self.app.post('/orders/', data=source_order)
        assert resp.status_code == BAD_REQUEST

    def test_create_order__failure_empty_field(self):
        usr1 = User.create(
                user_id=str(uuid.uuid4()),
                first_name='Name',
                last_name='Surname',
                email='email@domain.com',
                password='password'
            )
        source_order = {
            'total_price': None,
            'user': usr1.user_id
        }

        resp = self.app.post('/orders/', data=source_order)
        assert resp.status_code == BAD_REQUEST

    def test_modify_order__success(self):
        usr1 = User.create(
                user_id=str(uuid.uuid4()),
                first_name='Name',
                last_name='Surname',
                email='email@domain.com',
                password='password'
            )
        ord1 = Order.create(
                order_id=str(uuid.uuid4()),
                total_price=10,
                user=usr1.id
            )
        ord2 = Order.create(
                order_id=str(uuid.uuid4()),
                total_price=12,
                user=usr1.id
            )

        updates = {
            'total_price': 7
        }

        resp = self.app.put(
            '/orders/{}'.format(ord1.order_id),
            data=updates
            )
        assert resp.status_code == OK
        ord1_upd = Order.get(Order.order_id == ord1.order_id).json()

        assert ord1_upd['total_price'] == updates['total_price']

    def test_modify_order__failure_non_existing(self):
        usr1 = User.create(
                user_id=str(uuid.uuid4()),
                first_name='Name',
                last_name='Surname',
                email='email@domain.com',
                password='password'
            )
        ord1 = Order.create(
                order_id=str(uuid.uuid4()),
                total_price=10,
                user=usr1.id
            )

        updates = {
            'total_price': 7
        }

        resp = self.app.put(
            '/orders/{}'.format(str(uuid.uuid4())),
            data=updates
            )
        assert resp.status_code == NOT_FOUND