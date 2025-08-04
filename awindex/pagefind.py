import json
import asyncio
import logging
from typing import List, Optional, Set, Dict, Tuple, Type, Union, Literal, Annotated
from pydantic import BaseModel
from pagefind.index import PagefindIndex, IndexConfig
from .models import Settings, IndexRecord

log = logging.getLogger(__name__)


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
            sort={
                'title': ir.title,
            }
        )
        # Optional fields etc.:
        if ir.abstract:
            pf.content += f" {ir.abstract}"
        if ir.full_text:
            pf.content += f" {ir.full_text}"
        if ir.creators and len(ir.creators) > 0:
            summary = ", ".join(ir.creators)
            pf.content += f" {summary}" # Ensures the values are searchable
            pf.meta['creators'] = summary
            pf.filters['creators'] = ir.creators
        if ir.keywords and len(ir.keywords) > 0:
            summary = ", ".join(ir.keywords)
            pf.content += f" {summary}"  
            pf.meta['keywords'] = summary
            pf.filters['keywords'] = ir.keywords
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
            pf.filters['year'] = [ str(ir.date.year) ]
            pf.meta['date'] = ir.date.isoformat()
            pf.sort['date'] = ir.date.isoformat()
        if ir.metadata:
            for k,v in ir.metadata.items():
                # If this looks like a JSON encoded array, try to load it as such and join it:
                if v.startswith("[\""):
                    v = ", ".join(json.loads(v))
                # Store the (resulting) value for search and for viewing:
                pf.content += f" {v}"  
                pf.meta[k] = v

        # Other items to consider including:
        #source_url: str
        #license: Optional[str] = None
        #weight: Optional[int] = None
        #links: Optional[Dict[str, str]] = None

        # Return the mapped object:
        return pf

async def async_generator(index_path, records: List[IndexRecord]):
    # Set up index config and generate:
    log.info("Generating PageFind index...")
    index_config = IndexConfig(
        root_selector="main", output_path=str(index_path), verbose=False
    )
    async with PagefindIndex(config=index_config) as index:
        # Add custom records:
        count = 0
        for ir in records:
            pf = PageFindRecord.from_index_record(ir)
            await index.add_custom_record(**(dict(pf)))
            count += 1
        # Report (don't call get_files as it returns the actual files and locks up the pipes):
        log.info(f"Indexed {count} records, now writing PageFind index files...")
    log.info("Indexing complete.")


# Take the records and convert them into a PageFind index.
def generate_pagefind_index(config: Settings, records: List[IndexRecord]):
    asyncio.run(async_generator(config, records))