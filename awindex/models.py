from typing import List, Optional, Set, Dict
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

