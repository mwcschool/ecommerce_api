from flask_restful import Resource
from http.client import NOT_FOUND
from http.client import OK
from flask import send_from_directory, current_app
from models import Picture, Item


class PictureResource(Resource):

    def get(self, uuid):
        try:
            picture =  Picture.get(Picture.uuid == uuid)
        except Picture.DoesNotExist:
            return None, NOT_FOUND

        item = Item.get(picture.item)

        return send_from_directory(
            os.path.join(
                current_app.config['UPLOADS_FOLDER'],
                'items',
                str(item.uuid),
            ),

            secure_filename('.'.join([str(picture.uuid), picture.extension]))
            #'{}.{}'.format(str(picture.uuid), picture.extension),
        )

    def delete(self, uuid):
        try:
            picture = Picture.get(picture.uuid == uuid)
        except Picture.DoesNotExist:
            return None, NOT_FOUND

        '{}.{}'.format(picture.uuid, picture.extension).delete_instance()
        return None, NO_CONTENT
