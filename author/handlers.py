from author import app
from flask import g, render_template, session, redirect, url_for, request, flash, abort
from author.data import db_session, User


@app.before_request
def before_request():
    g.user = None
    if 'session_id' in session:
        from author.data import session_get
        s = session_get(session['session_id'])
        if s:
            g.user = User.query.get(s.user_id)


@app.after_request
def after_request(response):
    db_session.remove()
    return response


@app.route('/auth/logout')
def logout():
    session.pop('session_id', None)
    flash('You have been signed out')
    return redirect(request.referrer or url_for('index'))


@app.route('/auth/')
def index():
    return render_template('index.html')


@app.route('/auth/profile', methods=['GET', 'POST'])
def edit_profile():
    """Updates a profile"""
    if g.user is None:
        return redirect(url_for('index'))
    form = dict(name=g.user.name, email=g.user.email)
    if request.method == 'POST':
        if 'delete' in request.form:
            db_session.delete(g.user)
            db_session.commit()
            session['openid'] = None
            flash(u'Profile deleted')
            return redirect(url_for('index'))
        form['name'] = request.form['name']
        form['email'] = request.form['email']
        if not form['name']:
            flash(u'Error: you have to provide a name')
        elif '@' not in form['email']:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            g.user.name = form['name']
            g.user.email = form['email']
            db_session.commit()
            return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', form=form)
