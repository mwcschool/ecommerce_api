
import flask
import flask_restful
import json
import peewee


database = SqliteDatabase('database.db')


app = Flask(__name__)
api = Api(app)


class Item(BaseModel):
    item_id = UUIDField(unique=True)
    name = CharField()
    price = DecimalField()
    description = TextField()

    class Meta:
        database = database
