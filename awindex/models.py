import json
from typing import List, Optional, Set, Dict, Tuple, Type, Union, Literal, Annotated
from pydantic import BaseModel, Field
from datetime import datetime

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

# Data model for input configuration, and storing results temporarily:
class Source(BaseModel):
    name: str
    homepage: str
    description: Optional[str] = None

# Awesome List Source:
class Awesome(Source):
    type: Literal['awesome-list']
    view_url: Optional[str] = None
    url: str = None

# Zotero-specific fields:
class Zotero(Source):
    type: Literal['zotero']
    library_id: Union[str, int]
    library_type: str
    collection_id: Optional[str] = None
    api_key: Optional[str] = None

# Zenodo
class Zenodo(Source):
    type: Literal['zenodo']
    community: str

# JSONL local file source
class Jsonl(Source):
    type: Literal['jsonl']
    file: str

# Config file spec:
class Settings(BaseModel):
    title: str
    homepage: Optional[str] = None
    description: Optional[str] = None
    output: Optional[str] = './index'
    sources: List[Annotated[Union[Awesome, Zenodo, Zotero, Jsonl], Field(discriminator='type')]]


# Class to hold the summary of a source along with the results:
class SourceResults(Source):
    records: Optional[List[IndexRecord]] = None
    warnings: Optional[List[str]] = None
    num_records: int = 0
    num_ignored: int = 0
    num_errors: int = 0