from flask import Blueprint
from controllers.index_controller import index

index_route = Blueprint('index', __name__)

index_route.route('/', methods=['GET'])(index)