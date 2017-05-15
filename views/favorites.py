from flask_restful import Resource, reqparse
# from http.client import CREATED
# from http.client import NO_CONTENT
# from http.client import NOT_FOUND
from http.client import OK
# from http.client import BAD_REQUEST
from models import Item, User, Favorites
import uuid
import utils


class FavoritesResource(Resource):
    def get(self):
        # TODO: we will have a user from auth here.
        user = User.select().get()
        return user.get_favorite_items(), OK


class FavoriteResource(Resource):
    def get(self):
        True
