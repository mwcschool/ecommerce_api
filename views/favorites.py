from flask_restful import Resource, reqparse
from http.client import CREATED
# from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
# from http.client import BAD_REQUEST
from models import Item, User, Favorites
import uuid
import utils


def check_uuid_is_in_(id_check):
    # if id_check not
    pass


class FavoritesResource(Resource):
    def get(self):
        # TODO: we will have a user from auth here.
        try:
            user = User.select().get()
        except User.DoesNotExist:
            return None, NOT_FOUND
        return user.get_favorite_items(), OK

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id_user', type=type(uuid.uuid4()), required=True)
        parser.add_argument('id_item', type=type(uuid.uuid4()), required=True)
        args = parser.parse_args(strict=True)
        if not User.exists_uuid(args['id_user']) and not Item.exists_uuid(args['id_item']):
            return None, NOT_FOUND

        obj = Favorites.create(
            item=Item.get(Item.item_id == args['id_item']),
            user=User.get(User.user_id == args['id_user']),
        )
        return obj.json(), CREATED


class FavoriteResource(Resource):
    def delete(self):
        # TODO: we will have a user from auth here.
        try:
            user = User.select().get()
        except User.DoesNotExist:
            return None, NOT_FOUND

        parser = reqparse.RequestParser()
        parser.add_argument('id_item', type=type(uuid.uuid4()), required=True)
        args = parser.parse_args(strict=True)
        if not Item.exists_uuid(args['id_item']):
            return None, NOT_FOUND

        query = Favorites.select()\
            .join(Item)\
            .where(Favorites.item == Item.item_id)\
            .join(User)\
            .where(Favorites.user == User.user_id)\
            # .on(Favorites.item ==  )

        # if not Favorites.s
        #    return None, NOT_FOUND

        True
