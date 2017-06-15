import json
from peewee import SqliteDatabase
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
from http.client import BAD_REQUEST
from .base_test import BaseTest
from models import Picture
from models import Item
from app import app
import uuid
import os


class TestPicture(BaseTest):

    def test_get_picture(self):
        picture1 = self.create_item_picture()

        resp = self.app.get('/pictures/{}'.format(picture1.uuid))
        assert resp.status_code == OK
        #assert json.loads(resp.data.decode()) == [picture1.json()]

    def test_get_picture_not_existing_picture(self):
        resp = self.app.get('/pictures/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND

    def test_get_picture_wrong_item(self):
        item1 = self.create_item()
        item2 = self.create_item()
        picture1 = self.create_item_picture(item1)
        #import pdb; pdb.set_trace()

        resp = self.app.get('/pictures/{}'.format(item2.uuid))
        assert resp.status_code == NOT_FOUND

    def test_get_picture_int_uuid(self):
        picture1 = self.create_item_picture()

        resp = self.app.get('/pictures/{}'.format(int(picture1.uuid)))
        assert resp.status_code == NOT_FOUND

    def test_get_picture_wrong_extension(self):
        test_image_path= os.path.join('.', 'tests', 'images', 'test_image.png')

        picture1 = self.create_item_picture(extension='jpeg')

        resp = self.app.get('/pictures/{}'.format(picture1.uuid))
        assert resp.status_code == NOT_FOUND


    #def test_image_path():
        #pass

    # def test_get_picture_wrong_extension(self):
    #     picture1 = self.create_item_picture(extension='png')

    #     resp = self.app.get('/pictures/{}'.format(picture1.uuid))
    #     assert resp.status_code == BAD_REQUEST

    def test_delete_picture_succed(self):
        picture1 = self.create_item_picture()

        resp = self.app.delete('/pictures/{}'.format(picture1.uuid))
        assert resp.status_code == NO_CONTENT
        assert len(Picture.select()) == 0
        resp = self.app.get('/pictures/{}'.format(picture1.uuid))
        assert resp.status_code == NOT_FOUND

    def test_delete_picture_failure_not_found(self):
        resp = self.app.get('/picture/{}'.format(uuid.uuid4()))
        assert resp.status_code == NOT_FOUND