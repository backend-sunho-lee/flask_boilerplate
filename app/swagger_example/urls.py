from flask import Blueprint
import app.swagger_example.controllers as ctrl

swag = Blueprint('swag', __name__)

swag.add_url_rule('/language/<string:language>', view_func=ctrl.language_awesomeness, methods=['GET'])
