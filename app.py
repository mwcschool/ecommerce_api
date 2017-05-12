from flask import Flask
from flask_restful import Api
from models import database
import views.order
from views import item
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


api.add_resource(views.order.OrdersResource, '/orders/')
api.add_resource(views.order.OrderResource, '/orders/<uuid:order_id>')
api.add_resource(item.ItemsResource, '/items/')
api.add_resource(item.ItemResource, '/item/<uuid:item_id>')
api.add_resource(UsersResource, '/users/')
api.add_resource(UserResource, '/users/<uuid:user_id>')
