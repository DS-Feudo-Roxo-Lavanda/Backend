import os
from src.utils.CustomEnconder import CustomEncoder
from src.controllers.index_controller import IndexController
from flask import Flask
import pymongo

app = Flask(__name__)

app.json_encoder = CustomEncoder

connect_uri = os.environ.get('MONGO_URI') if os.environ.get(
    'MONGO_URI'
) else "mongodb+srv://RoxoLavanda:g63e3IkyRkQewVYo@teste.m5o3z.mongodb.net/Meuapp?retryWrites=true&w=majority" #'mongodb://admin:admin@mongo-db:27017/moviesmanager?authSource=admin'

client = pymongo.MongoClient(connect_uri, serverSelectionTimeoutMS=30000)

try:
    app.logger.debug(client.server_info())
except Exception:
    print("Unable to connect to the server.")

IndexController(app, client).routes()

if __name__ == '__main__':
    PORT = os.getenv('PORT') if os.getenv('PORT') else 5000
    app.run(debug=True, host='0.0.0.0', port=PORT)
