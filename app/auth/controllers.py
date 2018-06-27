from flask import request, make_response, url_for, session, redirect, jsonify, json, abort
import app.auth.models as model
from app import app
import traceback
import requests
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_oauthlib.client import OAuth
import google.oauth2.credentials
import google_auth_oauthlib.flow


#: flask_login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'strong'

#: flask_oauthlib
oauth = OAuth()
facebook = oauth.remote_app(
    'facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=app.config['FACEBOOK_APP_ID'],
    consumer_secret=app.config['FACEBOOK_APP_SECRET'],
    request_token_params={'scope': 'email'}
)

#: google_oauth
SCOPES = ['https://www.googleapis.com/auth/plus.login',
          'https://www.googleapis.com/auth/plus.me',
          'https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email']


@login_manager.user_loader
def user_loader(uid):
    user = model.select_user_profile_by_email(uid)
    return user


def signup(signup_type):
    name = request.form.get('nickname', None)
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    social_id = request.form.get('social_id', None)
    picture = request.form.get('picture', None)

    if None in [email, password, name]:
        return make_response(jsonify(code=2201, message="Something Not Entered",
                                     description="email, password, name을 다시 한번 확인해주세요;("),
                             422)
    elif (signup_type == 'facebook' or signup_type == 'google') and social_id is None:
        return make_response(jsonify(code=2201, message="Unprocessable Entity",
                                     description="signupType, socialId를 다시 한번 확인해주세요;("), 422)

    #: 비밀번호 검사
    if len(password) < 4:
        return make_response(jsonify(code=2202, message="Invalid data format",
                                     description="비밀번호는 4글자 이상이어야 해요;("), 422)

    #: 존재하는 사용자인지 확인하기
    user, is_ok = model.select_user(email)
    if is_ok == 1:
        return make_response(jsonify(code=2203, message="Duplication",
                                     description="이미 가입한 사용자입니다. 로그인 해주세요;)"), 422)
    elif is_ok == 2:
        return make_response(jsonify(code=2203, message="Duplication",
                                     description="이미 가입한 사용자입니다. 이메일 인증 후 로그인해주세요:O"
                                     ), 422)

    #: 사용자 DB에 저장 + 인증 이메일 보내기
    is_done, uid = model.insert_user(signup_type, name, email, password, social_id, picture)

    if is_done is 1:
        return make_response(jsonify(uid=uid,
                                     message="회원가입 성공! 이메일 인증 후 로그인 가능합니다:^)"), 201)
    elif is_done is 2:
        return make_response(jsonify(code=2203, message="Duplication",
                                     description="이미 가입한 사용자입니다:O"), 422)
    elif is_done is 3:
        return make_response(jsonify(code=901, message="Conflict",
                                     description="프로필 사진 업로드 중 에러가 발생했어요;("), 409)
    else:
        return abort(422)


def cert_local_signup():
    email = request.values.get('email', None)
    cert_token = request.values.get('cert_token', None)

    if None in [email, cert_token]:
        return make_response(jsonify(code=2201, message="Something Not Entered",
                                     description="email, cert_token을 다시 한번 확인해주세요;("), 422)

    is_done, uid = model.cert_local_user(email, cert_token)

    if is_done is True:
        return make_response(jsonify(uid=uid, message="인증 성공!:^)"), 200)
    elif is_done is 2:
        return make_response(jsonify(code=1001, message="Unauthorized",
                                     description="email, cert_token을 다시 한번 확인해주세요;("), 401)
    else:
        return abort(422)


def signout():
    if current_user:
        user = current_user
        user.authenticated = False
    session.clear()
    logout_user()

    return make_response(jsonify(message="로그아웃 성공!:^)"), 200)


