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


def ddos_check_and_write_log():
    """
    API 실행 전, 해당 IP에서 1초에 100번 이상 실행되면 30분동안 접속 차단한다.
    그리고 차단하지 않은 IP는 임시 테이블에 로그를 남겨 나중에 분석 자료로 이용한다.

    # 추후 변경 사항
    현재는 임시테이블(temp_actions_log)에 로그를 쌓고 있다.
    나중에 Agent가 30분에 한번씩 로그를 영구보관소로 옮길 예정

    :return: 우리 서비스를 계속 사용할 수 있는 자격 유무(True/False)
    """
    conn = db.engine.connect()
    trans = conn.begin()
    meta = MetaData(bind=db.engine)
    tal = Table('temp_actions_log', meta, autoload=True)
    bl = Table('blacklist', meta, autoload=True)
    is_ok = True

    method = request.method
    api_endpoint = request.environ['PATH_INFO']
    ip_address = request.remote_addr

    #: 사용자 id 받아오기
    if current_user.is_authenticated is True:
        uid = current_user.profile['id']
    else:
        uid = 0

    try:
        #: 1초동안 몇번 접속했는가?
        res1 = conn.execute(text("""SELECT count(*) as cnt FROM `marocat v1.1`.temp_actions_log 
                                    WHERE (user_id=:uid OR ip_address=:ip_address)
                                    AND log_time BETWEEN CURRENT_TIMESTAMP AND (CURRENT_TIMESTAMP - INTERVAL 1 SECOND)""")
                            , uid=uid, ip_address=ip_address).fetchone()
        conn_cnt = res1['cnt']

        #: 1초동안 100번이상 접속하면 블랙리스트 등록
        if conn_cnt > 100:
            for key in list(session.keys()):
                session.pop(key)

            conn.execute(bl.insert(), user_id=uid, ip_address=ip_address
                         , time_from=datetime.utcnow(), time_to=datetime.utcnow() + timedelta(minutes=30))
            is_ok = False

        #: 블랙리스트인가?
        res2 = conn.execute(text("""SELECT count(*) as cnt FROM `marocat v1.1`.blacklist 
                                    WHERE user_id=:uid
                                    AND CURRENT_TIMESTAMP BETWEEN time_from AND time_to""")
                            , uid=uid).fetchone()
        blacklist_cnt = res2['cnt']

        #: 블랙리스트라면 차단시키기 위해 세션값 먼저 삭제하기
        if blacklist_cnt > 0:
            for key in list(session.keys()):
                session.pop(key)
            is_ok = False

        #: 로그 저장 (temp_actions_log)
        conn.execute(tal.insert(), user_id=uid, ip_address=ip_address, method=method, api=api_endpoint)

        trans.commit()
        return is_ok
    except:
        print('Wrong (ddos_check_and_write_log)')
        traceback.print_exc()
        trans.rollback()
        return make_response(jsonify(result='Something Wrong'), 461)


def convert_datetime_4mysql(basedate):
    """
    client에서 보내주는 datetime이 MySQL 포맷에 맞지 않기 때문에 포맷형식을 바꿔주는 함수입니다
    """
    formatfrom = "%a, %d %b %Y %H:%M:%S GMT"
    formatto = "%Y-%m-%d %H:%M:%S"
    convertdate = datetime.strptime(basedate, formatfrom).strftime(formatto)
    return convertdate


def encrypt_pwd(password):
    """
    비밀번호 암호화하기
    """
    m = hashlib.sha512()
    m.update(password.encode('utf-8'))
    hashpwd = m.hexdigest()
    return hashpwd


def create_token(sth, size=13):
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


def send_mail(mail_to, title, content, mail_from='', name='', password=''):
    """
    :param mail_to: 받는 사람
    :param title: 이메일 제목
    :param content: 이메일 내용
    :param mail_from: 보내는 사람
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    try:
        content = MIMEText(content, 'html', _charset='utf-8')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = title
        msg['From'] = '{} team <{}>'.format(name, mail_from)
        msg['To'] = str(mail_to)
        msg.attach(content)

        a = smtplib.SMTP('smtp.gmail.com:587')
        a.ehlo()
        a.starttls()
        a.login(mail_from, password)
        a.sendmail('', str(mail_to), msg.as_string())
        a.quit()
        return True
    except:
        traceback.print_exc()
        return False


def upload_photo_to_bytes_on_s3(picture, mimetype, name):
    """
    S3에 Bytes로 사진 저장하기
    :param picture: 사진, bytes
    :param mimetype:
    :param name:
    :return: S3에 저장한 이름과 URL + 성공유무
    """
    try:
        t = create_token(name)
        pname = 'profile/' + str(datetime.utcnow().strftime('%Y%m%d%H%M%S')) + t + '.' + mimetype

        S3.upload_fileobj(io.BytesIO(picture), BUCKET_NAME, pname)

        # purl = S3.generate_presigned_url(
        #     ClientMethod='get_object',
        #     Params={
        #         'Bucket': BUCKET_NAME,
        #         'Key': pname
        #     }
        # )

        # return pname, purl, True
        return pname, True
    except:
        print('Wrong! (S3 upload_fileobj)')
        traceback.print_exc()
        return None, False
