# -*- coding: utf-8 -*-
from datetime import timedelta

VERSION='0.1'
DEBUG=True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#: Define the database
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
# DATABASE_CONNECT_OPTIONS = {}


#: HOST
if os.environ.get('PURPOSE') == 'PROD':
    HOST='http://ciceron.me'
    #SESSION_COOKIE_DOMAIN=".ciceron.me"
    #SESSION_COOKIE_PATH="/"
elif os.environ.get('PURPOSE') == 'DEV':
    HOST='http://ciceron.xyz'
    #SESSION_COOKIE_DOMAIN=".ciceron.xyz"
    #SESSION_COOKIE_PATH="/"
else:
    HOST='http://localhost'


#: Session
SESSION_TYPE='redis'
SESSION_COOKIE_NAME="CiceronCookie"
PERMANENT_SESSION_LIFETIME=timedelta(days=15)
SECRET_KEY='Yh1onQnWOJuc3OBQHhLFf5dZgogGlAnEJ83FacFv'

#: Swagger
SWAGGER = {
    'title': 'My flask API',
    'uiversion': 2
}


#: JSON으로 들어온 데이터들을 정렬해준다
JSON_SORT_KEYS=False
MAX_CONTENT_LENGTH=4 * 1024 * 1024
UPLOAD_FOLDER_RESULT="translate_result"


#: Facebook
FACEBOOK_APP_ID=256525961180911
FACEBOOK_APP_SECRET='e382ac48932308c15641803022feca13'

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
# THREADS_PER_PAGE = 2
