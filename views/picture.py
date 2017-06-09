from flask_restful import Resource
from http.client import NOT_FOUND
from http.client import OK
from flask import send_from_directory
from models import Picture


class PictureResource(Resource):

    def get(self, uuid):
        try:
            obj = Picture.get(Picture.uuid == uuid), OK
        except Picture.DoesNotExist:
            return None, NOT_FOUND

        picture = '{}.{}'.format(obj.uuid, obj.exstension)

        return send_from_directory(
            'images',
            picture,
        )
