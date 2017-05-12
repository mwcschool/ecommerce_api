from flask import Flask
from flask_restful import Api
from models import database
from views import item

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


api.add_resource(item.Items_Resource, '/items/')
api.add_resource(item.Item_Resource, '/item/<uuid:item_id>')
