import json
import logging
from pyzotero import zotero
from .models import IndexRecord, Zotero
from .utils import cache, CACHE_FOR_SECONDS


# So we can see what's happening:
log = logging.getLogger(__name__)

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
        

def parse_zotero(source: Zotero):
    # Get and cache the whole set of items and collections:
    items, collections = get_zotero_collection(source.library_id, source.library_type, source.api_key, collection_id=source.collection_id)

    # Can index collections by key, and then can add collections as section facets:
    cols = {}
    for c in collections:
        cols[c['key']] = c

    # Convert to common format:
    count = 0
    attachment_count = 0
    skipped_count = 0
    for item in items:
        # Set up as indexer record:
        d = item['data']
        log.debug(f"Processing: {json.dumps(item)}")
        # Skip attachments/notes/annotations for now:
        if d['itemType'] in ['attachment', 'note', 'annotation']:
            attachment_count += 1
            continue
        # Skip items with no URL:
        if not 'url' in d:
            log.warning(f"No URL for: {json.dumps(item)}")
            skipped_count += 1
            continue
        # Build a record:
        ir = IndexRecord(
            source=source.name,
            source_url=source.homepage,
            url=d['url'],
            title=d['title'],
            abstract=d['abstractNote'],
            type=d['itemType'],
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
            ir.categories = sections
            
        # Skip items in no collections if a specific collection was requested:
        if source.collection_id and len(sections) == 0:
            continue

        # And return it
        yield ir
        count += 1
    # Log stats
    log.info(f"Found {count} records.") 
    log.info(f"Ignored {attachment_count} attachments/notes/annotations and skipped {skipped_count} records with no URL.") 


# Entrypoint
if __name__ == "__main__":
    # Connect to the test group library:
    library_id = '2271741' 
    library_type = 'group'
    api_key = None # No key needed to read...
    for item in parse_zotero(library_id, library_type, api_key):
        print(item)

