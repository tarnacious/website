from flask import redirect, url_for, make_response, flash, request
from flask_oauth import OAuth
from app import app
from author import auth
from app.data import User, db_session
from author import sessions
from author import parse_next_url
import json
oauth = OAuth()

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=app.config['GOOGLE_CLIENT_ID'],
                          consumer_secret=app.config['GOOGLE_CLIENT_SECRET'])


@auth.route('/auth/google')
def login_google():
    callback = url_for('author.authorized', _external=True)
    return google.authorize(callback=callback)


@auth.route(app.config['GOOGLE_REDIRECT_URI'])
@google.authorized_handler
def authorized(resp):

    access_token = resp['access_token']

    info = request_userinfo(access_token)
    user = User.query.filter_by(identity=info['email'],
                                provider='google').first()

    if user is None:
        user = User()
        user.name = info['email'].split('@')[0]
        user.email = info['email']
        user.provider = 'google'
        user.identitiy = info['email']
        db_session.add(user)
        db_session.commit()


    session_id = sessions.start(user)
    next_url = parse_next_url(request.args.get('next')) or url_for('index')
    resp = make_response(redirect(next_url))
    resp.set_cookie('session_id', session_id)
    flash('You were signed in')
    return resp


def request_userinfo(access_token):
    from urllib2 import Request, urlopen, URLError
    headers = {'Authorization': 'OAuth ' + access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError:
        raise
    return json.loads(res.read())


@google.tokengetter
def get_access_token():
    pass
