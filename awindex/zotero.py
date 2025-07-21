import json
import logging
from diskcache import Cache
from pyzotero import zotero
from .models import PageFindRecord

# So we can see what's happening:
log = logging.getLogger(__name__)

# Set up caching of calls to web services:
cache = Cache(directory=".data_cache")
CACHE_FOR_SECONDS = 60*60*24 # Cache for a day by default

# Caching call to Zotero:
@cache.memoize(expire=CACHE_FOR_SECONDS)
def get_zotero_collection(library_id: str, library_type: str, api_key: str, collection_id:str = None):
    # Get the whole set of data from Zotero:
    zot = zotero.Zotero(library_id, library_type, api_key)
    items = zot.everything(zot.items())
    # Get all collections and sub-collections, starting at the supplied ID or ALL if None: 
    collections = zot.everything(zot.all_collections(collid=collection_id))
    # And return
    return items, collections

def get_full_collection(cols, c):
    name = c['data']['name']
    if c['data']['parentCollection']:
        p = cols[c['data']['parentCollection']]
        return f"{get_full_collection(cols, p)} > {name}"
    else:
        return name
        

def parse_zotero(library_id, library_type, api_key=None, collection_id:str = None, source=None, language="en"):
    # Get and cache the whole set of items and collections:
    items, collections = get_zotero_collection(library_id, library_type, api_key, collection_id=collection_id)

    # Can index collections by key, and then can add collections as section facets:
    cols = {}
    for c in collections:
        cols[c['key']] = c

    # Convert to common format:
    for item in items:
        # Set up as indexer record:
        d = item['data']
        log.debug(f"Processing: {json.dumps(item)}")
        # Skip items with no URL:
        if not 'url' in d:
            continue
        # Skip attachgments for now:
        if d['itemType'] == 'attachment':
            continue
        # Build a record:
        pf = PageFindRecord(
            url=d['url'],
            content=f"{d['title']} {d['abstractNote']}",
            language=language,
            meta={
                'title': d['title'],
                'type' : d['itemType']
            },
            filters={
                'type': [ d['itemType'] ]
            }
        )

        # Add the collection:
        sections = []
        if 'collections' in d:
            for c_k in d['collections']:
                # Skip entries that are outside the requestions collection scope:
                if not c_k in cols:
                    continue
                c = cols[c_k]
                sections.append(get_full_collection(cols, c))
            pf.filters['sections'] = sections
            if len(sections) == 1:
                pf.meta['section'] = sections[0]
            
        # Skip items in no collections if a specific collection was requested:
        if collection_id and len(sections) == 0:
            continue

        # Add the source
        if source:
            pf.filters['source'] = [ source ]
            pf.meta['source'] = source
        # And return it
        yield pf


# Entrypoint
if __name__ == "__main__":
    # Connect to the test group library:
    library_id = '2271741' 
    library_type = 'group'
    api_key = None # No key needed to read...
    for item in parse_zotero(library_id, library_type, api_key):
        print(item)

