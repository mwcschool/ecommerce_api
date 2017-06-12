import json
from peewee import SqliteDatabase
from http.client import CREATED
from http.client import NO_CONTENT
from http.client import NOT_FOUND
from http.client import OK
from http.client import BAD_REQUEST
from models import Picture
from models import Item
from app import app
import uuid
from .base_test import BaseTest

class TestPicture(BaseTest):

    def test_get_picture(self):
        picture1 = self.create_item_picture()

        resp = self.app.get('/pictures/{}'.format(picture1.uuid))
        assert resp.status_code == OK

