import json
import datetime
import requests
import logging
from .models import IndexRecord, PageFindRecord, Zenodo
from .utils import uncomma_name, cache, CACHE_FOR_SECONDS

log = logging.getLogger(__name__)

@cache.memoize(expire=CACHE_FOR_SECONDS)
def get_zenodo_url(url):
    log.warning(f"Fetching {url}")
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("FAILED")
    return r.text

# https://zenodo.org/api/communities/digital-preservation/records?page=2&size=25&sort=newest
def get_zenodo_community(community):
    next_url = f"https://zenodo.org/api/communities/{community}/records"
    # Go through the pages...
    while next_url:
        results_text = get_zenodo_url(next_url)
        results = json.loads(results_text)
        for hit in results["hits"].get("hits", []):
            yield hit
        next_url = results['links'].get('next', None)

def parse_zenodo(config: Zenodo):
    for hit in get_zenodo_community(config.community):
        #print(hit)
        md = hit['metadata']
        #print(md['publication_date'])
        ir = IndexRecord(
            source=config.name,
            source_url=config.homepage,
            url=hit['doi_url'],
            title=md['title'],
            abstract=md.get('description', None),
            keywords=md.get('keywords', None),
            type=md['resource_type']['title'],
            creators=(uncomma_name(item['name']) for item in md['creators']),
        )
        # Attempt to parse date:
        pd = md['publication_date']
        try:
            if len(pd) == 10:
                ir.date = datetime.datetime.fromisoformat(pd)
            elif len(pd) == 7:
                ir.date = datetime.datetime.strptime(pd, "%Y-%m")
            else:
                ir.date = datetime.datetime.strptime(pd, "%Y")
        except ValueError as e:
            log.warning(f"Could not parse publication_date of {pd} from record '{md['title']}'")
            
        yield ir


