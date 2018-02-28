# -*- coding: utf-8 -*-
from flask import Flask, g, redirect, abort, make_response, jsonify
from flask_session import Session
from flask_cors import CORS
from flask_caching import Cache
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify

# Define the WSGI application object
app = Flask(__name__, static_url_path='/static')

#: Configurations
import config
app.config.from_object(config)

#: Swagger
#Swagger(app)

# Flask-Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

#: Flask-Session
Session(app)

#: Flask-CORS
cors = CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": "true"}})

#: Flask_SSLify
sslify = SSLify(app)

###: DB 연결
# 저는 configs에 설정해서 바로 연결해서 쓸 수 있도록 했습니다.

# Import SQLAlchemy
# from flask.ext.sqlalchemy import SQLAlchemy
# from flask_sqlalchemy import SQLAlchemy

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()


#################################### 모듈 연결시키기 ####################################

# ##: Method 1: Blueprint 사용할 때
# Import a module / component using its blueprint handler variable (mod_auth)

# Register blueprint(s)

#: 버전이 여러개일 경우, 버전을 하나씩 삽입할까? 아니면 그전처럼 배열로해서 다 돌아가게 할까
# for version in versions:
#     app.register_blueprint(module01, url_prefix='{}/module01'.format(version))

from app.ex_swagger.urls import swag
app.register_blueprint(swag, url_prefix='/api/v1/swag')

from app.auth.urls import auth
app.register_blueprint(auth, url_prefix='/api/v1/auth')

from app.users.urls import users
app.register_blueprint(users, url_prefix='/api/v1/users')

# ##: Method 2: add_url_rule 사용할 때, Blueprint 안 쓸 때
# module 만들때마다 붙여줘라!
import app.module02.urls as module02

#: 등록된 url 확인하기
print(app.url_map)

#####################################################################################

from app import common
from flask import request


@app.before_request
def before_request():
    """
    모든 API 실행 전 실행하는 부분
    """
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
    
    if '/api' in request.environ['PATH_INFO']:
        is_ok = common.ddos_check_and_write_log()
        if is_ok is False:
            return make_response(jsonify(result='Blocked connection'), 503)


@app.teardown_request
def teardown_request(exception):
    """
    모든 API 실행 후 실행하는 부분. 여기서는 DB 연결종료.
    """
    pass


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify(result='존재하지 않는 페이지입니다'), 404)


@app.errorhandler(401)
def not_unauthorized(error):
    return make_response(jsonify(result='인증되지 않음'), 401)


@app.errorhandler(403)
def forbidden(error):
    # return abort(403)
    return make_response(jsonify(result='접근 금지!'), 403)


@app.route('/')
def hello_world():
    return redirect('/static/index.html')
