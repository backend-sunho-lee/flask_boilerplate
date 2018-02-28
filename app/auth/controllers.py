from flask import request, make_response, json, url_for, session, redirect, jsonify, flash
import app.auth.models as model
from app import app
import traceback
import requests

from flask_login import LoginManager, login_user, logout_user, current_user
login_manager = LoginManager()
login_manager.init_app(app)

from flask_oauthlib.client import OAuth
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

twitter = oauth.remote_app(
    'twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=app.config['TWITTER_CONSUMER_KEY'],
    consumer_secret=app.config['TWITTER_CONSUMER_SECRET']
)

import google.oauth2.credentials
import google_auth_oauthlib.flow
CLIENT_SECRETS_FILE = "google_client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/plus.login'
    , 'https://www.googleapis.com/auth/plus.me'
    , 'https://www.googleapis.com/auth/userinfo.profile'
    , 'https://www.googleapis.com/auth/userinfo.email']


@login_manager.user_loader
def user_loader(uid):
    user = model.select_user_profile_by_email(uid)
    return user


def signup(signup_type):
    """
    회원가입
    """
    # signup_type = request.form.get('signup_type', None)
    name = request.form.get('nickname', None)
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    social_id = request.form.get('social_id', None)
    picture = request.form.get('picture', None)

    if None in [email, password, name]:
        return make_response(json.jsonify(result_en='Something Not Entered'
                                          , result_ko='입력되지 않은 값이 있습니다'
                                          , result=460), 460)
    elif (signup_type == 'facebook' or signup_type == 'google') and social_id is None:
        return make_response(json.jsonify(result_en='Something Not Entered'
                                          , result_ko='입력되지 않은 값이 있습니다'
                                          , result=460), 460)

    #: 비밀번호 검사
    if len(password) < 4:
        return make_response(json.jsonify(result_en='Password must be at least 4 digits'
                                          , result_ko='비밀번호는 4자리 이상이어야 합니다.'
                                          , result=467), 467)

    #: 존재하는 사용자인지 확인하기
    user, is_ok = model.select_user(email)
    if is_ok in [1, 2]:
        return make_response(json.jsonify(result_en='You are already signed up'
                                          , result_ko='이미 가입한 사용자입니다'
                                          , result=260), 260)

    #: 사용자 DB에 저장 + 인증 이메일 보내기
    is_done = model.insert_user(signup_type, name, email, password, social_id, picture)

    if is_done is 1:
        return make_response(json.jsonify(result_en='Congratulation! You successfully sign-up!'
                                          , result_ko='축하합니다! 회원가입에 성공했습니다! \n이메일 인증 후 이용 가능합니다'
                                          , result=200), 200)
    elif is_done is 2:
        return make_response(json.jsonify(result_en='This email already exists'
                                          , result_ko='이미 가입된 이메일입니다'
                                          , result=260), 260)
    elif is_done is 3:
        return make_response(json.jsonify(result_en='Picture upload failed'
                                          , result_ko='프로필 사진 업로드에 실패했습니다'
                                          , result=468), 468)
    else:
        return make_response(json.jsonify(result_en='Something Wrong'
                                          , result_ko='일시적인 오류로 실패했습니다'
                                          , result=461), 461)


def cert_local_signup():
    """
    로컬 회원가입 인증
    """
    email = request.values.get('email', None)
    cert_token = request.values.get('cert_token', None)

    if None in [email, cert_token]:
        return make_response(json.jsonify(result='Something Not Entered'), 460)

    is_done = model.cert_local_user(email, cert_token)

    if is_done is True:
        return make_response(json.jsonify(result_en='Certification is complete!'
                                          , result_ko='인증이 완료되었습니다!'
                                          , result=200), 200)
    elif is_done is 2:
        return make_response(json.jsonify(result_en='You entered an incorrect value'
                                          , result_ko='잘못된 이메일 또는 인증코드를 입력했습니다'
                                          , result=401), 401)
    else:
        return make_response(json.jsonify(result_en='Something Wrong'
                                          , result_ko='일시적인 오류로 실패했습니다'
                                          , result=461), 461)


def signout():
    """
    로그아웃
    """
    for key in list(session.keys()):
        session.pop(key)
    logout_user()
    return make_response(json.jsonify(result_en="Successfully sign-out!"
                                      , result_ko='로그아웃 성공!'
                                      , result=200), 200)


