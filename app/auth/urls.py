from flask import Blueprint
import app.auth.controllers as ctrl

auth = Blueprint('auth', __name__, template_folder='static/front/user')

#: Local
auth.add_url_rule('/signup/<signup_type>', view_func=ctrl.signup, methods=['POST'])  # sign-up
auth.add_url_rule('/local/cert', view_func=ctrl.cert_local_signup, methods=['POST']) # sign-up certification
auth.add_url_rule('/local/signin', view_func=ctrl.local_signin, methods=['POST'])  # sign-in

#: OAuth common
auth.add_url_rule('/social/callback', view_func=ctrl.social_callback, methods=['GET', 'POST'])

#: Facebook
auth.add_url_rule('/facebook/signin', view_func=ctrl.facebook_signin, methods=['GET'])  # sign-in
auth.add_url_rule('/facebook/authorized', view_func=ctrl.facebook_authorized, methods=['GET', 'POST'])
auth.add_url_rule('/facebook/tokengetter', view_func=ctrl.facebook_tokengetter, methods=['GET'])

#: Google
auth.add_url_rule('/google/signin', view_func=ctrl.google_signin, methods=['GET'])  # sign-in
auth.add_url_rule('/google/authorized', view_func=ctrl.google_authorized, methods=['GET'])
auth.add_url_rule('/google/oauth2callback', view_func=ctrl.google_oauth2callback, methods=['GET'])
auth.add_url_rule('/google/revoke', view_func=ctrl.google_revoke, methods=['GET'])


auth.add_url_rule('/signout', view_func=ctrl.signout, methods=['GET'])  # sign-out
auth.add_url_rule('/recoverPwd', view_func=ctrl.recovery_password, methods=['POST'])  # password recovery
auth.add_url_rule('/check', view_func=ctrl.get_session, methods=['GET'])  # session check
