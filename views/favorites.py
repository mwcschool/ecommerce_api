from flask_restful import Resource, reqparse
from http.client import NOT_FOUND
from http.client import OK
from http.client import NO_CONTENT
from http.client import CREATED
from models import Item, User, Favorites
import uuid


class FavoritesResource(Resource):
    def get(self):
        # TODO: we will have a user from auth here.
        try:
            user = User.get()
        except User.DoesNotExist:
            return None, NOT_FOUND
        return user.favorite_items(), OK

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id_user', type=type(uuid.uuid4()), required=True)
        parser.add_argument('id_item', type=type(uuid.uuid4()), required=True)
        args = parser.parse_args(strict=True)

        try:
            user = User.get(User.uuid == args['id_user'])
            item = Item.get(Item.uuid == args['id_item'])

        except (User.DoesNotExist, Item.DoesNotExist):
            return None, NOT_FOUND

        return user.add_favorite(item).json(), CREATED


class FavoriteResource(Resource):
    def delete(self, item_id):
        # TODO: we will have a user from auth here.
        try:
            user = User.get()
        except User.DoesNotExist:
            return None, NOT_FOUND

        try:
            item = Item.get(Item.uuid == item_id)
        except Item.DoesNotExist:
            return None, NOT_FOUND

        try:
            Favorites.get(Favorites.item == item and Favorites.user == user)
        except Favorites.DoesNotExist:
            return None, NOT_FOUND

        return user.remove_favorite(item), NO_CONTENT
