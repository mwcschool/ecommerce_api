from marshmallow import Schema, fields, validate


def check_empty_str(value):
    if str(value).strip() == '':
        return False


class ItemSchema(Schema):
    uuid = fields.UUID(dump_only=True)
    name = fields.Str(required=True, validate=check_empty_str)
    price = fields.Decimal(required=True, validate=validate.Range(min=0))
    description = fields.Str(required=True, validate=check_empty_str)
    category = fields.Str(required=True, validate=check_empty_str)
    availability = fields.Int(required=True, validate=validate.Range(min=0))


class ItemPatchSchema(Schema):
    uuid = fields.UUID(dump_only=True)
    name = fields.Str(validate=check_empty_str)
    price = fields.Decimal(validate=validate.Range(min=0))
    description = fields.Str(validate=check_empty_str)
    category = fields.Str(validate=check_empty_str)
    availability = fields.Int(validate=validate.Range(min=0))


class UserSchema(Schema):
    uuid = fields.UUID(dump_only=True)
    first_name = fields.Str(required=True, validate=check_empty_str)
    last_name = fields.Str(required=True, validate=check_empty_str)
    email = fields.Str(required=True, validate=check_empty_str)
    password = fields.Str(required=True, validate=check_empty_str, load_only=True)
    status = fields.Str(validate=check_empty_str, dump_only=True)


class AddressSchema(Schema):
    uuid = fields.UUID(dump_only=True)
    user = fields.UUID(attribute='user.uuid', dump_only=True)
    nation = fields.Str(required=True, validate=validate.Length(min=1))
    city = fields.Str(required=True, validate=validate.Length(min=1))
    postal_code = fields.Str(required=True, validate=validate.Length(min=1))
    local_address = fields.Str(required=True, validate=validate.Length(min=1))
    phone = fields.Str(required=True, validate=validate.Length(min=1))


class OrderItemSchema(Schema):
    item = fields.UUID(required=True, dump_only=True, attribute='item.uuid')
    quantity = fields.Integer(as_string=False)
    subtotal = fields.Decimal(required=True, dump_only=True)


class OrderSchema(Schema):
    uuid = fields.UUID(required=True, dump_only=True)
    total_price = fields.Decimal(required=True)
    user = fields.Nested(UserSchema, only=["uuid"])
    items = fields.Nested(OrderItemSchema, many=True, attribute='order_items')


class FavoritesSchema(Schema):
    uuid = fields.UUID(dump_only=True)
    user = fields.UUID(required=True, attribute='user.uuid')
    item = fields.UUID(required=True, attribute='item.uuid')
