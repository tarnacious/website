import ConfigParser
import os
import markdown
from dateutil import parser
from markup import syntax_highlight
import re
from app.data import Post, Comment


def slugify(name):
    name = re.sub(r'\W+', '', name)
    name = name.replace("_", "-")
    if name[0] == "-":
        name = name[:-1]
    return name


def read_post(name):
    if not os.path.exists("posts/%s/info" % (name)):
        print "No info file found"
        return None
    config = ConfigParser.ConfigParser()
    config.read("posts/%s/info" % (name))
    title = config.get("Post", "title")
    date = parser.parse(config.get("Post", "date"))
    text = open("posts/%s/index.txt" % (name)).read()
    if os.path.exists("posts/%s/head.html" % (name)):
        head = open("posts/%s/head.html" % (name)).read()
    else:
        head = ""
    if os.path.exists("posts/%s/foot.html" % (name,)):
        footer = open("posts/%s/foot.html" % (name)).read()
    else:
        footer = ""

    html = markdown.markdown(text)
    html = syntax_highlight(html)

    post = Post(title=title,
                date=date,
                slug=slugify(name),
                text=text,
                html=html,
                head=head,
                footer=footer)
    return post


def import_comments(filename):
    import json
    from app.markup import markup_comment
    from app.data import db_session
    comments = json.loads(open(filename).read())
    for comment in comments:
        print comment['slug']
        post = Post.query.filter_by(slug=comment['slug']).first()
        model = Comment()
        #model.user_id =
        model.post_id = post.id
        model.text = comment['content']
        model.html = markup_comment(comment['content'])
        model.website = comment['url']
        model.name = comment['name']
        date = parser.parse(comment['created'])
        model.timestamp = date
        db_session.add(model)
        db_session.commit()


def read_posts():
    folders = [folder for folder in os.listdir("posts")
               if not folder.startswith(".")]
    all_posts = [read_post(folder) for folder in folders]
    posts = [post for post in all_posts if post is not None]
    return posts


def import_posts():
    from app.data import db_session
    posts = read_posts()
    for post in posts:
        print post.slug
        if post:
            find_post = Post.query.filter_by(slug=post.slug).first()

            if find_post is None:
                db_session.add(post)
            else:
                find_post.title = post.title
                find_post.date = post.date
                find_post.text = post.text
                find_post.html = post.html
                find_post.head = post.head
                find_post.footer = post.footer
                db_session.add(find_post)

            db_session.commit()
