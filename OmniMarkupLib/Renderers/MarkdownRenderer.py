from OmniMarkupLib.Renderers.libs.markdown.extensions.codehilite import (
    CodeHilite,
    CodeHiliteExtension,
)
import OmniMarkupLib.Renderers.libs.markdown.extensions.extra as extra
import OmniMarkupLib.Renderers.libs.markdown.extensions.meta as meta
import OmniMarkupLib.Renderers.libs.markdown.extensions.nl2br as nl2br
import OmniMarkupLib.Renderers.libs.markdown.extensions.smarty as smarty
import OmniMarkupLib.Renderers.libs.markdown.extensions.toc as toc
from .base_renderer import *
import re
import markdown


@renderer
class MarkdownRenderer(MarkupRenderer):
    FILENAME_PATTERN_RE = re.compile(r"\.(md|mmd|mkdn?|mdwn|mdown|markdown|litcoffee)$")
    YAML_FRONTMATTER_RE = re.compile(
        r"\A---\s*\n.*?\n?^---\s*$\n?", re.DOTALL | re.MULTILINE
    )
    MARKDOWN_SYNTAX_RE = re.compile(r"^text\.html\.markdown\S*")

    def load_settings(self, renderer_options, global_setting):
        super(MarkdownRenderer, self).load_settings(renderer_options, global_setting)
        if "extensions" in renderer_options:
            extensions = renderer_options["extensions"]
        else:
            # Fallback to the default GFM style
            extensions = ["tables", "strikeout", "fenced_code", "codehilite"]
        extensions = set(extensions)
        if global_setting.mathjax_enabled:
            if "mathjax" not in extensions:
                extensions.add("mathjax")
        if "smartypants" in extensions:
            extensions.remove("smartypants")
            extensions.add("smarty")
        if "codehilite" in extensions:
            extensions.remove("codehilite")
            extensions.add("codehilite(linenums=False,guess_lang=False)")
        self.extensions = list(extensions)

    @classmethod
    def is_enabled(cls, filename, syntax):
        """Looks for any syntax that begins with 'text.html.markdown'.

        Common options are:

        * text.html.markdown  # normal
        * text.html.markdown.gfm  # github-flavored
        * text.html.markdown.multimarkdown  # fletcherpenney.net/multimarkdown
        """
        if cls.MARKDOWN_SYNTAX_RE.match(syntax):
            return True
        return cls.FILENAME_PATTERN_RE.search(filename) is not None

    def render(self, text, **kwargs):
        text = self.YAML_FRONTMATTER_RE.sub("", text)
        # self.extensions.remove("markdown.extensions.mdx_mathjax")
        self.extensions = [
            # "mdx_subscript",
            CodeHiliteExtension([["linenums", False], ["guess_lang", False]]),
            "mdx_mathjax",
            # nl2br.makeExtension(),
            # smarty.makeExtension(),
            "mdx_strikeout",
            toc.makeExtension(),
            # "mdx_superscript",
            extra.makeExtension(),
        ]
        return markdown.markdown(
            text, output_format="html5", extensions=self.extensions
        )
