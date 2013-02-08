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

from author import auth
import author
from blog import blog

app.register_blueprint(auth)
app.register_blueprint(blog)


@app.before_request
def before_request():
    author.before_request()


@auth.after_request
def after_request(response):
    return author.after_request()


@app.route('/')
def index():
    return render_template('index.html')
