import os
from src.utils.CustomEnconder import CustomEncoder
from src.utils.constantes import USUARIO_MONGO, SENHA_MONGO, DB_MONGO, CLUSTER_MONGO
from src.controllers.index_controller import IndexController
from flask_cors import CORS
from flask import Flask
import pymongo

app = Flask(__name__)

cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

app.config['CORS_HEADERS'] = 'Content-Type'

app.json_encoder = CustomEncoder

connect_uri = os.environ.get('MONGO_URI') if os.environ.get(
    'MONGO_URI'
) else f"mongodb+srv://{USUARIO_MONGO}:{SENHA_MONGO}@{CLUSTER_MONGO}.mongodb.net/{DB_MONGO}?retryWrites=true&w=majority" #'mongodb://admin:admin@mongo-db:27017/moviesmanager?authSource=admin'

client = pymongo.MongoClient(connect_uri, serverSelectionTimeoutMS=30000)

try:
    app.logger.debug(client.server_info())
except Exception:
    print("Unable to connect to the server.")

IndexController(app, client).routes()

if __name__ == '__main__':
    PORT = os.getenv('PORT') if os.getenv('PORT') else 5000
    app.run(debug=True, host='0.0.0.0', port=PORT)
