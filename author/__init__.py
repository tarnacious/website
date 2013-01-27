from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
import os

app = Flask(__name__)
app.config.from_object('author.settings')

if 'AUTHOR_SETTINGS' in os.environ:
    app.config.from_envvar('AUTHOR_SETTINGS')
else:
    print "Warning: No settings file set"

app.wsgi_app = ProxyFix(app.wsgi_app)

from handlers import *
from openid import *
from twitter import *
from google import *