def local_signin():
    signout()

    email = request.form.get('email', None)
    password = request.form.get('password', None)

    if None in [email, password]:
        return make_response(jsonify(code=2201, message="Something Not Entered",
                                     description="email, password를 다시 한번 확인해주세요;("), 422)

    user, is_ok = model.select_user(email)

    if is_ok == 0:
        return make_response(jsonify(code=4001, message="Not Found", description="존재하지 않는 이메일이에요;("), 404)
    elif is_ok == 2:
        return make_response(jsonify(code=1002, message="Unauthorized",
                                     description="인증되지 않은 이메일이네요;("), 401)
    else:
        #: 존재하는 사용자라면 입력된 password가 맞는지 확인
        is_ok = user.can_login(password)

        #: 비밀번호가 일치한다면 login_user에 user 정보를 넣고, 로그인 완료!
        if is_ok is True:
            login_user(user)
            session['user_nickname'] = user.nickname
            session['user_picture'] = user.picture

            return make_response(jsonify(uid=user.idx, message="로그인 성공!:^)"), 200)
        else:
            return make_response(jsonify(code=1001, message="Unauthorized",
                                         description="비밀번호 틀렸어요;("), 401)


def social_callback(social_type, social_id, social_name, social_email, picture):
    # social_type = request.values.get('social_type', None)
    # social_id = request.values.get('social_id', None)
    # social_name = request.values.get('social_name', None)
    # social_email = request.values.get('social_email', None)
    # picture = request.values.get('picture', None)

    #: 존재하는 소셜 사용자인지 확인 = 소셜 존재 유무 확인
    user, is_ok = model.select_user(social_id)

    #: 소셜 존재
    if user:
        #: 소셜 존재함 + 로그아웃 상태 --> 로그인 시키기
        if current_user.is_authenticated is False:
            login_user(user, remember=True)
            session['user_nickname'] = user.nickname
            session['user_picture'] = user.picture

            return redirect('')

        #: 소셜 존재함 + 로그인 상태
        elif current_user.is_authenticated is True:
            #: + 로그인한 사용자와 소셜이 연결된 사용자가 다른 경우 --> 연동 실패 메세지 + 사용자 정보 페이지로 이동
            if user.id != current_user.id:
                # return render_template('user/userinfo.html'
                #                        , result_en="Already connected to another account"
                #                        , result_ko="이미 다른 계정과 연결되었습니다"
                #                        , result=264)
                return redirect(url_for('static', filename='',
                                        code=2203, message="Duplication",
                                        description="이미 다른 계정에 연동되었네요:O"))

            else:
                return redirect(url_for('static', filename='',
                                        message="소셜 연동 성공!:^D"))

    #: 소셜 존재함 + 이메일 인증되지 않음 --> 로그인 페이지로 이동
    if is_ok == 2:
        return redirect(url_for('static', filename='',
                                code=1002, message="Unauthorized",
                                description="이메일 인증을 아직 안하셨네요;("))

    #: 소셜 존재하지 않음
    if not user:
        #: 소셜 존재하지 않음 + 로그인 상태 --> 페이스북 연동 시키기 + 사용자 정보 페이지로 이동
        if current_user.is_authenticated is True:
            email = current_user.id
            is_done = model.update_user_social_info(social_type, email, social_id, social_email, social_name)
            if is_done is True:
                return redirect(url_for('static', filename='',
                                        message="소셜 연동 성공!:^D"))

            else:
                return redirect(url_for('static', filename='',
                                        code=5301, message="Service Unavailable",
                                        description="소셜 연동 중 일시적인 오류가 발생하였어요;("))

        #: 소셜 존재하지 않음 + 이메일 존재 --> 로그인 페이지로 이동
        luser, is_ok2 = model.select_user(social_email)
        if luser is not None:
            return redirect(url_for('static', filename='',
                                    code=2203, message="Duplication",
                                    description="다른 방법으로 가입하시지 않았나요?;)"))

        #: 소셜 존재하지 않음 + 로그아웃 상태 --> 회원가입 페이지로 이동
        if current_user.is_authenticated is False:
            results = {
                'signup_type': social_type,
                'social_id': social_id,
                'name': social_name,
                'email': social_email,
                'picture': picture
            }
            return redirect(url_for('static', filename='', **results))

    print('이건 무슨 경우의 수일까..')
    return redirect('')


