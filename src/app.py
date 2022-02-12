import os
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'message': 'Hello, World!'})

if __name__ == '__main__':
    PORT = os.getenv('PORT') if os.getenv('PORT') else 8080
    app.run(host='0.0.0.0', port=PORT)