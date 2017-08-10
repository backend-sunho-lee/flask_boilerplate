from flask import request, make_response, json
import app.module01.models as models

def index():
    return 'Module01 API'

def signup():
    email = request.form.get('email', None)
    nickname = request.form.get('nickname', None)
    password = request.form.get('password', None)

    if not email or not nickname or not password:
        return make_response(json.jsonify('Something not Entered'), 400)

def checkInfo():
    nickname = request.form.get('nickname', None)
    email = request.form.get('email', None)

    return make_response(json.jsonify(result=''), 200)
