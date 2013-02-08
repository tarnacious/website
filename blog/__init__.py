from flask import Blueprint, render_template, abort, request, g, flash, redirect, url_for
from app.data import db_session, Post, Comment
from sqlalchemy import desc

blog = Blueprint('blog', __name__,
                 template_folder='templates')

from wtforms import Form, TextField, TextAreaField, validators


class CommentForm(Form):
    userid = TextField()
    html = TextField()
    name_validators = [validators.Length(min=1, max=50,
                                         message="Name Required")]

    name = TextField('Name', name_validators, default='')
    url = TextField('Link', [validators.Length(max=200)], default='')
    validator = [validators.Length(min=1, max=5000,
                                   message="Comment Required")]
    comment = TextAreaField('Comment', validator)


@blog.route('/journal')
def index():
    posts = db_session.query(Post).order_by(desc(Post.date))
    return render_template('blog/index.html', posts=posts)


@blog.route('/journal/<slug>', methods=['GET'])
def post_view(slug):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        abort(404)
    comments = Comment.query.filter_by(post_id=post.id)
    return render_template('blog/post.html',
                           post=post,
                           comments=comments,
                           form=CommentForm())


@blog.route('/journal/<slug>', methods=['POST'])
def post_comment(slug):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        abort(404)
    comments = Comment.query.filter_by(post_id=post.id)
    comment_form = CommentForm(request.form)
    if comment_form.validate():
        comment = Comment()
        comment.user_id = g.user.id
        comment.post_id = post.id
        comment.text = comment_form.comment.data
        comment.text = comment_form.comment.data
        comment.website = comment_form.url.data
        comment.name = comment_form.name.data
        db_session.add(comment)
        db_session.commit()
        flash('Comment Saved')
        return redirect(url_for('blog.post_view', slug=post.slug))

    return render_template('blog/post.html',
                           post=post,
                           comments=comments,
                           form=comment_form)
