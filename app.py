from flask import Flask
from flask_restful import Api

from models import database

import views.item as vi


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


api.add_resource(vi.Items, '/items/')
api.add_resource(vi.Item, '/item/<uuid:item_id>')
