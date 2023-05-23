import os
import re
import shutil
import sys
from configparser import ConfigParser
from dateutil import parser
from datetime import timezone
from text2html import text2html
from jinja2 import Environment, FileSystemLoader
from feedgen.feed import FeedGenerator

src_path = os.path.dirname(__file__)
template_path = os.path.join(src_path, "templates")
output_path = "./build"
templating = Environment(loader=FileSystemLoader(template_path))
content_path = "./posts"

def slugify(name):
    pattern = r"\d{4}-\d{2}-\d{2}-(.*)"
    match = re.search(pattern, name)
    if match:
        return match.group(1)

def copy_assets(source_dir, destination_dir):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        destination_item = os.path.join(destination_dir, item)
        if os.path.isfile(source_item):
            filename = os.path.basename(source_item)
            if filename in ["index.txt", "info", "head.html", "foot.html"]:
                continue
            shutil.copy2(source_item, destination_item)
        elif os.path.isdir(source_item):
            shutil.copytree(source_item, destination_item)

def read_post(directory):
    slug = slugify(directory.split('/')[-1])
    if not slug:
        sys.stderr.write("Unable to parse slug: " + directory + "\n")
        return None

    if not os.path.exists("%s/info" % (directory)):
        sys.stderr.write("No info file found: " + directory + "\n")
        return None

    config = ConfigParser()
    config.read("%s/info" % (directory))
    title = config.get("Post", "title")
    date = parser.parse(config.get("Post", "date"))
    date = date.replace(tzinfo=timezone.utc)
    text = open("%s/index.txt" % (directory), "r", encoding="utf-8").read()
    if os.path.exists("%s/head.html" % (directory)):
        head = open("%s/head.html" % (directory)).read()
    else:
        head = ""
    if os.path.exists("%s/foot.html" % (directory,)):
        footer = open("%s/foot.html" % (directory)).read()
    else:
        footer = ""

    html = text2html(text)

    post = {
            "title": title,
            "date": date,
            "slug": slug,
            "text": text,
            "html": html,
            "head": head,
            "footer": footer,
            "directory": directory
    }
    return post

def read_posts(path):
    directories = [directory for directory in os.listdir(path)
                   if not directory.startswith(".")]
    all_posts = [read_post(os.path.join(path, directory))
                 for directory in directories]
    posts = [post for post in all_posts if post is not None]
    return sorted(posts, key=lambda post: post["date"], reverse=True)

def generate_feeds(posts):
    fg = FeedGenerator()
    fg.id("https://tarnbarford.net/journal")
    fg.title("The Journals of Tarn Barford")
    fg.description("Infrequent blog posts")
    fg.author( {"name":"tarn","email":"tarn@tarnbarford.net"} )
    fg.link( href="https://tarnbarford.net", rel="alternate" )
    fg.link( href="https://tarnbarford.net/atom", rel="self" )
    fg.language("en")

    for post in posts[::-1]:
        fe = fg.add_entry()
        post_url = "https://tarnbarford.net/journal/" + post["slug"]
        fe.id(post_url)
        fe.title(post["title"])
        fe.link(href=post_url, rel="self")
        fe.author(name="tarn", email="tarn@tarnbarford.net")
        fe.published(post["date"])
        fe.content(render_post(post))

    fg.atom_file(os.path.join(output_path, "atom.xml"))
    fg.rss_file(os.path.join(output_path, "rss.xml"))

def render_post(post):
    template = templating.get_template("journal/post.html")
    return template.render(post=post)

def render_index():
    template = templating.get_template("index.html")
    return template.render()

def render_journal_index(posts):
    template = templating.get_template("journal/index.html")
    return template.render(posts=posts)



if __name__ == "__main__":
    posts = read_posts(content_path)
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)
    os.makedirs(os.path.join(output_path, "journal"))
    shutil.copytree(
        os.path.join(src_path, "static"),
        os.path.join(output_path, "static"))

    # content directories to /static/journal
    os.makedirs(os.path.join(output_path, "static/journal"))
    directories = [directory for directory in os.listdir(content_path)
                   if not directory.startswith(".")]
    for directory in directories:
        shutil.copytree(
            os.path.join(content_path, directory),
            os.path.join(output_path, "static/journal", directory))


    with open(os.path.join(output_path, "index.html"), 'w') as out:
        out.write(render_index())

    with open(os.path.join(output_path, "journal/index.html"), 'w') as out:
        out.write(render_journal_index(posts))

    for post in posts:
        content = render_post(post)
        post_path = os.path.join(output_path, "journal", post["slug"])
        os.makedirs(post_path)
        copy_assets(post["directory"], post_path)
        with open(os.path.join(post_path, "index.html"), 'w') as out:
            out.write(content)

    generate_feeds(posts)
