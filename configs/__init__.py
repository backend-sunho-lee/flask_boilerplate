# -*- coding: utf-8 -*-
from datetime import timedelta
import os


class Config(object):
    VERSION = '0.1'
    DEBUG = True

    # Define the application directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    PORT = 5001
    HOST=''
    SSL_KEY = './configs/cert_key/cert_key.key'
    SSL_CERT = './configs/cert_key/cert_key.crt'

    #: Session
    SESSION_TYPE = 'redis'
    SESSION_COOKIE_NAME = ""
    REMEMBER_COOKIE_DURATION = timedelta(days=15)
    SECRET_KEY = os.urandom(24)

    #: Swagger
    SWAGGER = {
        'title': 'Flask Boilerplate API',
        'uiversion': 2
    }

    #: SQLAlchemy, DB
    DATABASE_CONFIG = {
        'driver': 'mysql+pymysql',
        'host': '',
        'dbname': '',
        'user': '',
        'password': '',
        'port': 3306
    }
    SQLALCHEMY_DATABASE_URI = '{driver}://{user}:{password}@{host}/{dbname}'.format(**DATABASE_CONFIG)
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    #: JSON으로 들어온 데이터들을 정렬해준다
    JSON_SORT_KEYS=False
    MAX_CONTENT_LENGTH=5 * 1024 * 1024
    UPLOAD_FOLDER_RESULT="results"

    #: Google
    GOOGLE_CLIENT_SECRETS_FILE = './configs/google_client_secret.json'

    #: Facebook
    FACEBOOK_APP_ID = ''
    FACEBOOK_APP_SECRET = ''

    #: AWS
    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''
    REGION = 'a'

    MANAGER_MAIL = ''

    # Application threads. A common general assumption is using 2 per available processor cores
    # - to handle incoming requests using one and performing background operations using the other.
    # THREADS_PER_PAGE = 2


class ProdConfig(Config):
    pass


class DevConfig(Config):
    pass


class TestConfig(Config):
    pass
