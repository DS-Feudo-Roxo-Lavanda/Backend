from telnetlib import STATUS
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
            email = request.get_json().get('email')
            username = request.get_json().get('username')
            password = request.get_json().get('password')

            user = self.client.db.user.find_one({
                "email": email
            })
            
            
            if user is not None:
                return jsonify(message="O usuário já existe", status=404)

            if email == '':
                return jsonify(message="E-mail não pode ser vazio.", status=400)

            if username == '':
                return jsonify(message="Usuário não pode ser vazio.", status=400)

            if password == '':
                return jsonify(message="Senha não pode ser vazia.", status=400)

            self.client.db.user.insert_one(
                {'email': email, 'username': username, 'password': password}
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
