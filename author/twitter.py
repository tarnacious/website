from flask import request, redirect, url_for, flash, g, make_response
from flask_oauth import OAuth
from author import auth
from app.data import User, db_session
from app import app
from app import sessions
from author import parse_next_url

oauth = OAuth()

twitter = oauth.remote_app(
    'twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key=app.config['TWITTER_CONSUMER_KEY'],
    consumer_secret=app.config['TWITTER_CONSUMER_SECRET']
)


@twitter.tokengetter
def get_twitter_token():
    """This is used by the API to look for the auth token and secret
    it should use for API calls.  During the authorization handshake
    a temporary set of token and secret is used, but afterwards this
    function has to return the token and secret.  If you don't want
    to store this in the database, consider putting it into the
    session instead.
    """
    user = g.user
    if user is not None:
        return user.oauth_token, user.oauth_secret


@auth.route('/twitter')
def login_twitter():
    """Calling into authorize will cause the OpenID auth machinery to kick
    in.  When all worked out as expected, the remote application will
    redirect back to the callback URL provided.
    """
    next_url = request.args.get('next') or request.referrer
    callback_url = url_for('author.oauth_authorized', next=next_url)
    return twitter.authorize(callback=callback_url)


@auth.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    """Called after authorization.  After this function finished handling,
    the OAuth information is removed from the session again.  When this
    happened, the tokengetter from above is used to retrieve the oauth
    token and secret.

    Because the remote application could have re-authorized the application
    it is necessary to update the values in the database.

    If the application redirected back after denying, the response passed
    to the function will be `None`.  Otherwise a dictionary with the values
    the application submitted.  Note that Twitter itself does not really
    redirect back unless the user clicks on the application name.
    """

    next_url = parse_next_url(request.args.get('next')) or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    user = User.query.filter_by(identity=resp['user_id'],
                                provider='twitter').first()

    # user never signed on
    if user is None:
        user = User()
        user.name = resp['screen_name']
        user.identity = resp['user_id']
        user.provider = "twitter"
        db_session.add(user)

    db_session.commit()

    session_id = sessions.start(user)
    resp = make_response(redirect(next_url))
    resp.set_cookie('session_id', session_id)
    flash('You were signed in')
    return resp
