# -*- coding: utf-8 -*-
from datetime import timedelta
import os

VERSION='0.1'
DEBUG=True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#: HOST
if os.environ.get('PURPOSE') == 'PROD':
    HOST=''
    #SESSION_COOKIE_DOMAIN=""
    #SESSION_COOKIE_PATH="/"
elif os.environ.get('PURPOSE') == 'DEV':
    HOST=''
    #SESSION_COOKIE_DOMAIN=""
    #SESSION_COOKIE_PATH="/"
else:
    HOST='http://localhost'

#: Session
SESSION_TYPE = 'redis'
SESSION_COOKIE_NAME = "SunnyFlaskBoilerplate"
PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
SECRET_KEY = os.urandom(24)

#: Swagger
SWAGGER = {
    'title': 'My flask API',
    'uiversion': 2
}

#: SQLAlchemy, DB
SQLALCHEMY_DATABASE_URI = 'driver://user:pass@localhost/dbname'
SQLALCHEMY_TRACK_MODIFICATIONS = True
# DATABASE_CONNECT_OPTIONS = {}

#: Facebook
FACEBOOK_APP_ID = ''
FACEBOOK_APP_SECRET = ''

#: AWS
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
REGION = ''

#: JSON으로 들어온 데이터들을 정렬해준다
JSON_SORT_KEYS=False
MAX_CONTENT_LENGTH=5 * 1024 * 1024
UPLOAD_FOLDER_RESULT="results"

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
# THREADS_PER_PAGE = 2
