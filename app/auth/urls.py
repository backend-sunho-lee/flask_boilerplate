from flask import Blueprint
import app.auth.controllers as ctrl

auth = Blueprint('auth', __name__, template_folder='static/front/user')

# 로컬 회원가입
auth.add_url_rule('/signup/<signup_type>', view_func=ctrl.signup, methods=['POST'])

# 로컬 회원가입 인증
auth.add_url_rule('/local/cert', view_func=ctrl.cert_local_signup, methods=['POST'])

# 로컬 로그인
auth.add_url_rule('/local/signin', view_func=ctrl.local_signin, methods=['POST'])
auth.add_url_rule('/social/callback', view_func=ctrl.social_callback, methods=['GET', 'POST'])


# 페이스북
auth.add_url_rule('/facebook/signin', view_func=ctrl.facebook_signin, methods=['GET'])
auth.add_url_rule('/facebook/authorized', view_func=ctrl.facebook_authorized, methods=['GET', 'POST'])
auth.add_url_rule('/facebook/tokengetter', view_func=ctrl.facebook_tokengetter, methods=['GET'])


# 구글
auth.add_url_rule('/google/signin', view_func=ctrl.google_signin, methods=['GET'])
auth.add_url_rule('/google/authorized', view_func=ctrl.google_authorized, methods=['GET'])
auth.add_url_rule('/google/oauth2callback', view_func=ctrl.google_oauth2callback, methods=['GET'])
auth.add_url_rule('/google/revoke', view_func=ctrl.google_revoke, methods=['GET'])

# 트위터
auth.add_url_rule('/twitter/login', view_func=ctrl.twitter_login, methods=['GET'])
auth.add_url_rule('/twitter/oauth-authorized', view_func=ctrl.twitter_authorized, methods=['GET'])
auth.add_url_rule('/twitter/logout', view_func=ctrl.twitter_logout, methods=['GET'])


# 로그아웃
auth.add_url_rule('/signout', view_func=ctrl.signout, methods=['GET'])

# 비밀번호 찾기
auth.add_url_rule('/recoverPwd', view_func=ctrl.recovery_password, methods=['POST'])

auth.add_url_rule('/check', view_func=ctrl.get_session, methods=['GET'])
