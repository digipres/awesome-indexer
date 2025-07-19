import mistletoe
from mistletoe.markdown_renderer import MarkdownRenderer, BaseRenderer, block_token, span_token

from typing import List, Optional, Set, Dict
from pydantic import BaseModel
from datetime import datetime
import json
import re

# Pydantic data model for PageFind records:
# See https://pagefind.app/docs/py-api/#indexadd_custom_record
class IndexRecord(BaseModel):
    url: str
    content: str
    language: str = "en"
    meta: Optional[Dict[str, str]] = None
    filters: Optional[Dict[str, List[str]]] = None
    sort: Optional[Dict[str, str]] = None


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
        self.item = { 'meta': {}, 'filters': {} }
        if source:
            self.item['filters']['source'] = [ source ]
        self.keep_text = False
        self.in_item = False
    
    def render_heading(self, token: block_token.Heading) -> str:
        self.keep_text = True
        rendered = self.render_inner(token)
        self.headings.insert( token.level - 1, rendered.strip() )
        self.headings = self.headings[0:token.level]
        self.item['filters']['section'] = [ " > ".join(self.headings[1:]) ]
        self.keep_text = False
        return ""

    def render_list_item(self, token: block_token.ListItem) -> str:
        # This just skips sub-lists, but they are bad form anyway, I think.
        if self.in_item:
            return ""
        self.in_item = True
        self.keep_text = True
        self.item['url'] = None
        self.item['meta']['title']  = self.render_inner(token)
        self.keep_text = False
        self.in_item = False
        # FIXME drop items with empty or # URLs
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
        Strip any HTML comments, if keeping text. e.g. <!-- omit in toc -->
        """
        if not self.keep_text:
            return ""
        return self.re_comment.sub("", token.content)


with open('test/awesome-digital-preservation.md', 'r') as fin:
    with JsonlRenderer(source="Awesome Digital Preservation") as renderer:
        print(renderer.render(mistletoe.Document(fin)))




