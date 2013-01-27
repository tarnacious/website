from flask import redirect, url_for, session, request
from flask_oauth import OAuth
from author import app
from author.data import User, db_session
from author.data import session_create, session_get
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


@app.route('/auth/google')
def login_google():
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)


@app.route(app.config['GOOGLE_REDIRECT_URI'])
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    google_id = resp['id_token']

    info = request_userinfo(access_token)
    user = User.query.filter_by(google_id=info['email']).first()

    if user is None:
        user = User(info['email'])
        user.email = info['email']
        user.google_id = info['email']
        db_session.add(user)
        db_session.commit()
    else:
        db_session.commit()

    session_id = session_create(user)
    session['session_id'] = session_id
    return redirect(url_for('index'))


def request_userinfo(access_token):
    from urllib2 import Request, urlopen, URLError
    headers = {'Authorization': 'OAuth ' + access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        raise
    return json.loads(res.read())

@google.tokengetter
def get_access_token():
    return session.get('access_token')
