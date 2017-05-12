from flask_restful import Resource, reqparse
# from http.client import CREATED
# from http.client import NO_CONTENT
# from http.client import NOT_FOUND
# from http.client import OK
# from http.client import BAD_REQUEST
import uuid
from models import Item, User
import utils


class FavoritesResource(Resource):
    def get(self):
        # return [obj.json() for obj in Favorites.get(user=)], OK
        query = Item.select(Item.name, Item.price, Item.description)\
            .join(Favorites).join(User)\
            .where(Item.item_id == Favorites.item_id)\
            .where(User.user_id == Favorites.user_id)

        return [obj.json() for obj in query], OK
# class Favorites(BaseModel):
#     user_id = ForeignKeyField(User)
#     item_id = ForeignKeyField(Item)
#
# class User(BaseModel):
#     user_id = UUIDField(unique=True)
#     first_name = CharField()
#     last_name = CharField()
#     email = CharField(unique=True)
#     password = CharField()
#
# class Item(BaseModel):
#     item_id = UUIDField(unique=True)
#     name = CharField()
#     price = DecimalField()
#     description = TextField()


class FavoriteResource(Resource):
    def get(self):
        True
