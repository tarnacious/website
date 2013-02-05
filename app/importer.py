import ConfigParser
import os
import markdown
from dateutil import parser
from markup import syntax_highlight
import re


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

    return {'title': title,
            'date': date,
            'slug': slugify(name),
            'text': text,
            'html': html,
            'head': head,
            'footer': footer,
            }


def read_posts():
    folders = [folder for folder in os.listdir("posts")
               if not folder.startswith(".")]
    all_posts = [read_post(folder) for folder in folders]
    posts = [post for post in all_posts if post is not None]
    return posts
