from flask import request, redirect, url_for, flash, g, make_response, abort
from authentication import authentication
from app.data import User, db_session
from app import app
from app import sessions
from authentication import parse_next_url
import json
import requests

@authentication.route('/persona', methods=['POST'])
def login_persona():
    if 'assert' not in request.form:
        abort(400)

    data = {'assertion': request.form['assert'], 'audience': app.config['PERSONA_URL']}
    resp = requests.post('https://verifier.login.persona.org/verify', data=data, verify=True)

    if resp.ok:
        verification_data = json.loads(resp.content)

        if verification_data['status'] == 'okay':
            email = verification_data['email']

            user = User.query.filter_by(identity=email,
                                        provider='persona').first()

            if user is None:
                user = User()
                user.name = email
                user.identity = email
                user.provider = "persona"
                db_session.add(user)

            db_session.commit()

            session_id = sessions.start(user)
            next_url = parse_next_url(request.args.get('next')) or url_for('index')
            resp = make_response('You were signed in')
            resp.set_cookie('session_id', session_id)
            flash('You were signed in')
            return resp

    abort(500)
