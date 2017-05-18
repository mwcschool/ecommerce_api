from flask import Flask
from flask_restful import Api
from models import database

from views import item
from views.order import OrderResource, OrdersResource
from views.user import UserResource, UsersResource

app = Flask(__name__)
api = Api(app)


@app.before_request
def database_connect():
    if database.is_closed():
        database.connect()


@app.teardown_request
def database_disconnect(response):
    if not database.is_closed():
        database.close()
    return response


api.add_resource(item.ItemsResource, '/items/')
api.add_resource(item.ItemResource, '/item/<uuid:uuid>')
api.add_resource(UsersResource, '/users/')
api.add_resource(UserResource, '/users/<uuid:uuid>', methods=['put', 'delete'])
api.add_resource(OrdersResource, '/orders/')
api.add_resource(OrderResource, '/orders/<uuid:uuid>')
