from flask_restful import Resource, reqparse
from http.client import NOT_FOUND
from http.client import OK
from http.client import NO_CONTENT
from http.client import CREATED
from http.client import BAD_REQUEST
from models import Item, Favorites
import uuid
import auth
from flask import g


class FavoritesResource(Resource):
    @auth.login_required
    def get(self):
        # TODO: we will have a user from auth here.

        return g.current_user.favorite_items(), OK

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id_item', type=type(uuid.uuid4()), required=True)
        args = parser.parse_args(strict=True)

        try:
            item = Item.get(Item.uuid == args['id_item'])

        except (Item.DoesNotExist):
            return None, BAD_REQUEST

        return g.current_user.add_favorite(item).json(), CREATED


class FavoriteResource(Resource):
    @auth.login_required
    def delete(self, item_id):
        # TODO: we will have a user from auth here.

        try:
            item = Item.get(Item.uuid == item_id)
        except Item.DoesNotExist:
            return None, NOT_FOUND

        try:
            Favorites.get(Favorites.item == item and Favorites.user == g.current_user)
        except Favorites.DoesNotExist:
            return None, NOT_FOUND

        return g.current_user.remove_favorite(item), NO_CONTENT