#: Facebook
def facebook_signin():
    return facebook.authorize(callback=url_for('auth.facebook_authorized',
                                               next=request.args.get('next') or None,
                                               _external=True))


def facebook_authorized():
    try:
        resp = facebook.authorized_response()
    except:
        traceback.print_exc()
        return make_response(jsonify(code=5301, message="Service Unavailable",
                                     description="Facebook의 일시적인 오류입니다"), 503)

    if resp is None:
        return make_response(jsonify(code=3001, message="Forbidden",
                                     description="Access denied! \n{} \n{}".format(request.args['error_reason'], request.args['error_description'])
                                     ), 403)

    elif 'access_token' not in resp:
        return make_response(jsonify(code=3001, message="Forbidden",
                                     description="No access token from Facebook."), 403)

    session['facebook_token'] = (resp['access_token'], '')
    data = facebook.get('/me?fields=email,name,picture').data

    user_info = {
        'social_type': 'facebook',
        'social_id': data['id'],
        'social_name': data['name'],
        'social_email': data.get('email'),
        'picture': data['picture']['data']['url']
    }
    return social_callback(**user_info)
    # return redirect(url_for('auth.social_callback', social_type='facebook', social_id=data['id']
    #                         , social_name=data['name'], social_email=data.get('email')
    #                         , picture=data['picture']['data']['url']))


@facebook.tokengetter
def facebook_tokengetter():
    return session.get('facebook_token')


#: 구글
def google_signin():
    if 'google_credentials' not in session:
        return redirect(url_for('auth.google_authorized'))

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(**session['google_credentials'])

    # drive = googleapiclient.discovery.build('oauth2', 'v1', credentials=credentials)
    # files = drive.files().list().execute()

    session['google_credentials'] = google_credentials_to_dict(credentials)

    authorization_header = {"Authorization": "OAuth %s" % session['google_credentials']['token']}
    res = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=authorization_header)
    data = json.loads(res.text)

    user_info = {
        'social_type': 'google',
        'social_id': data['id'],
        'social_name': data['name'],
        'social_email': data['email'],
        'picture': data['picture']
    }
    return social_callback(**user_info)
    # return redirect(url_for('auth.social_callback', social_type='google', social_id=data['id']
    #                         , social_name=data['name'], social_email=data['email'], picture=data['picture']))


def google_authorized():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(app.config['GOOGLE_CLIENT_SECRETS_FILE'],
                                                                   scopes=SCOPES)

    flow.redirect_uri = url_for('auth.google_oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['google_state'] = state

    return redirect(authorization_url)


def google_oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    error = request.values.get('error', None)
    if error is not None:
        return make_response(jsonify(error=error), 403)

    state = session['google_state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(app.config['GOOGLE_CLIENT_SECRETS_FILE'],
                                                                   scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('auth.google_oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these credentials in a persistent database instead.
    session['google_credentials'] = google_credentials_to_dict(flow.credentials)

    return redirect(url_for('auth.google_signin'))


def google_revoke():
    if 'google_credentials' not in session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(**session['google_credentials'])

    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return make_response(jsonify(message="Credentials successfully revoked."), 204)
    else:
        traceback.print_exc()
        return abort(422)


def google_credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def recovery_password():
    email = request.form.get('email', None)

    is_done, msg, updated_email = model.send_email_for_recovery_pwd(email)
    if is_done is True:
        return make_response(jsonify(email=updated_email, message="새로운 비밀번호를 이메일로 보냈습니다!:)"), 200)
    else:
        return make_response(jsonify(code=902, message="Conflict",
                                     description=msg), 409)


#: (for test) session check
def get_session():
    return make_response(jsonify(**session), 200)
