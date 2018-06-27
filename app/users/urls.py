from flask import Blueprint
import app.users.controllers as ctrl

users = Blueprint('users', __name__)

users.add_url_rule('/me', view_func=ctrl.get_profile, methods=['GET'])
users.add_url_rule('/me/pwd', view_func=ctrl.change_password, methods=['PUT'])
users.add_url_rule('/me/nickname', view_func=ctrl.change_nickname, methods=['PUT'])
users.add_url_rule('/me/picture', view_func=ctrl.change_picture, methods=['PUT'])
users.add_url_rule('/me/picture/<picture_name>', view_func=ctrl.get_thumbnail, methods=['GET'])
users.add_url_rule('/me/picture/<picture_name>/origin', view_func=ctrl.get_thumbnail_original, methods=['GET'])
users.add_url_rule('/me/bye', view_func=ctrl.user_withdraw, methods=['DELETE'])
