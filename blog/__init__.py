from flask import Blueprint, render_template, abort
from app.data import db_session, Post
from sqlalchemy import desc

blog = Blueprint('blog', __name__,
                 template_folder='templates')


@blog.route('/journal')
def index():
    posts = db_session.query(Post).order_by(desc(Post.date))
    return render_template('blog/index.html', posts=posts)

@blog.route('/journal/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        abort(404)
    return render_template('blog/post.html', post=post)
