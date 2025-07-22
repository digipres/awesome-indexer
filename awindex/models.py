from typing import List, Optional, Set, Dict, Tuple, Type, Union
from pydantic import BaseModel
from datetime import datetime

# Data model for input configuration:
class Source(BaseModel):
    name: str
    type: str
    # URL sources:
    view_url: Optional[str] = None
    url: Optional[str] = None
    # Zotero-specific fields:
    library_id: Optional[Union[str, int]] = None
    library_type: Optional[str] = None
    collection_id: Optional[str] = None

class Settings(BaseModel):
    title: str
    output: Optional[str] = './output'
    sources: List[Source]


# Data model of normalised form of index record:
# (We generate these from the various sources, which can be output in various forms, including PageFindRecords)
class IndexRecord(BaseModel):
    title: str 
    url: str
    creators: Optional[List[str]] = None
    abstract: Optional[str] = None
    full_text: Optional[str] = None
    # Ideally from https://vocabularies.coar-repositories.org/documentation/resource_types/
    type: Optional[str] = None
    categories: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    license: Optional[str] = None
    date: Optional[datetime] = None
    weight: Optional[int] = None
    # Encode lists as JSON arrays:
    metadata: Optional[Dict[str, str]] = None
    # Some standard link types are declared in TBA...
    links: Optional[Dict[str, str]] = None
    language: str = "en"
    source: str
    source_url: str


# Data model for PageFind records:
# See https://pagefind.app/docs/py-api/#indexadd_custom_record
class PageFindRecord(BaseModel):
    url: str
    content: str
    language: str = "en"
    meta: Optional[Dict[str, str]] = None
    filters: Optional[Dict[str, List[str]]] = None
    sort: Optional[Dict[str, str]] = None

    @staticmethod
    def from_index_record(ir: IndexRecord):
        # Build a record:
        pf = PageFindRecord(
            url=ir.url,
            content=f"{ir.title}",
            meta={
                'title': ir.title,
            },
            filters={},
            sort={}
        )
        # Optional fields etc.:
        if ir.abstract:
            pf.content += f" {ir.abstract}"
        if ir.categories:
            pf.filters['categories'] = ir.categories
            pf.meta['categories'] = ", ".join(ir.categories)
        if ir.type:
            pf.filters['type'] = [ ir.type ]
            pf.meta['type'] = ir.type
        # Add the language:
        if ir.language:
            pf.language = ir.language
        # Add the source:
        if ir.source:
            pf.filters['source'] = [ ir.source ]
            pf.meta['source'] = ir.source
        # If there's a date, filter on the year:
        if ir.date:
            pf.filters['year'] = [ ir.date.year ]
            pf.meta['date'] = ir.date.isoformat()
            pf.sort['date'] = ir.date.isoformat()

        # Other items to consider including:
        #source_url: str
        #full_text: Optional[str] = None
        #keywords: Optional[List[str]] = None
        #license: Optional[str] = None
        #weight: Optional[int] = None
        #metadata: Optional[Dict[str, str]] = None
        #links: Optional[Dict[str, str]] = None

        # Return the mapped object:
        return pf

