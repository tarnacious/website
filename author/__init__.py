from flask import Blueprint, current_app

auth = Blueprint('author', __name__,
                 template_folder='templates')

from handlers import *
from openid import *
from twitter import *
from google import *
