VERSION_STR = 'v1.0.0'


from flask import Blueprint
from flask_swagger import swagger

blueprint = Blueprint(VERSION_STR, __name__)


@blueprint.route('/')
def root():
    return VERSION_STR


@blueprint.route('/docs')
def docs():
    return jsonify(swagger(blueprint))


from app import app
app.register_blueprint(blueprint, url_prefix='/'+VERSION_STR)
