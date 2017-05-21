from flask_restful import Resource, reqparse
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
from http.client import BAD_REQUEST
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
        if not User.exists_uuid(args['id_user']) or not Item.exists_uuid(args['id_item']):
            return None, NOT_FOUND

        obj = Favorites.create(
            item=Item.get(Item.item_id == args['id_item']),
            user=User.get(User.user_id == args['id_user']),
        )
        return obj.json(), CREATED


class FavoriteResource(Resource):
    def delete(self, item_id):
        # TODO: we will have a user from auth here.
        try:
            user = User.select().get()
        except User.DoesNotExist:
            return None, NOT_FOUND

        if not Item.exists_uuid(item_id):
            return None, NOT_FOUND

        query_check_many_to_many_exists = Item.select()\
                .join(Favorites, on=Favorites.item)\
                .join(User, on=Favorites.user)\
                .where(User.user_id == user.user_id)\
                .exists()

        if query_check_many_to_many_exists is False:
            return None, NOT_FOUND

        favorite_to_be_deleted = Favorites.select()\
                .join(Item, on=Favorites.item)\
                .switch(Favorites)\
                .join(User, on=Favorites.user)\
                .where(User.user_id == user.user_id)\
                .where(Item.item_id == item_id)

        Favorites.delete().where(Favorites.id == favorite_to_be_deleted).execute()

        return None, NO_CONTENT
