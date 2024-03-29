import markdown
from bs4 import BeautifulSoup
import pygments
from pygments.lexers import get_lexer_by_name
import pygments.lexers
from pygments.formatters import HtmlFormatter
from pygments.lexers import load_lexer_from_file
import re
from html import unescape
import markdown

def text2html(text):
    html = markdown.markdown(text)
    html = syntax_highlight(html)
    return html

def markup_comment(text):
    html = markdown.markdown(text)
    html = syntax_highlight(html)
    html = sanitize(html)
    return html


def sanitize(html):
    from lxml.html.clean import Cleaner
    cleaner = Cleaner(remove_tags=['img'])
    return cleaner.clean_html(html)

def handle_shebang(text):
    shebang_re = r'^\W*(#!\/[^\ \n]+)'
    shebang = re.search(shebang_re, text)
    if shebang:
        text = re.sub(shebang_re, '', text)
        name = shebang.group(1).split("/")[-1]
        return (name, text)
    return (None, text)

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
            name, text = handle_shebang(text)
            if name:
                class_name = "highlight-console" if name == "console" else "highlight"
                class_name = "highlight-block " + class_name

                formatter = HtmlFormatter(wrapcode=True, cssclass=class_name)
                if name == "bash":
                    lexer = get_lexer_by_name("text")
                elif name == "nix":
                    lexer = load_lexer_from_file("src/nixlexer.py", "NixLexer")
                else:
                    lexer = get_lexer_by_name(name)
                    if not lexer:
                        lexer = get_lexer_by_name("text")

                html = pygments.highlight(text, lexer, formatter)
                code_soup = BeautifulSoup(html, features="html.parser")
                element.parent.replaceWith(code_soup)
    return str(soup)

if __name__ == "__main__":
    text = """
An observable that yields for every capture click after the start button and
before the stop button has been clicked.

    // Comment
    compose.Subscribe(function (result) {
        var val = $("<li/>").html(result);
        val.appendTo($("#results"));
    });

Bye.
    """
    html = markdown.markdown(text)
    html = syntax_highlight(html)
    print(html)
