from utils import non_empty_str
from marshmallow import Schema, fields


class ItemSchema(Schema):
    uuid = fields.UUID(required=True, dump_only=True)
    name = fields.Str(required=True, validate=non_empty_str)
    price = fields.Decimal(required=True)
    description = fields.Str(required=True, validate=non_empty_str)
    category = fields.Str(required=True, validate=non_empty_str)


class UserSchema(Schema):
    uuid = fields.UUID(required=True, dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Str(required=True, validate=non_empty_str)
    password = fields.Str(required=True, validate=non_empty_str, load_only=True)


class AddressSchema(Schema):
    uuid = fields.UUID(required=True, dump_only=True)
    user = fields.UUID(required=True, attribute='user.uuid')
    nation = fields.Str(required=True)
    city = fields.Str(required=True)
    postal_code = fields.Str(required=True)
    local_address = fields.Str(required=True)
    phone = fields.Str(required=True)