def local_signin():
    """
    로컬 로그인
    """
    #: 세션 비우기용
    signout()

    email = request.form.get('email', None)
    password = request.form.get('password', None)

    if None in [email, password]:
        return make_response(json.jsonify(result_en='Something Not Entered'
                                          , result_ko='입력되지 않은 값이 있습니다'
                                          , result=460), 460)

    #: 입력된 email의 사용자 찾기
    user, is_ok = model.select_user(email)

    if is_ok == 0:
        return make_response(json.jsonify(result_en='User does not exist'
                                          , result_ko='존재하지 않는 사용자입니다'
                                          , result=464), 464)
    elif is_ok == 2:
        return make_response(json.jsonify(result_en='Unauthenticated User'
                                          , result_ko='이메일 인증되지 않은 사용자입니다'
                                          , result=263), 263)
    else:
        #: 존재하는 사용자라면 입력된 password가 맞는지 확인
        is_ok = user.can_login(password)

        #: 비밀번호가 일치한다면 login_user에 user 정보를 넣고, 로그인 완료!
        if is_ok is True:
            login_user(user, remember=True)
            session['user_nickname'] = user.nickname
            session['user_picture'] = user.picture

            return make_response(json.jsonify(result_en="Successfully sign-in!"
                                              , result_ko="로그인 성공!"
                                              , result=200), 200)
        else:
            return make_response(json.jsonify(result_en="Password is wrong"
                                              , result_ko='잘못된 비밀번호를 입력했습니다'
                                              , result=465), 465)


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

            return redirect('/static/front/project/projects.html')

        #: 소셜 존재함 + 로그인 상태
        elif current_user.is_authenticated is True:
            #: + 로그인한 사용자와 소셜이 연결된 사용자가 다른 경우 --> 연동 실패 메세지 + 사용자 정보 페이지로 이동
            if user.id != current_user.id:
                # return render_template('user/userinfo.html'
                #                        , result_en="Already connected to another account"
                #                        , result_ko="이미 다른 계정과 연결되었습니다"
                #                        , result=264)
                return redirect(url_for('static', filename='front/user/userinfo.html'
                                        , result_en="Already connected to another account"
                                        , result_ko="이미 다른 계정과 연결되었습니다"
                                        , result=264))

            else:
                return redirect(url_for('static', filename='front/user/userinfo.html'
                                        , result_en="Connection complete!"
                                        , result_ko="소셜 연동 완료!"
                                        , result=262))

    #: 소셜 존재함 + 이메일 인증되지 않음 --> 로그인 페이지로 이동
    if is_ok == 2:
        return redirect(url_for('static', filename='front/user/login.html'
                                , result_en="Unauthenticated User"
                                , result_ko="이메일 인증되지 않은 사용자입니다"
                                , result=263))

    #: 소셜 존재하지 않음
    if not user:
        #: 소셜 존재하지 않음 + 로그인 상태 --> 페이스북 연동 시키기 + 사용자 정보 페이지로 이동
        if current_user.is_authenticated is True:
            email = current_user.id
            is_done = model.update_user_social_info(social_type, email, social_id, social_email, social_name)
            if is_done is True:
                return redirect(url_for('static', filename='front/user/userinfo.html'
                                        , result_en="Connection complete!"
                                        , result_ko="소셜 연동 완료!"
                                        , result=262))

            else:
                return redirect(url_for('static', filename='front/user/userinfo.html'
                                        , result_en='Something Wrong'
                                        , result_ko='일시적인 오류로 실패했습니다'
                                        , result=461))

        #: 소셜 존재하지 않음 + 이메일 존재 --> 로그인 페이지로 이동
        luser, is_ok2 = model.select_user(social_email)
        if luser is not None:
            return redirect(url_for('static', filename='front/user/login.html'
                                    , result_en='You are already signed up'
                                    , result_ko='이미 가입한 사용자입니다. 다른 방법으로 가입하셨나요?'
                                    , result=260))

        #: 소셜 존재하지 않음 + 로그아웃 상태 --> 회원가입 페이지로 이동
        if current_user.is_authenticated is False:
            results = {
                'signup_type': social_type,
                'social_id': social_id,
                'name': social_name,
                'email': social_email,
                'picture': picture
            }
            return redirect(url_for('static', filename='front/user/signup.html', **results))

    print('이건 무슨 경우의 수일까..')
    return redirect('/static/index.html')


#: 페이스북
def facebook_signin():
    return facebook.authorize(callback=url_for('auth.facebook_authorized'
                                               , next=request.args.get('next') or None
                                               , _external=True))


def facebook_authorized():
    try:
        resp = facebook.authorized_response()
    except:
        traceback.print_exc()
        return make_response(json.jsonify(result_en='Facebook currently works abnormally'
                                          , result_ko='페이스북의 일시적인 오류입니다'
                                          , result=466), 466)

    if resp is None:
        return make_response(jsonify(message='Access denied'
                                     , error_reason=request.args['error_reason']
                                     , error_description=request.args['error_description']))
    elif 'access_token' not in resp:
        return make_response(json.jsonify(result_en='No access token from facebook'
                                          , result_ko='페이스북이 Access Token을 보내지 않았습니다'
                                          , result=403), 403)

    #: 페이스북에서 사용자의 데이터 가져오기 - 이메일, 이름, 프로필사진
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
def facebook_tokengetter(token=None):
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
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

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
    state = session['google_state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
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
        return make_response(jsonify(result='Credentials successfully revoked.'))
    else:
        return make_response(jsonify(result='An error occurred.'))


def google_credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


#: 트위터
@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


def twitter_login():
    return twitter.authorize(callback=url_for('_auth.twitter_authorized'
                                              , next=request.args.get('next') or request.referrer or None))


def twitter_authorized():
    # next_url = request.args.get('next') or url_for('index')
    # resp = twitter.authorized_response()
    # if resp is None:
    #     flash(u'You denied the request to sign in.')
    #     return redirect(next_url)
    #
    # session['twitter_token'] = (
    #     resp['oauth_token'],
    #     resp['oauth_token_secret']
    # )
    # session['twitter_user'] = resp['screen_name']

    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in twitter.')
    else:
        session['twitter_oauth'] = resp

    # flash('You were signed in as %s' % resp['screen_name'])
    # return redirect(next_url)
    return jsonify(session=dict(session))


#: 비밀번호 복구메일 보내기
def recovery_password():
    email = request.form.get('email', None)

    #: 버전2에선 자세한 오류로 내보내기
    is_done = model.send_email_for_recovery_pwd(email)
    if is_done is True:
        return make_response(json.jsonify(result='Sent your password to email'), 200)
    else:
        return make_response(json.jsonify(result='Something Wrong'), 461)


#: (테스트용) 세션 확인
def get_session():
    return make_response(jsonify(**session), 200)
