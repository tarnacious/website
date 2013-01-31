from flask import Blueprint, current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

auth = Blueprint('auth', __name__,
                template_folder='templates')


from handlers import *
from openid import *
from twitter import *
from google import *
