from marshmallow import Schema, fields
from marshmallow_jsonschema import JSONSchema


class ItemSchema(Schema):
    uuid = fields.UUID()
    name = fields.Str()
    price = fields.Decimal()
    description = fields.Str()
    category = fields.Str()


class UserSchema(Schema):
    uuid = fields.UUID()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Str()
    password = fields.Str(load_only=True)


class AddressSchema(Schema):
    uuid = fields.UUID()
    user = fields.UUID()
    nation = fields.Str()
    city = fields.Str()
    postal_code = fields.Str()
    local_address = fields.Str()
    phone = fields.Str()
