import markdown
from BeautifulSoup import BeautifulSoup
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import re
import HTMLParser


def markup_comment(text):
    html = markdown.markdown(text)
    html = syntax_highlight(html)
    html = sanitize(html)
    return html


def sanitize(html):
    from lxml.html.clean import Cleaner
    cleaner = Cleaner(remove_tags=['img'])
    return cleaner.clean_html(html)


def syntax_highlight(html):
    """
    Replace Markdown style code blocks in html.

        <pre>
            <code>
                #!/usr/bin/python
                print "Hello"
            </code>
        </pre>

    With Pygments markup using the lexer based on the name in the shebang.
    It also removes the shebang.

    """
    soup = BeautifulSoup(html)
    elements = soup.findAll('pre')
    for pretag in elements:
        element = pretag.find('code')
        text = str(element.getString())
        text = HTMLParser.HTMLParser().unescape(text)
        shebang_re = r'^\W*(#!\/[^\ \n]+)'
        shebang = re.search(shebang_re, text)
        if shebang:
            text = re.sub(shebang_re, '', text)
            name = shebang.group(1).split("/")[-1]
            if name == "bash":
                html = '<div class="highlight"><pre>%s</pre></div>' % (text)
                code_soup = BeautifulSoup(html)
                element.parent.replaceWith(code_soup)
            else:
                lexer = get_lexer_by_name(name)
                if lexer:
                    html = pygments.highlight(text, lexer, HtmlFormatter())
                    code_soup = BeautifulSoup(html)
                    element.parent.replaceWith(code_soup)
    return str(soup)
