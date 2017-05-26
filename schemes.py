from marshmallow import Schema, fields
from marshmallow_jsonschema import JSONSchema


class ItemSchema(Schema):
    uuid = fields.UUID()


class UserSchema(Schema):
    uuid = fields.UUID()


class AddressSchema(Schema):
    uuid = fields.UUID()


class OrderSchema(Schema):
    uuid = fields.UUID()


class PictureSchema(Schema):
    uuid = fields.UUID()
