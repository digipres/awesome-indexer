import json
import logging
from diskcache import Cache
from pyzotero import zotero

# So we can see what's happening:
logging.basicConfig(level=logging.INFO)

# Set up caching of calls to web services:
cache = Cache(directory=".data_cache")
CACHE_FOR_SECONDS = 60*60*24 # Cache for a day by default

# Caching call to Zotero:
@cache.memoize(expire=CACHE_FOR_SECONDS)
def get_zotero_collection(library_id: str, library_type: str, api_key: str):
    # Get the whole set of data from Zotero:
    zot = zotero.Zotero(library_id, library_type, api_key)
    items = zot.everything(zot.items())
    collections = zot.everything(zot.all_collections())
    # And return
    return items, collections


# Entrypoint
if __name__ == "__main__":
    # Connect to the iPRES group library:
    library_id = '5564150' 
    library_type = 'group'
    api_key = None # No key needed to read...

    # Get and cache the whole set of items and collections:
    items, collections = get_zotero_collection(library_id, library_type, api_key)

    # Can index collections by key, and then can add collections as section facets:

    # Convert to JSON:
    for item in items:
        print(item)


