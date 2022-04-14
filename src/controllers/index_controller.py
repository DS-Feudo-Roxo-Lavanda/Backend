from functools import wraps
from src.utils.CustomEnconder import CustomEncoder
from src.utils.constantes import SECRET_KEY
from flask import jsonify, request
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import jwt

# Autenticador JWT
def token_req(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify(message='Token necessário', status=401)
        
        try:
            data = jwt.decode(token, SECRET_KEY, "HS256")
        except:
            return jsonify(message='Token inválido.', status=403)

        return f(*args,**kwargs)

    return decorated

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

        # Rota de cadastro de usuário
        @self.app.route('/cadastro', methods=['POST'])
        def save_user():
            email = request.get_json().get('email').strip()
            username = request.get_json().get('username').strip()
            password = request.get_json().get('password').strip()

            if email == '':
                return jsonify(message="E-mail não pode ser vazio.", status=400)
            if username == '':
                return jsonify(message="Usuário não pode ser vazio.", status=400)
            if password == '':
                return jsonify(message="Senha não pode ser vazia.", status=400)

            user = self.client.db.user.find_one({
                "email": email
            })

            if user is not None:
                return jsonify(message="O usuário já existe.", status=404)
            
            self.client.db.user.insert_one(
                {'email': email, 'username': username, 'password': generate_password_hash(password)}
            )

            return jsonify(message="Cadastro concluído!", status=200)

        # Rota de login do usuário
        @self.app.route('/login', methods=['POST'])
        def login():
            email = request.get_json().get('email')
            password = request.get_json().get('password')
            
            if email == '' or password == '':
                return jsonify(message="Preencha todos os campos.",status=400)
            
            user = self.client.db.user.find_one({
                "email": email
            })

            if user is None or not check_password_hash(user["password"], password):
                return jsonify(message="Usuário ou senha incorretos.",status=400)
            
            exp_time = datetime.utcnow() + timedelta(minutes=30)

            token = jwt.encode({
                    "user": {
                        "email": f"{user['email']}",
                        "id": f"{user['_id']}",
                    },"exp": exp_time
                    }, SECRET_KEY)

            return jsonify(message="Login concluído!", token=token, status=200)
        
        # Rota que retorna os Meus Shows, do tipo solicitada
        @self.app.route('/meus-shows/<tipo>', methods=['GET'])# tipo="filmes","series","favoritos"
        @token_req
        def meus_shows(tipo):
            string_id = request.get_json().get('user_id')
            
            user = self.client.db.user.find_one(
                {'_id': ObjectId(string_id)})
            if user is None:
                return jsonify(message="Usuário não existe", status=400)
            
            if tipo == "favoritos":
                filmes, series = [], []
                
                f_favoritos = self.client.db.filmes.find(
                    {"user_id": ObjectId(string_id), "favorito": bool(True)}
                )
                for i in f_favoritos:
                    filmes.append(i["filme"])

                s_favoritos = self.client.db.series.find(
                    {"user_id": ObjectId(string_id), "favorito": bool(True)}
                )
                for i in s_favoritos:
                    series.append(i["serie"])
                
                
                return jsonify(user_id=string_id, filmes=filmes, series=series)
            
            if tipo == "series":
                assistidos, nao_assistidos = [], []
                
                series = self.client.db.series.find(
                    {"user_id": ObjectId(string_id)}
                )
                for i in series:
                    if i["assistido"] == True:
                        assistidos.append(i["serie"])
                    elif i["nao_assistido"] == True:
                        nao_assistidos.append(i["serie"])
                
                return jsonify(user_id=string_id, assistidos=assistidos, nao_assistidos=nao_assistidos)
            
            if tipo == "filmes":
                assistidos, nao_assistidos = [], []
                
                filmes = self.client.db.filmes.find(
                    {"user_id": ObjectId(string_id)}
                )
                for i in filmes:
                    if i["assistido"] == True:
                        assistidos.append(i["filme"])
                    elif i["nao_assistido"] == True:
                        nao_assistidos.append(i["filme"])
                
                return jsonify(user_id=string_id, assistidos=assistidos, nao_assistidos=nao_assistidos)

        # Rota que retorna os estados de um filme/série específico
        @self.app.route('/<tipo>/<tmdb_id>', methods=['GET']) # tipo="filme","serie" | tmdb_id=id do filme/série
        @token_req
        def especifico(tipo, tmdb_id):
            string_id = request.get_json().get('user_id')

            user = self.client.db.user.find_one(
                {'_id': ObjectId(string_id)})
            
            if user is None:
                return jsonify(message="Usuário não existe", status=400)

            if tipo == "filme":
                filme = self.client.db.filmes.find_one(
                    {"user_id": ObjectId(string_id), "tmdb_id": int(tmdb_id)}
                )

                if filme is None:
                    return jsonify(assistido=False, nao_assistido=False, favorito=False)
                else:
                    return jsonify(assistido=filme["assistido"], nao_assistido=filme["nao_assistido"], favorito=filme["favorito"])
            
            if tipo == "serie":
                serie = self.client.db.series.find_one(
                    {"user_id": ObjectId(string_id), "tmdb_id": int(tmdb_id)}
                )

                if serie is None:
                    return jsonify(assistido=False, nao_assistido=False, favorito=False)
                else:
                    return jsonify(assistido=serie["assistido"], nao_assistido=serie["nao_assistido"], favorito=serie["favorito"])

        # Rota que atualiza o estado atual do filme, ou adiciona-o ao banco caso não estivesse
        @self.app.route('/<tipo>/<tmdb_id>/atualizar/<estado>', methods=['POST']) # tipo="filme","serie" | tmdb_id=id do filme/série | estado="assistido","nao_assistido","favorito"
        @token_req
        def atualizar(tipo, tmdb_id, estado):
            string_id = request.get_json().get('user_id')
            
            user = self.client.db.user.find_one(
                {'_id': ObjectId(string_id)})
            
            if user is None:
                return jsonify(message="Usuário não existe", status=400)
            
            if tipo == "serie":
                objeto = self.client.db.series.find_one(
                    {'user_id': ObjectId(string_id), "tmdb_id": int(tmdb_id)}
                )
                if objeto is None:
                    json_show = request.get_json().get('objeto')
                    objeto = {
                            "user_id": ObjectId(string_id),
                            "tmdb_id": int(tmdb_id),
                            "serie": json_show,
                            "assistido": False,
                            "nao_assistido": False,
                            "favorito": False
                        }
                    self.client.db.series.insert_one(objeto)                    
            
            if tipo == "filme":
                objeto = self.client.db.filmes.find_one(
                    {
                        'user_id': ObjectId(string_id), "tmdb_id": int(tmdb_id)
                    })
                if objeto is None:
                    json_show = request.get_json().get('objeto')
                    objeto = {
                            "user_id": ObjectId(string_id),
                            "tmdb_id": int(tmdb_id),
                            "filme": json_show,
                            "assistido": False,
                            "nao_assistido": False,
                            "favorito": False
                        }
                    self.client.db.filmes.insert_one(objeto)
                    
            
            if objeto[estado] == True:
                objeto[estado] = False
            elif objeto[estado] == False:
                objeto[estado] = True
            
            if estado == "assistido" and objeto["assistido"] == False and objeto["favorito"] == True:
                objeto["favorito"] = False
            if estado == "favorito" and objeto["favorito"] == True and objeto["nao_assistido"] == True:
                objeto["nao_assistido"], objeto["assistido"] = False, True
            if estado == "assistido" and objeto["assistido"] == True and objeto["nao_assistido"] == True:
                objeto["nao_assistido"] = False
            if estado == "nao_assistido" and objeto["nao_assistido"] == True and objeto["favorito"] == True:
                objeto["favorito"], objeto["assistido"] = False, False
            if estado == "nao_assistido" and objeto["nao_assistido"] == True and objeto["assistido"] == True:
                objeto["assistido"] = False
        
            
            if tipo == "filme":
                    self.client.db.filmes.replace_one(
                        {
                            'user_id': ObjectId(string_id), "tmdb_id": int(tmdb_id)
                        },
                        {
                            "user_id": ObjectId(string_id),
                            "tmdb_id": int(tmdb_id),
                            "filme": objeto["filme"],
                            "assistido": objeto['assistido'],
                            "nao_assistido": objeto['nao_assistido'],
                            "favorito": objeto['favorito']
                        })
                
            if tipo == "serie":    
                self.client.db.series.replace_one(
                    {
                        'user_id': ObjectId(string_id), "tmdb_id": int(tmdb_id)
                    },
                    {
                        "user_id": ObjectId(string_id),
                        "tmdb_id": int(tmdb_id),
                        "serie": objeto["serie"],
                        "assistido": objeto['assistido'],
                        "nao_assistido": objeto['nao_assistido'],
                        "favorito": objeto['favorito']
                    })

            return jsonify(message="Atributo alterado com sucesso", status=200)
            