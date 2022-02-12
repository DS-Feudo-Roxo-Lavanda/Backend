from flask import Flask, jsonify

def index():
    return jsonify({'message': 'Hello, World!'})