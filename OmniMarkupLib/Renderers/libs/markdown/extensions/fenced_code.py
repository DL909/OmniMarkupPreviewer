"""
Fenced Code Extension for Python Markdown
=========================================

This extension adds Fenced Code Blocks to Python-Markdown.

    >>> import markdown
    >>> text = '''
    ... A paragraph before a fenced code block:
    ...
    ... ~~~
    ... Fenced code block
    ... ~~~
    ... '''
    >>> html = markdown.markdown(text, extensions=['fenced_code'])
    >>> print html
    <p>A paragraph before a fenced code block:</p>
    <pre><code>Fenced code block
    </code></pre>

Works with safe_mode also (we check this because we are using the HtmlStash):

    >>> print markdown.markdown(text, extensions=['fenced_code'], safe_mode='replace')
    <p>A paragraph before a fenced code block:</p>
    <pre><code>Fenced code block
    </code></pre>

Include tilde's in a code block and wrap with blank lines:

    >>> text = '''
    ... ~~~~~~~~
    ...
    ... ~~~~
    ... ~~~~~~~~'''
    >>> print markdown.markdown(text, extensions=['fenced_code'])
    <pre><code>
    ~~~~
    </code></pre>

Language tags:

    >>> text = '''
    ... ~~~~{.python}
    ... # Some python code
    ... ~~~~'''
    >>> print markdown.markdown(text, extensions=['fenced_code'])
    <pre><code class="python"># Some python code
    </code></pre>

Optionally backticks instead of tildes as per how github's code block markdown is identified:

    >>> text = '''
    ... `````
    ... # Arbitrary code
    ... ~~~~~ # these tildes will not close the block
    ... `````'''
    >>> print markdown.markdown(text, extensions=['fenced_code'])
    <pre><code># Arbitrary code
    ~~~~~ # these tildes will not close the block
    </code></pre>

If the codehighlite extension and Pygments are installed, lines can be highlighted:

    >>> text = '''
    ... ```hl_lines="1 3"
    ... line 1
    ... line 2
    ... line 3
    ... ```'''
    >>> print markdown.markdown(text, extensions=['codehilite', 'fenced_code'])
    <pre><code><span class="hilight">line 1</span>
    line 2
    <span class="hilight">line 3</span>
    </code></pre>

Copyright 2007-2008 [Waylan Limberg](http://achinghead.com/).

Project website: <http://packages.python.org/Markdown/extensions/fenced_code_blocks.html>
Contact: markdown@freewisdom.org

License: BSD (see ../docs/LICENSE for details)

Dependencies:
* [Python 2.4+](http://python.org)
* [Markdown 2.0+](http://packages.python.org/Markdown/)
* [Pygments (optional)](http://pygments.org)

"""

from __future__ import absolute_import
from __future__ import unicode_literals
from . import Extension
from ..preprocessors import Preprocessor
from .codehilite import CodeHilite, CodeHiliteExtension, parse_hl_lines
import re

import markdown


class FencedCodeExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        """Add FencedBlockPreprocessor to the Markdown instance."""
        md.registerExtension(self)

        md.preprocessors.add(
            "fenced_code_block", FencedBlockPreprocessor(md), ">normalize_whitespace"
        )


class FencedBlockPreprocessor(Preprocessor):
    FENCED_BLOCK_RE = re.compile(
        r"""
(?P<fence>^(?:~{3,}|`{3,}))[ ]*         # Opening ``` or ~~~
(\{?\.?(?P<lang>[a-zA-Z0-9_+-]*))?[ ]*  # Optional {, and lang
# Optional highlight lines, single- or double-quote-delimited
(hl_lines=(?P<quot>"|')(?P<hl_lines>.*?)(?P=quot))?[ ]*
}?[ ]*\n                                # Optional closing }
(?P<code>.*?)(?<=\n)
(?P=fence)[ ]*$""",
        re.MULTILINE | re.DOTALL | re.VERBOSE,
    )
    CODE_WRAP = "<pre><code%s>%s</code></pre>"
    LANG_TAG = ' class="%s"'

    def __init__(self, md):
        super(FencedBlockPreprocessor, self).__init__(md)

        self.checked_for_codehilite = False
        self.codehilite_conf = {}

    def run(self, lines):
        """Match and store Fenced Code Blocks in the HtmlStash."""

        # Check for code hilite extension
        if not self.checked_for_codehilite:
            for ext in self.markdown.registeredExtensions:
                if isinstance(ext, CodeHiliteExtension):
                    self.codehilite_conf = ext.config
                    break

            self.checked_for_codehilite = True

        text = "\n".join(lines)
        while 1:
            m = self.FENCED_BLOCK_RE.search(text)
            if m:
                lang = ""
                if m.group("lang"):
                    lang = self.LANG_TAG % m.group("lang")

                # If config is not empty, then the codehighlite extension
                # is enabled, so we call it to highlight the code
                if self.codehilite_conf:
                    highliter = CodeHilite(
                        m.group("code"),
                        linenums=self.codehilite_conf["linenums"][0],
                        guess_lang=self.codehilite_conf["guess_lang"][0],
                        css_class=self.codehilite_conf["css_class"][0],
                        style=self.codehilite_conf["pygments_style"][0],
                        lang=(m.group("lang") or None),
                        noclasses=self.codehilite_conf["noclasses"][0],
                        hl_lines=parse_hl_lines(m.group("hl_lines")),
                    )

                    code = highliter.hilite()
                else:
                    code = self.CODE_WRAP % (lang, self._escape(m.group("code")))

                placeholder = self.markdown.htmlStash.store(code)
                text = "%s\n%s\n%s" % (text[: m.start()], placeholder, text[m.end() :])
            else:
                break
        return text.split("\n")

    def _escape(self, txt):
        """basic html escaping"""
        txt = txt.replace("&", "&amp;")
        txt = txt.replace("<", "&lt;")
        txt = txt.replace(">", "&gt;")
        txt = txt.replace('"', "&quot;")
        return txt


def makeExtension(**kwargs):
    return FencedCodeExtension(**kwargs)
