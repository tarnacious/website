from flask import render_template, request, g, flash, redirect, make_response
from flask_openid import OpenID
from author.data import User, db_session
from author import app, sessions
import urlparse

oid = OpenID(app)


@app.route('/auth/openid', methods=['GET', 'POST'])
@oid.loginhandler
def openid():
    if g.user is not None:
        path = urlparse.urlparse(oid.get_next_url()).path
        if path != request.path:
            return redirect(oid.get_next_url())

    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            return oid.try_login(openid, ask_for=['email', 'fullname',
                                                  'nickname'])
    return render_template('openid.html', next=oid.get_next_url(),
                           error=oid.fetch_error())


@oid.after_login
def create_or_login(resp):
    user = User.query.filter_by(identity=resp.identity_url,
                                provider='openid').first()
    if user is None:
        user = User()
        user.name = resp.fullname or resp.nickname or ''
        user.email = resp.email or ''
        user.provider = 'openid'
        user.identity = resp.identity_url
        db_session.add(user)
        db_session.commit()

    session_id = sessions.start(user)
    resp = make_response(redirect(oid.get_next_url()))
    resp.set_cookie('session_id', session_id)
    flash('You were signed in')
    return resp
