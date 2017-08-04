# -*- coding: utf-8 -*-
"""
###: Alembic 사용법
# 참고: http://alembic.zzzcomputing.com/en/latest/tutorial.html

alembic init alembic
#: alembic 설치. 프로젝트 시작할 때 한 번만 해주면 된다

alembic revision --autogenerate -m "initial_migration"
#: 자동으로 alembic 버전 파일 만들기, 변경사항이 적용된 버전 파일 만들어진다.
# 맨 처음 초기화용으로 쓰려면 방법 다시 알아봐야할 듯..

alembic revision -m '제목, 간단한 설명을 넣어주세요'
#: alembic 버전 파일 만들기
# 빈 파일이 만들어지며 버전업할 사람이 직접 SQL문 작성하여 올릴 수 있다.

alembic upgrade head
#: 제일 최신의 버전 파일 적하기
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateTable
from datetime import datetime

SCHEMA_NAME = ''

DEV_DATABASE = {'user': '',
                'password': '',
                'host': '',
                'database': ''}


def connectDB(db_info, schema_name):
    """
    :param db_info: dict, DataBase Information
    :param schema_name: str, schema name
    :return: Connected engine and base
    """

    #: MySQL
    url = 'mysql+pymysql://{user}:{password}@{host}:3306/{database}?'.format(**db_info)
    engine = create_engine(url, convert_unicode=True, echo=True)

    #: PostgreSQL
    # url = 'postgresql+psycopg2://{user}:{password}@{host}:5432/{database}'.format(**db_info)
    # engine = create_engine(url, client_encoding='utf8')

    # conn = engine.connect()
    Base = declarative_base(metadata=MetaData(schema=schema_name, bind=engine))

    # Import the schema's information into metadata.
    Base.metadata.reflect(engine)
    return Base, engine


def saveSQLfile(base):
    """
    :param base: what you want to store
    :return: SQL file
    """
    file_date = datetime.now().strftime('%Y%m%d_%H%M%S')
    tables = base.metadata.tables
    for table in tables.values():
        rawSQL = str(CreateTable(table))
        with open('./sql_files/schema_{}.sql'.format(file_date), 'a') as text_file:
            text_file.write(rawSQL)


# Base, engine = connectDB(DEV_DATABASE, SCHEMA_NAME)
# conn = engine.connect()

#: Raw SQL문 파일 저장하기
# saveSQLfile(Base)

#: DB Pool 설정
# import sqlalchemy.pool as pool
# dbPool = pool.QueuePool(conn, max_overflow=10, pool_size=5)
