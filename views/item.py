from flask_restful import Resource, reqparse, abort, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
from http.client import BAD_REQUEST
from http.client import UNAUTHORIZED
from flask import current_app, g
import uuid
import os

from models import Item, Picture
import utils
import auth

from jsonschema import ValidationError



def non_empty_string(string):
    string = str(string).strip()
    if string:
        return string
    else:
        raise ValueError


class ItemsResource(Resource):
    def get(self):
        return [obj.json() for obj in Item.select()], OK

    @auth.login_required
    def post(self):
        if not g.current_user.superuser:
            return None, UNAUTHORIZED

        jsondata = request.get_json()

        try:
            utils.non_empty_str(jsondata['name'], 'name')
        except ValueError:
            return None, BAD_REQUEST

        try:
            if jsondata['availability'] < 0:
                return None, BAD_REQUEST
        except KeyError:
            return None, BAD_REQUEST

        try:
            Item.verify_json(jsondata)
        except ValidationError as ver_json_error:
            return ver_json_error.message, BAD_REQUEST

        obj = Item.create(
            uuid=uuid.uuid4(),
            name=jsondata['name'],
            price=jsondata['price'],
            description=jsondata['description'],
            category=jsondata['category'],
            availability=jsondata['availability']
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
        if not g.current_user.superuser:
            return None, UNAUTHORIZED

        try:
            item = Item.get(Item.uuid == uuid)
        except Item.DoesNotExist:
            return None, NOT_FOUND

        item.delete_instance()
        return None, NO_CONTENT

    @auth.login_required
    def put(self, uuid):
        if not g.current_user.superuser:
            return None, UNAUTHORIZED

        try:
            obj = Item.get(Item.uuid == uuid)
        except Item.DoesNotExist:
            return None, NOT_FOUND

        jsondata = request.get_json()

        try:
            utils.non_empty_str(jsondata['name'], 'name')
        except ValueError:
            return None, BAD_REQUEST

        try:
            if jsondata['availability'] < 0:
                return None, BAD_REQUEST
        except KeyError:
            return None, BAD_REQUEST

        try:
            Item.verify_json(jsondata)
        except ValidationError as ver_json_error:
            return ver_json_error.message, BAD_REQUEST

        obj.name = args['name']
        obj.price = args['price']
        obj.description = args['description']
        obj.category = args['category']
        obj.availability = args['availability']
        obj.save()

        return obj.json(), OK

    @auth.login_required
    def patch(self, uuid):
        try:
            obj = Item.get(Item.uuid == uuid)
        except Item.DoesNotExist:
            return None, NOT_FOUND

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('price', type=int)
        parser.add_argument('description', type=str)
        parser.add_argument('category', type=str)
        parser.add_argument('availability', type=int)
        args = parser.parse_args(strict=True)

        try:
            utils.non_empty_str(args['name'], 'name')
        except ValueError:
            return None, BAD_REQUEST

        if args['availability'] is not None:
            if args['availability'] < 0:
                return None, BAD_REQUEST

        for attr in args.keys():
            if args.get(attr) is not None:
                setattr(obj, attr, args[attr])

        obj.save()

        return obj.json(), OK


class ItemPicturesResource(Resource):
    def get(self, item_id):
        try:
            item = Item.get(Item.uuid == item_id)
        except Item.DoesNotExist:
            return None, NOT_FOUND

        return [pic.json() for pic in item.pictures], OK

    @auth.login_required
    def post(self, item_id):
        if not g.current_user.superuser:
            return None, UNAUTHORIZED

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
        if '.' in image.filename and extension not in config['ALLOWED_EXTENSIONS']:
            abort(400, message='Extension not supported.')

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
