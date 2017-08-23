from flask import Blueprint
import app.auth.controllers as ctrl

auth = Blueprint('auth', __name__)
auth.add_url_rule('/', view_func=ctrl.index, methods=['GET'])

auth.add_url_rule('/twitter/login', view_func=ctrl.login, methods=['GET'])
auth.add_url_rule('/twitter/oauth-authorized', view_func=ctrl.twitter_authorized, methods=['GET'])
auth.add_url_rule('/twitter/logout', view_func=ctrl.logout, methods=['GET'])
