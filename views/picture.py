from flask_restful import Resource
from http.client import OK, NOT_FOUND, NO_CONTENT
from flask import send_from_directory, current_app
from models import Picture, Item
from werkzeug.utils import secure_filename
import os

class PictureResource(Resource):

    def get(self, uuid):
        try:
            picture =  Picture.get(Picture.uuid == uuid)
        except Picture.DoesNotExist:
            return None, NOT_FOUND

        return send_from_directory(
            os.path.join(
                current_app.config['UPLOADS_FOLDER'],
                'items',
                str(picture.item.uuid),
            ),

            secure_filename('.'.join([str(picture.uuid), picture.extension]))
        )

    def delete(self, uuid):
        try:
            picture = Picture.get(Picture.uuid == uuid)
        except Picture.DoesNotExist:
            return None, NOT_FOUND

        picture.delete_instance()
        return None, NO_CONTENT
