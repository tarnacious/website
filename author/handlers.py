from flask import g, render_template, redirect, url_for, request, flash
from app.data import db_session, User
import sessions
from author import auth


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


@auth.route('/auth/logout')
def logout():
    flash('You have been signed out')
    session_id = request.cookies.get('session_id')
    if session_id:
        sessions.remove(session_id)
    return redirect(request.referrer or url_for('index'))


@auth.route('/auth/')
def index():
    return render_template('author/index.html')


@auth.route('/auth/profile', methods=['GET', 'POST'])
def edit_profile():
    if g.user is None:
        return redirect(url_for('index'))
    form = dict(name=g.user.name, email=g.user.email)
    if request.method == 'POST':
        if 'delete' in request.form:
            db_session.delete(g.user)
            db_session.commit()
            #TODO: Delete session
            flash(u'Profile deleted')
            return redirect(url_for('index'))
            flash(u'Profile saved')
            g.user.name = request.form['name']
            g.user.email = request.form['email']
            db_session.commit()
            return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', form=form)
