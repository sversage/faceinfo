VERSION_STR = 'vmock'


from flask import Blueprint

blueprint = Blueprint(VERSION_STR, __name__)


@blueprint.route('/')
def root():
    return VERSION_STR


from app import app
app.register_blueprint(blueprint, url_prefix='/'+VERSION_STR)
