import os
from flask import Flask
from routes.index import  index_route

app = Flask(__name__)


app.register_blueprint(index_route, url_prefix='/')

if __name__ == '__main__':
    PORT = os.getenv('PORT') if os.getenv('PORT') else 8080
    app.run(host='0.0.0.0', port=PORT)