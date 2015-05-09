from flask import Blueprint, render_template, abort, request, g, flash, redirect, url_for
from app.data import db_session, Post, Comment
from datetime import datetime
from sqlalchemy import desc
from app.markup import markup_comment
from werkzeug.contrib.atom import AtomFeed
from urlparse import urljoin

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

def clean_post(html):
    import lxml
    from lxml.html.clean import Cleaner
    from StringIO import StringIO
    
    cleaner = Cleaner()
    cleaner.javascript = True
    cleaner.style = True
    cleaner.remove_tags = ['body']
    return lxml.html.tostring(cleaner.clean_html(lxml.html.parse(StringIO(html)))) 

@blog.route('/atom')
def atom():
    feed = AtomFeed('The Journals of Tarn Barford',
                    feed_url=request.url, url=request.url_root)
    posts = db_session.query(Post).order_by(desc(Post.date)) \
                      .limit(15).all()
    for post in posts:
        feed.add(post.title, unicode(clean_post(post.html)),
                 content_type='html',
                 author="tarn",
                 url=urljoin(request.url_root,
                             "journal/" + post.slug),
                 updated=post.date,
                 published=post.date)
    return feed.get_response()


@blog.route('/journal/<slug>', methods=['GET'])
def post_view(slug):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        abort(404)
    comments = Comment.query.filter_by(post_id=post.id)
    comment_form = CommentForm()
    edit_comment = None
    if 'comment_id' in request.args:
        edit_comment = Comment.query.filter_by(id=request.args['comment_id']).first()
        if not edit_comment:
            flash("Comment not found")
            return redirect(url_for('blog.post_view', slug=post.slug))
        if not g.user:
            flash("You must be logged in")
            return redirect(url_for('blog.post_view', slug=post.slug))
        if not edit_comment.user_id == g.user.id:
            flash("Not allowed to edit this comment")
            return redirect(url_for('blog.post_view', slug=post.slug))
        comment_form.name.data = edit_comment.name
        comment_form.url.data = edit_comment.website
        comment_form.comment.data = edit_comment.text
    return render_template('blog/post.html',
                           post=post,
                           edit_comment=edit_comment,
                           comments=comments,
                           form=comment_form)


@blog.route('/journal/<slug>', methods=['POST'])
def post_comment(slug):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        abort(404)
    comment_form = CommentForm(request.form)

    edit_comment = None
    if comment_form.validate():
        if 'comment_id' in request.args:
            edit_comment = Comment.query.filter_by(id=request.args['comment_id']).first()

        if edit_comment:
            if not edit_comment.user_id == g.user.id:
                flash("You must be logged in")
                return redirect(url_for('blog.post_view', slug=post.slug))

            if request.form.get('action') == "Delete":
                db_session.delete(edit_comment)
                db_session.commit()
                flash('Comment Deleted')
                return redirect(url_for('blog.post_view', slug=post.slug))

            edit_comment.text = comment_form.comment.data
            edit_comment.html = markup_comment(comment_form.comment.data)
            edit_comment.website = comment_form.url.data
            edit_comment.name = comment_form.name.data
            db_session.commit()
            flash('Comment Updated')
            return redirect(url_for('blog.post_view', slug=post.slug))

        comment = Comment()
        comment.user_id = g.user.id
        comment.post_id = post.id
        comment.text = comment_form.comment.data
        comment.html = markup_comment(comment_form.comment.data)
        comment.website = comment_form.url.data
        comment.name = comment_form.name.data
        comment.timestamp = datetime.now()
        db_session.add(comment)
        db_session.commit()
        flash('Comment Posted')
        return redirect(url_for('blog.post_view', slug=post.slug))
    else:
        flash('Comment incomplete');

    comments = Comment.query.filter_by(post_id=post.id)
    return render_template('blog/post.html',
                           post=post,
                           comments=comments,
                           form=comment_form)
