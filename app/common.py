#: 여기저기서 자꾸쓰는 함수 모음집
from app import app, db
from flask import request, session, make_response, jsonify
from sqlalchemy import Table, MetaData, text, exc
from flask_login import current_user
from datetime import datetime, timedelta
import hashlib
import string
import random
import traceback
import io

import boto3
S3 = boto3.client(
        's3',
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
        # aws_session_token=SESSION_TOKEN,
    )
BUCKET_NAME = ''


def convert_datetime4mysql(basedate):
    """
    client에서 보내주는 datetime이 MySQL 포맷에 맞지 않기 때문에 포맷형식을 바꿔주는 함수입니다
    """
    formatfrom = "%a, %d %b %Y %H:%M:%S GMT"
    formatto = "%Y-%m-%d %H:%M:%S"
    convertdate = datetime.strptime(basedate, formatfrom).strftime(formatto)
    return convertdate


def create_sha512_hash(password):
    m = hashlib.sha512()
    m.update(password.encode('utf-8'))
    return m.hexdigest()


def create_md5_hash(sth):
    md5 = hashlib.md5()
    md5.update(sth.encode('utf-8'))
    return md5.hexdigest()


def create_sha1_token(sth, size=13):
    """
    토큰 만들기
    sth과 현재시간(UTC)을 가지고 해싱하여 토큰을 만든다.

    :param sth: 이 함수를 사용하는 어딘가에서 쓰이는 아무 변수
    :param len: 원하는 토큰의 길이
    :return:
    """
    m = hashlib.sha1()

    t1 = sth + str(datetime.utcnow())
    m.update(t1.encode('utf-8'))
    t2 = m.hexdigest()
    t3 = t2 + string.ascii_uppercase

    token = ''.join(random.choice(t3) for _ in range(size))
    return token


def upload_photo_to_bytes_on_s3(picture, mimetype, name):
    """
    S3에 Bytes로 사진 저장하기
    :param picture: 사진, bytes
    :param mimetype:
    :param name:
    :return: S3에 저장한 이름과 URL + 성공유무
    """
    try:
        t = ''
        pname = ''

        S3.upload_fileobj(io.BytesIO(picture), BUCKET_NAME, pname)

        # purl = S3.generate_presigned_url(
        #     ClientMethod='get_object',
        #     Params={
        #         'Bucket': BUCKET_NAME,
        #         'Key': pname
        #     }
        # )

        return pname, True
    except:
        traceback.print_exc()
        return None, False
