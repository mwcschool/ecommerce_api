from flask import Flask
from flask_restful import Api

from models import database
import views.order

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
