# -*- coding: utf-8 -*-
from flask import Flask
from flask_cors import CORS
from flask_session import Session
from flask_caching import Cache
from flasgger import Swagger

# Define the WSGI application object
app = Flask(__name__)

#: Configurations
import configs
app.config.from_object(configs)

#: Swagger
Swagger(app)

# Flask-Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

#: Flask-Session
Session(app)

#: Flask-CORS
cors = CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": "true"}})


###: DB 연결
# 저는 configs에 설정해서 바로 연결해서 쓸 수 있도록 했습니다.

# Import SQLAlchemy
# from flask.ext.sqlalchemy import SQLAlchemy
# from flask_sqlalchemy import SQLAlchemy

# Define the database object which is imported
# by modules and controllers
# db = SQLAlchemy(app)

# Build the database:
# This will create the database file using SQLAlchemy
# db.create_all()


#################################### 모듈 연결시키기 ####################################

# API Version
versions = ['/api/v1']

###: Method 1: Blueprint 사용할 때
# Import a module / component using its blueprint handler variable (mod_auth)
from app.module01.urls import module01
from app.auth.urls import auth

# Register blueprint(s)
#: 버전이 여러개일 경우, 버전을 하나씩 삽입할까? 아니면 그전처럼 배열로해서 다 돌아가게 할까
# for version in versions:
#     app.register_blueprint(module01, url_prefix='{}/module01'.format(version))

app.register_blueprint(module01, url_prefix='/api/v1/module01')
# app.register_blueprint(module01, url_prefix='/api/v2/module01')
app.register_blueprint(auth, url_prefix='/api/v1/auth')

###: Method 2: add_url_rule 사용할 때
# module 만들때마다 붙여줘라!
import app.module02.urls as module02

#: 등록된 url 확인하기
print(app.url_map)

#####################################################################################

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
@app.errorhandler(404)
def not_found(error):
    return 'Not Found!!!!!'

@app.route('/')
def hello_world():
    return 'Hello World!'
