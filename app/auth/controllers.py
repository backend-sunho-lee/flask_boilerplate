from flask import url_for, request, g, session, flash, render_template, redirect, jsonify, make_response, json
from flask_oauthlib.client import OAuth
from app import app

oauth = OAuth()

def index():
    return 'Auth API'

twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=app.config['TWITTER_CONSUMER_KEY'],
    consumer_secret=app.config['TWITTER_CONSUMER_SECRET']
)

@twitter.tokengetter
# def get_twitter_token(token=None):
#     return session.get('twitter_token')
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']

def twitter_login():
    return twitter.authorize(callback=url_for('auth.twitter_authorized',
        next=request.args.get('next') or request.referrer or None))
    # return twitter.authorize(callback=url_for('auth.twitter_authorized', _external=True))

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

def twitter_logout():
    session.pop('twitter_oauth', None)
    # session.pop('twitter_token', None)
    # session.pop('twitter_user', None)
    # return redirect(url_for('auth.index'))
    return jsonify(session=dict(session))


def login():
    pass