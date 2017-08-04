from flask import Blueprint, request, make_response, json
import app.module01.models as Models

module01 = Blueprint('module01', __name__)

@module01.route('/')
def index():
    return 'Module01 API'

@module01.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email', None)
    nickname = request.form.get('nickname', None)
    password = request.form.get('password', None)

    if not email or not nickname or not password:
        return make_response(json.jsonify('Something not Entered'), 400)


@module01.route('/signup/check/', methods=['GET'])
def checkInfo():
    nickname = request.form.get('nickname', None)
    email = request.form.get('email', None)

    return make_response(json.jsonify(result=''), 200)
