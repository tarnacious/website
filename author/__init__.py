from flask import Flask
import os

app = Flask(__name__)
app.config.from_object('author.settings')

if 'AUTHOR_SETTINGS' in os.environ:
    app.config.from_envvar('AUTHOR_SETTINGS')
else:
    print "Warning: No settings file set"

from handlers import *
from openid import *
from twitter import *
from google import *
