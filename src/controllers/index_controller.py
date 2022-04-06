from src.utils.CustomEnconder import CustomEncoder
from app import token_req
from flask import jsonify, request
from bson.objectid import ObjectId
import json
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
 

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


        @self.app.route('/cadastro', methods=['POST'])
        def save_user():
            email = request.get_json().get('email')
            username = request.get_json().get('username')
            password = request.get_json().get('password')

            user = self.client.db.user.find_one({
                "email": email
            })

            if user is not None:
                return jsonify(message="O usuário já existe.", status=404)
            
            if email == '':
                return jsonify(message="E-mail não pode ser vazio.", status=400)
            if username == '':
                return jsonify(message="Usuário não pode ser vazio.", status=400)
            if password == '':
                return jsonify(message="Senha não pode ser vazia.", status=400)

            self.client.db.user.insert_one(
                {'email': email, 'username': username, 'password': generate_password_hash(password)}
            )

            return jsonify(message="Cadastro concluído!", status=200)


        @self.app.route('/login', methods=['POST'])
        def login():
            email = request.get_json().get('email')
            password = request.get_json().get('password')
            
            user = self.client.db.user.find_one({
                "email": email
            })

            if email == '' or password == '':
                return jsonify(message="Preencha todos os campos.",status=400)
           
            elif user is None or not check_password_hash(user["password"], password):
                return jsonify(message="Usuário ou senha incorretos.",status=400)
            
            time = datetime.utcnow() + timedelta(minutes=30)
            token = jwt.encode({
                    "user": {
                        "email": f"{user['email']}",
                        "id": f"{user['_id']}",
                    },
                    "exp": time
                },"SECRET_KEY")

            return jsonify(message="Login concluído!", status=200)
        

        @self.app.route('/meus-shows/<tipo>', methods=['GET']) # tipo -> filme, serie ou favorito
        @token_req
        def lista_de_filmes(tipo):
            string_id = request.get_json().get('user_id')
            
            objetos = self.client.db.user.find({
                    "user_id": ObjectId(string_id), 
                })
            
            lista = []
            for i in objetos:
                if list(i)[2] == str(tipo):
                    lista.append(i[str(tipo)])

            if len(lista) != 0:    
                    return jsonify(requisicao=lista)
            else:
                return jsonify(message=f"Nenhum(a) {tipo} encontrado(a).", status=400)
            

        @self.app.route('/adicionar/<tipo>', methods=['POST']) # tipo -> filme, serie ou favorito
        @token_req
        def adicionar_filme(tipo):    
            string_id = request.get_json().get('user_id')
            json_show = request.get_json().get('objeto')
            
            self.client.db.user.insert_one(
                {'user_id': ObjectId(string_id), str(tipo): json_show}
            )

            return jsonify(message=f"{str(tipo).capitalize()} adicionado(a)!", status=200)