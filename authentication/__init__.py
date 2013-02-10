from flask import Blueprint, render_template
from urlparse import urlparse, parse_qs
from wtforms import Form, TextField
from datetime import datetime, timedelta


authentication = Blueprint('authentication', __name__,
                           template_folder='templates')


def parse_next_url(url):
    if not url:
        return
    qs = urlparse(url).query
    query = parse_qs(qs)
    if 'next' in query:
        return query['next'][0]


class ProfileForm(Form):
    name = TextField('Name', default='')
    url = TextField('Link', default='')
    email = TextField('Email', default='')


def before_request():
    g.user = None
    session_id = request.cookies.get('session_id')
    if session_id:
        session = sessions.find(session_id)
        if session:
            g.user = User.query.get(session['user_id'])


def after_request(response):
    db_session.remove()
    return response


@authentication.route('/logout', methods=['POST'])
def logout():
    flash('You have been signed out')
    session_id = request.cookies.get('session_id')
    if session_id:
        sessions.remove(session_id)
    resp = make_response(redirect(request.referrer or url_for('index')))
    resp.set_cookie('session_id', '', expires=datetime.now() - timedelta(days=1))
    return resp


@authentication.route('/', methods=['GET'])
def index():
    form = ProfileForm()
    if g.user:
        form.name.data = g.user.name
        form.url.data = g.user.website
        form.email.data = g.user.email
    next_url = request.args.get('next') or url_for('index')
    return render_template('authentication/index.html', form=form, next_url=next_url)


@authentication.route('/', methods=['POST'])
def account():
    if g.user is None:
        return redirect(url_for('authentication.index'))
    if 'delete' in request.form:
        session_id = request.cookies.get('session_id')
        sessions.remove(session_id)
        db_session.delete(g.user)
        db_session.commit()
        flash(u'Profile permanently deleted')
        return redirect(url_for('authentication.index'))
    g.user.name = request.form['name']
    g.user.email = request.form['email']
    g.user.website = request.form['url']
    db_session.commit()
    flash(u'Profile updated')
    return redirect(url_for('authentication.index'))


from openid import *
from twitter import *
from google import *
