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

        Order._meta.database = database
        Item._meta.database = database
        User._meta.database = database

        Order.create_table()
        Item.create_table()
        User.create_table()

        app.config['TESTING'] = True
        cls.app = app.test_client()

    def setup_method(self):
        OrderItem.delete().execute()
        Order.delete().execute()
        Item.delete().execute()
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
        itm1 = Item.create(
            item_id=str(uuid.uuid4()),
            name='Item one',
            price=10,
            description='Item one description'
        )
        ord1 = Order.create(
            order_id=str(uuid.uuid4()),
            total_price=10,
            user=usr1.id
        )
        OrderItem.create(
            order=ord1.id,
            item=itm1.id,
            quantity=1,
            subtotal=itm1.price
        )

        ord2 = Order.create(
            order_id=str(uuid.uuid4()),
            total_price=7,
            user=usr1.id
        )
        OrderItem.create(
            order=ord2.id,
            item=itm1.id,
            quantity=1,
            subtotal=itm1.price
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

        new_order_data = {
            'total_price': 10,
            'user': usr1.user_id
        }

        resp = self.app.post('/orders/', data=new_order_data)
        assert resp.status_code == CREATED

        order_from_server = json.loads(resp.data.decode())
        order_from_db = Order.get(Order.order_id == order_from_server['order_id']).json()

        assert len(Order.select()) == 1
        assert order_from_db == order_from_server
        order_from_server.pop('order_id')
        assert order_from_server == new_order_data

    def test_create_order__failure_missing_field(self):
        usr1 = User.create(
            user_id=str(uuid.uuid4()),
            first_name='Name',
            last_name='Surname',
            email='email@domain.com',
            password='password'
        )
        new_order_data = {
            'user': usr1.user_id
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
        assert len(User.select()) == 0

    def test_create_order__failure_empty_field(self):
        usr1 = User.create(
            user_id=str(uuid.uuid4()),
            first_name='Name',
            last_name='Surname',
            email='email@domain.com',
            password='password'
        )
        new_order_data = {
            'total_price': None,
            'user': usr1.user_id
        }

        resp = self.app.post('/orders/', data=new_order_data)
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

        ord2_db = Order.get(Order.order_id == ord2.order_id).json()
        assert ord2_db == ord2.json()

    def test_modify_order__failure_non_existing(self):
        usr1 = User.create(
            user_id=str(uuid.uuid4()),
            first_name='Name',
            last_name='Surname',
            email='email@domain.com',
            password='password'
        )
        Order.create(
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

    def test_modify_order__failure_non_existing_empty_orders(self):
        updates = {
            'total_price': 7
        }

        resp = self.app.put(
            '/orders/{}'.format(str(uuid.uuid4())),
            data=updates
        )
        assert resp.status_code == NOT_FOUND

    def test_modify_order__failure_changed_order_id(self):
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
            'order_id': str(uuid.uuid4())
        }

        resp = self.app.put(
            '/orders/{}'.format(ord1.order_id),
            data=updates
        )
        assert resp.status_code == BAD_REQUEST

    def test_modify_order__failure_changed_user(self):
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
            'user': str(uuid.uuid4())
        }

        resp = self.app.put(
            '/orders/{}'.format(ord1.order_id),
            data=updates
        )
        assert resp.status_code == BAD_REQUEST

    def test_modify_order__failure_empty_field(self):
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
            'total_price': None
        }

        resp = self.app.put(
            '/orders/{}'.format(ord1.order_id),
            data=updates
        )
        assert resp.status_code == BAD_REQUEST

    def test_delete_order__success(self):
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
        itm1 = Item.create(
            item_id=str(uuid.uuid4()),
            name='Item one',
            price=10,
            description='Item one description'
        )
        OrderItem.create(
            order=ord1.id,
            item=itm1.id,
            quantity=1,
            subtotal=itm1.price
        )
        ord2 = Order.create(
            order_id=str(uuid.uuid4()),
            total_price=12,
            user=usr1.id
        )
        OrderItem.create(
            order=ord2.id,
            item=itm1.id,
            quantity=1,
            subtotal=itm1.price
        )

        resp = self.app.delete('/orders/{}'.format(ord1.order_id))
        assert resp.status_code == NO_CONTENT

        orders = Order.select()
        assert len(orders) == 1
        assert Order.get(Order.order_id == ord2.order_id)

        order_items = OrderItem.select().where(OrderItem.order_id == ord1.id)
        assert len(order_items) == 0

    def test_delete_order__failure_non_existing(self):
        usr1 = User.create(
            user_id=str(uuid.uuid4()),
            first_name='Name',
            last_name='Surname',
            email='email@domain.com',
            password='password'
        )
        Order.create(
            order_id=str(uuid.uuid4()),
            total_price=10,
            user=usr1.id
        )
        Order.create(
            order_id=str(uuid.uuid4()),
            total_price=12,
            user=usr1.id
        )

        resp = self.app.delete('/orders/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND
        assert len(Order.select()) == 2

    def test_delete_order__failure_non_existing_empty_orders(self):
        resp = self.app.delete('/orders/{}'.format(str(uuid.uuid4())))
        assert resp.status_code == NOT_FOUND
