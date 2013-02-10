from flask import Flask, render_template
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)

app.config.from_object('app.settings')
app.config.from_envvar('AUTHOR_SETTINGS', silent=True)

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    from logging import Formatter
    import os
    logfile = app.config['LOG_FILE']
    directory = os.path.dirname(logfile)
    if not os.path.exists(directory):
        os.makedirs(directory)
    handler = RotatingFileHandler(logfile)
    handler.setLevel(logging.INFO)
    handler.setFormatter(Formatter(app.config['LOG_FORMAT']))
    app.logger.addHandler(handler)

app.wsgi_app = ProxyFix(app.wsgi_app)

import authentication
import blog

app.register_blueprint(authentication.authentication, url_prefix="/authentication")
app.register_blueprint(blog.blog)

@app.before_request
def before_request():
    authentication.before_request()


@app.after_request
def after_request(response):
    return authentication.after_request(response)


@app.route('/')
def index():
    return render_template('index.html')
