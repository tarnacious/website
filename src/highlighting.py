import markdown
from bs4 import BeautifulSoup
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import re
from html.parser import HTMLParser
from html import unescape, escape


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
    soup = BeautifulSoup(html, features="lxml")
    elements = soup.findAll('pre')
    for pretag in elements:
        element = pretag.find('code')
        if element:
            text = unescape(str(element.contents[0]))
            shebang_re = r'^\W*(#!\/[^\ \n]+)'
            shebang = re.search(shebang_re, text)
            text = escape(text)
            if shebang:
                text = re.sub(shebang_re, '', text)
                name = shebang.group(1).split("/")[-1]
                if name == "bash":
                    html = '<div class="highlight"><pre>%s</pre></div>' % (text)
                    code_soup = BeautifulSoup(html, features="html.parser")
                    element.parent.replaceWith(code_soup)
                else:
                    lexer = get_lexer_by_name(name)
                    if lexer:
                        html = pygments.highlight(text, lexer, HtmlFormatter())
                        code_soup = BeautifulSoup(html, features="html.parser")
                        element.parent.replaceWith(code_soup)
    return str(soup)
