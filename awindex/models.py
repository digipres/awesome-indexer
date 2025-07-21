from typing import List, Optional, Set, Dict, Tuple, Type, Union
from pydantic import BaseModel
from datetime import datetime
import json
import re

# Pydantic data model for PageFind records:
# See https://pagefind.app/docs/py-api/#indexadd_custom_record
class PageFindRecord(BaseModel):
    url: str
    content: str
    language: str = "en"
    meta: Optional[Dict[str, str]] = None
    filters: Optional[Dict[str, List[str]]] = None
    sort: Optional[Dict[str, str]] = None


# Data model for input configuration:

class Source(BaseModel):
    name: str
    type: str
    url: Optional[str] = None
    library_id: Optional[Union[str, int]] = None
    library_type: Optional[str] = None
    collection_id: Optional[str] = None

class Settings(BaseModel):
    title: str
    sources: List[Source]


