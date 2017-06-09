from flask_restful import Resource, reqparse, abort
from flask import current_app
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
from http.client import BAD_REQUEST
import uuid
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import os

from models import Item, Picture
import utils
import auth


def non_empty_string(string):
    return str(string).strip()


class ItemsResource(Resource):
    def get(self):
        return [obj.json() for obj in Item.select()], OK

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('price', type=int, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('category', type=str, required=True)
        parser.add_argument('availability', type=int, required=True)
        args = parser.parse_args(strict=True)
        try:
            utils.non_empty_str(args['name'], 'name')
        except ValueError:
            return None, BAD_REQUEST

        if args["availability"] < 0:
            return None, BAD_REQUEST

        obj = Item.create(
            uuid=uuid.uuid4(),
            name=args["name"],
            price=args["price"],
            description=args["description"],
            category=args["category"],
            availability=args["availability"]
        )

        return obj.json(), CREATED


class ItemResource(Resource):
    def get(self, uuid):
        try:
            return Item.get(Item.uuid == uuid).json(), OK
        except Item.DoesNotExist:
            return None, NOT_FOUND

    @auth.login_required
    def delete(self, uuid):
        try:
            item = Item.get(Item.uuid == uuid)
        except Item.DoesNotExist:
            return None, NOT_FOUND

        item.delete_instance()
        return None, NO_CONTENT

    @auth.login_required
    def put(self, uuid):
        try:
            obj = Item.get(uuid=uuid)
        except Item.DoesNotExist:
            return None, NOT_FOUND

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('price', type=int, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('category', type=str, required=True)
        parser.add_argument('availability', type=int, required=True)
        args = parser.parse_args(strict=True)
        try:
            utils.non_empty_str(args['name'], 'name')
        except ValueError:
            return None, BAD_REQUEST

        if args["availability"] < 0:
            return None, BAD_REQUEST

        obj.name = args["name"]
        obj.price = args["price"]
        obj.description = args["description"]
        obj.category = args["category"]
        obj.availability = args["availability"]
        obj.save()

        return obj.json(), OK


class ItemPicturesResource(Resource):
    def get(self, uuid):
        pass

    def post(self, item_id):
        try:
            item = Item.get(Item.uuid == item_id)
        except Item.DoesNotExist:
            return None, NOT_FOUND

        parser = reqparse.RequestParser()
        parser.add_argument('title', type=non_empty_string, required=True)
        parser.add_argument('file', type=FileStorage, location='files', required=True)

        args = parser.parse_args(strict=True)

        image = args['file']
        title = args['title']

        extension = image.filename.rsplit('.', 1)[1].lower()
        config = current_app.config
        if '.' in image.filename and not extension in config['ALLOWED_EXTENSIONS']:
            abort(400, message="Extension not supported.")

        picture = Picture.create(
            uuid=uuid.uuid4(),
            title=title,
            extension=extension,
            item=item
        )

        save_path = os.path.join('.', config['UPLOADS_FOLDER'], 'items', str(item_id))
        new_filename = secure_filename('.'.join([str(picture.uuid), extension]))

        os.makedirs(save_path, exist_ok=True)

        image.save(os.path.join(save_path, new_filename))

        return picture.json(), CREATED
