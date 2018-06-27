from sqlalchemy import Table, MetaData, text, and_
from app import app, db, common
import traceback
from flask_login import UserMixin
from datetime import datetime
import requests
import re
import io
import copy

import boto3
from PIL import Image
S3 = boto3.client(
        's3',
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
        # aws_session_token=SESSION_TOKEN,
    )
BUCKET_NAME = ''
BUCKET_FOLDER = ''


class User(UserMixin):
    def can_login(self, password):
        #: 로그인 할 수 있는 사용자인지 확인
        return True


def insert_user(signup_type, name, email, password, social_id, picture):
    conn = db.engine.connect()
    trans = conn.begin()
    meta = MetaData(bind=db.engine)
    u = Table('users', meta, autoload=True)

    hashpwd = ''

    #: 사진이 있는 경우, S3에 저장하기
    try:
        if len(picture) > 15:
            r = requests.get(picture)
            pic = copy.deepcopy(r.content)

            #: 업로드할 파일 이름짓기
            t = ''
            udate = str(datetime.utcnow().strftime('%Y%m%d%H%M%S'))
            _pname = t + udate

            mimetype = re.split('/', r.headers['Content-Type'])
            if mimetype[1] != 'png':
                mtype = '.jpg'
            else:
                mtype = '.' + mimetype[1]

            #: 원본 이미지 저장
            pname = _pname + mtype
            S3.upload_fileobj(io.BytesIO(pic), BUCKET_NAME, BUCKET_FOLDER+pname)

            #: 썸네일 저장
            #: 원본 사이즈가 (100,100) 이하인 경우는 원본 그대로 저장
            tname = _pname + 't' + mtype
            img = Image.open(io.BytesIO(pic))

            imgsize = img.size
            if imgsize[0] > 100 or imgsize[1] > 100:
                img.thumbnail((100, 100), Image.ANTIALIAS)
                b = io.BytesIO()
                img.save(b, format=mimetype[1].upper())
                timg_bytes = b.getvalue()

                S3.upload_fileobj(io.BytesIO(timg_bytes), BUCKET_NAME, BUCKET_FOLDER+tname)
            else:
                S3.upload_fileobj(io.BytesIO(pic), BUCKET_NAME, BUCKET_FOLDER+tname)

            # purl = S3.generate_presigned_url(
            #     ClientMethod='get_object',
            #     Params={
            #         'Bucket': BUCKET_NAME,
            #         'Key': pname
            #     }
            # )
        else:
            pname = 'noman.png'
            tname = 'noman_thumbnail.png'
    except:
        traceback.print_exc()
        return 3

    try:
        #: 데이터베이스에 사용자 저장하기
        #: 사용자에게 환영 이메일 보내기

        trans.commit()
        return 1
    except:
        traceback.print_exc()
        trans.rollback()
        return 0
    finally:
        conn.close()


def update_user_social_info(social_type, email, social_id, social_email=None, social_name=None):
    conn = db.engine.connect()
    trans = conn.begin()
    meta = MetaData(bind=db.engine)
    u = Table('users', meta, autoload=True)

    try:
        #: 소셜 연동시 작업...

        trans.commit()
        return True
    except:
        traceback.print_exc()
        trans.rollback()
        return False
    finally:
        conn.close()


def send_email_for_cert_signup(email):
    conn = db.engine.connect()
    trans = conn.begin()
    meta = MetaData(bind=db.engine)
    t = Table('token', meta, autoload=True)

    try:
        #: 인증코드 생성

        #: 인증코드 이메일 보내기

        if is_done is True:
            trans.commit()
            return True
        else:
            print('Wrong! (send_mail)')
            trans.rollback()
            False
    except:
        print('Wrong! (send_email_for_local_signup)')
        traceback.print_exc()
        trans.rollback()
        return False


def send_email_for_recovery_pwd(email):
    conn = db.engine.connect()
    trans = conn.begin()
    meta = MetaData(bind=db.engine)
    t = Table('token', meta, autoload=True)
    u = Table('users', meta, autoload=True)
    msg = ""

    try:
        #: 새로운 비밀번호 발급
        new_pwd = ''

        #: 변경된 비밀번호로 바꾸기

        #: 인증코드 이메일 보내기
        title = ''
        content = ''
        is_done = common.send_mail(email, title, content)

        if is_done is True:
            trans.commit()
            return True, msg
        else:
            trans.rollback()
            msg = "새로운 비밀번호를 메일로 보내다가 에러 발생했다."
            return False, msg
    except:
        traceback.print_exc()
        trans.rollback()
        msg = "!!!에러!!!"
        return False, msg


def cert_local_user(email, cert_token):
    conn = db.engine.connect()
    trans = conn.begin()
    meta = MetaData(bind=db.engine)

    try:
        # 인증하기

        trans.commit()
        return True
    except:
        traceback.print_exc()
        trans.rollback()
        return False


def select_user(input_id):
    conn = db.engine.connect()

    res = conn.execute(text(""), input_id=input_id).fetchone()

    if res is None:
        return None, 0
    elif res['is_certified'] == 0:
        return None, 2
    else:
        user = User()
        user.idx = res['id']
        user.id = res['email']
        user.nickname = res['name']
        user.picture = res['thumbnail']
        return user, 1


def select_user_profile_by_email(email):
    conn = db.engine.connect()
    res = conn.execute(text("""SELECT id, name, email, thumbnail
                                    , facebook_id, facebook_email, facebook_name, conn_facebook_time
                                    , google_id, google_email, google_name, conn_google_time
                              FROM users 
                              WHERE email=:email AND is_deleted=FALSE;""")
                       , email=email).fetchone()

    if res is None:
        return None
    else:
        user = User()
        user.id = res['email']
        user.idx = res['id']

        user.profile = {
            'id': res['id'],
            'email': res['email'],
            'name': res['name'],
            'picture': res['thumbnail'],
            'facebook': {
                'id': res['facebook_id'],
                'email': res['facebook_email'],
                'name': res['facebook_name'],
            },
            'google': {
                'id': res['google_id'],
                'email': res['google_email'],
                'name': res['google_name'],
            }
        }

        return user
