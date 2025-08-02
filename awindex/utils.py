from diskcache import Cache

# Set up caching of calls to web services:
cache = Cache(directory=".data_cache")
CACHE_FOR_SECONDS = 60*60*24 # Cache for a day by default

def uncomma_name(name):
    if ',' in name:
        surname, fornames = name.split(",", maxsplit=1)
        return f"{fornames.strip()} {surname.strip()}"
    else:
        return name.strip()