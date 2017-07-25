import uuid
from models import Item, User, Address, Favorites
from jsonschema import ValidationError
import pytest


class TestValidateJsonschema:
    def test_validate_item_json__success(self):
        data = {
            'name': 'Item one',
            'price': 15,
            'description': 'desc1',
            'category': 'poligoni',
            'availability': 11,
        }

        Item.verify_json(data)

    def test_validate_item_json__failure_wrong_type_field(self):
        data = {
            'name': 'Item one',
            'price': '15',
            'description': 'desc1',
            'category': 'poligoni',
            'availability': 11,
        }

        with pytest.raises(ValidationError):
            Item.verify_json(data)

    def test_validate_item_json__failure_invalid_field_value(self):
        data = {
            'name': 'Item one',
            'price': 15,
            'description': 'desc1',
            'category': 'poligoni',
            'availability': -8,
        }

        with pytest.raises(ValidationError):
            Item.verify_json(data)

    def test_validate_item_json__failure_invalid_field_value_2(self):
        data = {
            'name': 'Item one',
            'price': -35,
            'description': 'desc1',
            'category': 'poligoni',
            'availability': 11,
        }

        with pytest.raises(ValidationError):
            Item.verify_json(data)

    def test_validate_item_json__failure_missing_field(self):
        data = {
            'name': 'Item one',
            'price': 15,
            'description': 'desc1',
            'availability': 11,
        }

        with pytest.raises(ValidationError):
            Item.verify_json(data)

    def test_validate_user_json__success(self):
        data = {
            'first_name': 'Anna',
            'last_name': 'Markis',
            'email': 'anna@markis.com',
            'password': '1234567',
            }

        User.verify_json(data)

    def test_validate_user_json__failure_wrong_type_field(self):
        data = {
            'first_name': 'Anna',
            'last_name': 'Markis',
            'email': 'anna@markis.com',
            'password': 1234567,
            }

        with pytest.raises(ValidationError):
            User.verify_json(data)

    def test_validate_user_json__failure_missing_field(self):
        data = {
            'first_name': 'Anna',
            'email': 'anna@markis.com',
            'password': '1234567',
            }

        with pytest.raises(ValidationError):
            User.verify_json(data)

    def test_validate_address_json__success(self):
        data = {
            'user': str(uuid.uuid4()),
            'nation': 'Italia',
            'city': 'Prato',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        Address.verify_json(data)

    def test_validate_address_json__failure_wrong_type_field(self):
        data = {
            'user': str(uuid.uuid4()),
            'nation': 'Italia',
            'city': 'Prato',
            'postal_code': 59100,
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        with pytest.raises(ValidationError):
            Address.verify_json(data)

    def test_validate_address_json__failure_missing_field(self):
        data = {
            'user': str(uuid.uuid4()),
            'nation': 'Italia',
            'postal_code': '59100',
            'local_address': 'Via Roncioni 10',
            'phone': '0574100100',
        }

        with pytest.raises(ValidationError):
            Address.verify_json(data)

    def test_validate_favorites_json__success(self):
        data = {
            'user': str(uuid.uuid4()),
            'item': str(uuid.uuid4()),
        }

        Favorites.verify_json(data)

    def test_validate_favorites_json__failure_wrong_type_field(self):
        data = {
            'user': int(uuid.uuid4()),
            'item': str(uuid.uuid4()),
        }

        with pytest.raises(ValidationError):
            Favorites.verify_json(data)

    def test_validate_favorites_json__failure_missing_field(self):
        data = {
            'item': str(uuid.uuid4()),
        }

        with pytest.raises(ValidationError):
            Favorites.verify_json(data)
