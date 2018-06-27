# -*- coding: utf-8 -*-
from flask import Flask, make_response, jsonify, render_template
from flask_session import Session
from flask_cors import CORS
from flask_caching import Cache
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from flask_sslify import SSLify
import os

# Define the WSGI application object
app = Flask(__name__, static_url_path='/static')

#: Configurations
import configs

if os.environ.get('PURPOSE') == 'PROD':
    app.config.from_object(configs.ProdConfig)
elif os.environ.get('PURPOSE') == 'DEV':
    app.config.from_object(configs.DevConfig)
else:
    app.config.from_object(configs.Config)

#: Swagger
Swagger(app)

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

from app.swagger_example.urls import swag
app.register_blueprint(swag, url_prefix='/api/v1/swag')

from app.auth.urls import auth
app.register_blueprint(auth, url_prefix='/api/v1/auth')

from app.users.urls import users
app.register_blueprint(users, url_prefix='/api/v1/users')

# ##: Method 2: add_url_rule 사용할 때, Blueprint 안 쓸 때
# module 만들때마다 붙여줘라!
# import app.module01.urls as module01

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
    pass


@app.teardown_request
def teardown_request(exception):
    """
    모든 API 실행 후 실행하는 부분. 여기서는 DB 연결종료.
    """
    pass


# Sample HTTP error handling
@app.errorhandler(401)
def unauthorized(error):
    return make_response(jsonify(code=1000, message="Unauthorized",
                                 description="The server could not verify that you are authorized to access the URL requested. " +
                                 "You either supplied the wrong credentials (e.g. a bad password), " +
                                 "or your browser doesn't understand how to supply the credentials required."), 401)


@app.errorhandler(403)
def forbidden(error):
    return make_response(jsonify(code=3000, message="Forbidden",
                                 description="You don't have the permission to access the requested resource." +
                                 "It is either read-protected or not readable by the server."), 403)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify(code=4000, message="Not Found",
                                 description="The requested URL was not found on the server. " +
                                             "If you entered the URL manually please check your spelling and try again."), 404)


# The request was well-formed but was unable to be followed due to semantic errors.
@app.errorhandler(422)
def unprocessable_entity(error):
    return make_response(jsonify(code=2200, message="Unprocessable Entity",
                                 description="커버하지 못한 에러다아아아아아"), 422)


@app.route('/')
def hello_world():
    return render_template('index.html')
