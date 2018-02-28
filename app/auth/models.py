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
BUCKET_NAME = 'marocat'
BUCKET_FOLDER = 'profile/'


class User(UserMixin):
    def can_login(self, password):
        conn = db.engine.connect()
        res = conn.execute(text("""SELECT password = SHA2(:pwd, 512) as is_correcct FROM users WHERE email = :uid"""), pwd=password, uid=self.get_id()).fetchone()

        if res['is_correcct'] == 1:
            return True
        else:
            return False


def insert_user(signup_type, name, email, password, social_id, picture):
    conn = db.engine.connect()
    trans = conn.begin()
    meta = MetaData(bind=db.engine)
    u = Table('users', meta, autoload=True)

    hashpwd = common.encrypt_pwd(password)

    #: 사진이 있는 경우, S3에 저장하기
    try:
        if len(picture) > 15:
            r = requests.get(picture)
            pic = copy.deepcopy(r.content)

            #: 업로드할 파일 이름짓기
            t = common.create_token(email, 7)
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
        print('Wrong! (S3 upload_fileobj)')
        traceback.print_exc()
        return 3

    #: 데이터베이스에 사용자 저장하기
    try:
        if signup_type == 'local':
            res = conn.execute(u.insert(), email=email, name=name, password=hashpwd)
        elif signup_type == 'facebook':
                res = conn.execute(u.insert(), email=email, name=name, password=hashpwd
                                   , facebook_id=social_id, facebook_email=email, facebook_name=name
                                   , conn_facebook_time=datetime.utcnow()
                                   , picture_s3key=pname, thumbnail_s3key=tname)
        elif signup_type == 'google':
            res = conn.execute(u.insert(), email=email, name=name, password=hashpwd
                               , google_id=social_id, google_email=email, google_name=name
                               , conn_google_time=datetime.utcnow()
                               , picture_s3key=pname, thumbnail_s3key=tname)

        if res.rowcount != 1:
            print('DUP! (user is already exist, local)')
            trans.rollback()
            return 2

        is_done = send_email_for_cert_signup(email)
        if is_done is False:
            trans.rollback()
            return 0

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
        if social_type == 'facebook':
            res = conn.execute(u.update(u.c.email == email)
                               , facebook_id=social_id, facebook_email=social_email, facebook_name=social_name
                               , conn_facebook_time=datetime.utcnow(), update_time=datetime.utcnow())

        elif social_type == 'google':
            res = conn.execute(u.update(u.c.email == email)
                               , google_id=social_id, google_email=social_email, google_name=social_name
                               , conn_google_time=datetime.utcnow(), update_time=datetime.utcnow())

        # if res.rowcount != 1:
        #     trans.rollback()
        #     return False

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
        #: 16자리 인증코드 생성
        cert_token = common.create_token(email, size=16)
        res = conn.execute(t.insert(), token=cert_token, issue_to=email
                           , memo=email+'에게 로컬 회원가입 인증코드 전송')

        if res.rowcount != 1:
            print('Wrong! (create_token or insert_token)')
            trans.rollback()
            return False

        #: 인증코드 이메일 보내기
        title = '마이캣툴 인증 코드입니다.'
        with open('app/static/front/user/email_form.html', 'r') as f:
            file = f.read()

        content = file.format(cert_token=cert_token, email=email)
        is_done = common.send_mail(email, title, content)

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

    try:
        #: 16자리 인증코드 생성
        new_pwd = common.create_token(email, size=16)
        res = conn.execute(t.insert(), token=new_pwd, issue_to=email, memo=email+'님이 비밀번호 찾기 요청')
        if res.rowcount != 1:
            print('Wrong! (create_token or insert_token)')
            trans.rollback()
            return False

        #: 변경된 비밀번호로 바꾸기
        hash_new_pwd = common.encrypt_pwd(new_pwd)
        res = conn.execute(u.update(whereclause=(and_(u.c.email == email, u.c.is_deleted == False))), password=hash_new_pwd, update_time=datetime.utcnow())
        if res.rowcount < 1:
            print('Wrong! (update_user_password)')
            trans.rollback()
            return False

        #: 인증코드 이메일 보내기
        title = '마이캣툴에서 새로운 비밀번호를 발급했습니다'
        with open('app/static/front/user/find_pass_email.html', 'r') as f:
            file = f.read()

        content = file.format(password=new_pwd, email=email)
        is_done = common.send_mail(email, title, content)

        if is_done is True:
            trans.commit()
            return True
        else:
            print('Wrong! (send_mail)')
            trans.rollback()
            return False
    except:
        print('Wrong! (send_email_for_recovery_pwd)')
        traceback.print_exc()
        trans.rollback()
        return False


def cert_local_user(email, cert_token):
    conn = db.engine.connect()
    trans = conn.begin()
    meta = MetaData(bind=db.engine)
    u = Table('users', meta, autoload=True)

    try:
        #: 인증코드 확인
        res = conn.execute(text("""UPDATE `marocat v1.1`.token
                                  SET is_used = TRUE, update_time = CURRENT_TIMESTAMP()
                                  WHERE issue_to=:email AND token=:token""")
                           , email=email, token=cert_token)

        if res.rowcount != 1:
            print('Wrong! (update token, {})'.format(res.rowcount))
            trans.rollback()
            return 2

        #: 사용자 인증 정보 수정
        res = conn.execute(u.update(u.c.email == email and u.c.is_deleted == False), is_certified=True, update_time=datetime.utcnow())

        # if res.rowcount != 1:
        #     print('Wrong! (update users, {})'.format(res.rowcount))
        #     trans.rollback()
        #     return False

        trans.commit()
        return True
    except:
        print('Wrong! (update_user_local_info)')
        traceback.print_exc()
        trans.rollback()
        return False


def select_user(input_id):
    conn = db.engine.connect()

    res = conn.execute(text("""SELECT id, name, email, thumbnail_s3key as thumbnail
                                    , is_certified
                                    , facebook_id, facebook_email, facebook_name
                                    , google_id, google_email, google_name
                              FROM `marocat v1.1`.users 
                              WHERE (email=:input_id OR facebook_id=:input_id OR google_id=:input_id) 
                              AND is_deleted=FALSE ;"""), input_id=input_id).fetchone()

    if res is None:
        return None, 0
    elif res['is_certified'] == 0:
        return None, 2
    else:
        user = User()
        user.id = res['email']
        user.nickname = res['name']
        user.picture = '/api/v1/users/me/picture/' + res['thumbnail']
        return user, 1


def select_user_profile_by_email(email):
    conn = db.engine.connect()
    res = conn.execute(text("""SELECT id, name, email, thumbnail_s3key as thumbnail
                                    , facebook_id, facebook_email, facebook_name, conn_facebook_time
                                    , google_id, google_email, google_name, conn_google_time
                              FROM `marocat v1.1`.users 
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
            'picture': '/api/v1/users/me/picture/' + res['thumbnail'],
            'facebook': {
                'id': res['facebook_id'],
                'email': res['facebook_email'],
                'name': res['facebook_name'],
                'connect_time': res['conn_facebook_time']
            },
            'google': {
                'id': res['google_id'],
                'email': res['google_email'],
                'name': res['google_name'],
                'connect_time': res['conn_google_time']
            }
        }

        return user
