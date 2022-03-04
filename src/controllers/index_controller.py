from src.utils.CustomEnconder import CustomEncoder
from flask import jsonify, request
from bson.json_util import dumps
import json


class IndexController:
    def __init__(self, app, client):
        self.app = app
        self.client = client
        self.custo_encoder = CustomEncoder()

    def format_data(self, obj):
        return json.loads(self.custo_encoder.encode(obj))

    def routes(self):
        @self.app.route('/', methods=['GET'])
        def index():
            return jsonify({'message': 'Hello, World!'})

        @self.app.route('/user', methods=['POST'])
        def save_user():
            name = request.get_json().get('name')
            username = request.get_json().get('username')

            self.client.db.user.insert_one(
                {'name': name, 'username': username}
            )

            return jsonify({
                'message': 'User saved successfully',
            })

        @self.app.route('/users', methods=['GET'])
        def get_users():
            users = self.client.db.user.find({})

            users_response = [
                self.format_data(user) for user in users
            ]

            return jsonify({
                'message': 'Users retrieved successfully',
                'data': users_response,
            })
