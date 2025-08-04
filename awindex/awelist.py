import re
import requests
import json
import logging
import mistletoe
from mistletoe.markdown_renderer import MarkdownRenderer, BaseRenderer, block_token, span_token
from .models import IndexRecord, SourceResults, Awesome
from .utils import cache, CACHE_FOR_SECONDS

log = logging.getLogger(__name__)

class JsonlRenderer(BaseRenderer):
    def __init__(
        self,
        *extras,
        source: str = None,
        **kwargs
    ):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
            source (str): The name of the source to declare in each item
        """
        super().__init__(*extras, **kwargs)
        # Utilities:
        self.re_comment = re.compile("<!--.*-->")
        # Internal tracking state:
        self.headings = [] 
        self.item = { 'meta': {} }
        self.keep_text = False
        self.in_item = False
    
    def render_heading(self, token: block_token.Heading) -> str:
        self.keep_text = True
        rendered = self.render_inner(token)
        self.headings.insert( token.level - 1, rendered.strip() )
        self.headings = self.headings[0:token.level]
        self.item['sections'] = [ " > ".join(self.headings[1:]) ]
        self.keep_text = False
        return ""

    def render_list_item(self, token: block_token.ListItem) -> str:
        # This just skips sub-lists, but they are bad form anyway, I think.
        if self.in_item:
            return self.render_inner(token)
        self.in_item = True
        self.keep_text = True
        self.item['url'] = None
        self.item['title']  = self.render_inner(token)
        self.keep_text = False
        self.in_item = False
        return json.dumps(self.item)+"\n"

    def render_link(self, token: span_token.Link) -> str:
        if self.item.get('url', None) is None:
            self.item['url'] = token.target
        return self.render_inner(token)

    def render_auto_link(self, token: span_token.AutoLink) -> str:
        if not 'url' in self.item:
            self.item['url'] = token.target
        return self.render_inner(token)
    
    def render_raw_text(self, token) -> str:
        """
        If keeping text, strip any HTML comments, . e.g. <!-- omit in toc -->
        """
        if not self.keep_text:
            return ""
        return self.re_comment.sub("", token.content)

    # Without this, comment-only line break the parser.
    def render_line_break(self, token: span_token.LineBreak) -> str:
        if token.children:
            return self.render_inner(token)
        else:
            return ""

@cache.memoize(expire=CACHE_FOR_SECONDS)
def get_awesome_list(url):
    log.warning(f"Fetching {url}")
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("FAILED")
    return r.text

def parse_input(input, source: Awesome, result: SourceResults):
    with JsonlRenderer() as renderer:
        jsonl: str = renderer.render(mistletoe.Document(input))
        for json_item in jsonl.splitlines():
            item = json.loads(json_item)
            log.debug(f"Processing item {item}")
            if item['url'] and not item['url'].startswith('#'): 
                # Set up as indexer record:
                ir = IndexRecord(
                    source=source.name,
                    source_url=source.homepage,
                    title=item['title'],
                    url=item['url'],
                    categories=item['sections'],
                    metadata=item['meta'],
                )
                # And return it
                result.num_records += 1
                yield ir

def parse_awesome_list(source: Awesome, result: SourceResults):
    text = get_awesome_list(source.url)
    yield from parse_input(text, source, result)

# For testing:
if __name__ == "__main__":
    with open("test/awesome-web-archiving.md") as f:
        source = Awesome()
        source.name = "Test Source"
        source.homepage = "http://test.com"
        for pf in parse_input(f, source):
            print(pf)


