from flask import Blueprint, current_app
from urlparse import urlparse, parse_qs


auth = Blueprint('author', __name__,
                 template_folder='templates')


def parse_next_url(url):
    if not url:
        return
    qs = urlparse(url).query
    query = parse_qs(qs)
    if 'next' in query:
        return query['next'][0]


from handlers import *
from openid import *
from twitter import *
from google import *
