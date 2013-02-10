from flask import g, render_template, redirect, url_for, request, flash, make_response
from app.data import db_session, User
from app import sessions
from author import auth
from wtforms import Form, TextField
from datetime import datetime, timedelta


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


@auth.route('/logout', methods=['POST'])
def logout():
    flash('You have been signed out')
    session_id = request.cookies.get('session_id')
    if session_id:
        sessions.remove(session_id)
    resp = make_response(redirect(request.referrer or url_for('index')))
    resp.set_cookie('session_id', '', expires=datetime.now() - timedelta(days=1))
    return resp


@auth.route('/', methods=['GET'])
def index():
    form = ProfileForm()
    if g.user:
        form.name.data = g.user.name
        form.url.data = g.user.website
        form.email.data = g.user.email
    next_url = request.args.get('next') or url_for('index')
    return render_template('author/index.html', form=form, next_url=next_url)


@auth.route('/', methods=['POST'])
def account():
    if g.user is None:
        return redirect(url_for('author.index'))
    if 'delete' in request.form:
        session_id = request.cookies.get('session_id')
        sessions.remove(session_id)
        db_session.delete(g.user)
        db_session.commit()
        flash(u'Profile permanently deleted')
        return redirect(url_for('author.index'))
    g.user.name = request.form['name']
    g.user.email = request.form['email']
    g.user.website = request.form['url']
    db_session.commit()
    flash(u'Profile updated')
    return redirect(url_for('author.index'))
