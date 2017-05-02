from flask_restful import reqparse, Resource
from models import Order
import uuid


class Order(Resource):
    def get():
